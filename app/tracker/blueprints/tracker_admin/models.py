import enum

from flask import current_app
from sqlalchemy import select
from sqlalchemy.orm import validates

from tracker.blueprints.synset.models import Tracker
from tracker.extensions import db, cache


class AdminQueryTypeEnum(enum.Enum):
    statistic = 0
    diagnostic = 1


class AdminQuery(db.Model):
    __bind_key__ = 'tracker'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    query_text = db.Column(db.Text())
    enable_autorun = db.Column(db.Boolean())
    type = db.Column('type', db.Enum(AdminQueryTypeEnum), default=AdminQueryTypeEnum.statistic)

    required_words = ('select', 'from')
    banned_words = (
        'update ', 'insert ', 'delete ', 'create ', 'start ', 'begin ', 'commit ', 'drop ', 'alter ', 'database',
        'show ', 'describe ', 'into ', 'flush ', 'add ', 'modify ', 'load ', 'truncate ', 'mysql',
        'grant ', 'use ', 'root', 'localhost', 'commit',
    )
    special_cases = [
        # don't let passwords leak ... probably needs more extensive protection
        lambda q: not ('user' in q and 'password' in q),
        lambda q: not ('user' in q and '*' in q),
        # protect against setting variable but let synset queries be valid
        # it's still not safe in many cases, but hey...
        lambda q: not ('set' in q and 'synset' not in q),
    ]
    cache_key_template = "ADMIN_QUERY_RESULT_{id}"

    @validates('query_text')
    def validate_query_text(self, key, query):
        q_lower = query.lower()
        if all([
            word in q_lower for word in self.required_words
        ]) and all([
            word not in q_lower for word in self.banned_words
        ]) and all([
            case(q_lower) for case in self.special_cases
        ]):
            return query
        else:
            raise ValueError('Query needs to use SELECT and do not modify database in any way.')

    @staticmethod
    def execute(query):
        try:
            AdminQuery().validate_query_text(None, query)
        except ValueError:
            return [], []
        else:
            engine = db.get_engine(current_app)
            connection = engine.connect()
            aqs = connection.execute(query)
            headings = aqs.keys()
            if aqs.returns_rows:
                rows = [{key: value for (key, value) in o.items()} for o in aqs]
                connection.close()
            else:
                rows = []
            return headings, rows

    @staticmethod
    def results(key, update=False):
        cache_key = AdminQuery.cache_key_template.format(**{"id": key})
        results = cache.get(cache_key)
        if results is None or update:
            engine = db.get_engine(current_app, AdminQuery.__bind_key__)
            connection = engine.connect()
            aqs = connection.execute(select([AdminQuery]).where(AdminQuery.id == key))
            if aqs.returns_rows:
                aqs = [{key: value for (key, value) in o.items()} for o in aqs]
                connection.close()
                if len(aqs):
                    query_text = f"{aqs[0]['query_text']};".replace('\r\n', ' ').replace('\n', ' ')
                    query_name = f"{aqs[0]['name']}"
                    headings, rows = AdminQuery.execute(query_text)
                    results = headings, rows, query_name
                    cache.set(cache_key, results, timeout=current_app.config['ADMIN_QUERY_CACHE_TIMEOUT'])
                else:
                    results = [], [], "unknown"
            else:
                results = [], [], "unknown"
        return results
