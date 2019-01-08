from _operator import or_

from sqlalchemy import and_, text, func

from lib.util_sqlalchemy import AwareDateTime
from tracker.extensions import db, cache


class TrackerSynsetsHistory(db.Model):
    __tablename__ = 'view_tracker_synsets_history'

    id = db.Column(db.Integer, primary_key=True)

    datetime = db.Column(AwareDateTime())

    user = db.Column(db.String(255))

    operation = db.Column(db.String(255))

    synset_id = db.Column(db.Integer)

    synset_unitstr = db.Column(db.Text(''))

    sense_id = db.Column(db.Integer)

    lemma = db.Column(db.String(255))

    @classmethod
    def sort_by(cls, field, direction):
        """
        Validate the sort field and direction.

        :param field: Field name
        :type field: str
        :param direction: Direction
        :type direction: str
        :return: tuple
        """
        if field not in cls.__table__.columns:
            field = 'id'

        if direction not in ('asc', 'desc'):
            direction = 'desc'

        return field, direction

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if not query:
            return ''

        search_query = '%{0}%'.format(query)
        search_chain = (TrackerSynsetsHistory.id.ilike(search_query),
                        TrackerSynsetsHistory.datetime.ilike(search_query),
                        TrackerSynsetsHistory.user.ilike(search_query))

        return or_(*search_chain)

    @classmethod
    def search_by_form_filter(cls, date_from, date_to, synset_id, user):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        search_chain = list()

        if date_from is not '':
            search_chain.append(func.DATE(TrackerSynsetsHistory.datetime) >= date_from)
        if date_to is not '':
            search_chain.append(func.DATE(TrackerSynsetsHistory.datetime) <= date_to)
        if synset_id is not '':
            search_chain.append(TrackerSynsetsHistory.synset_id == synset_id)
        if user is not '':
            search_chain.append(TrackerSynsetsHistory.user == user)
        return and_(*search_chain)


class TrackerSynsetsRelationsHistory(db.Model):
    __tablename__ = 'view_tracker_synsets_relations_history'

    id = db.Column(db.Integer, primary_key=True)

    datetime = db.Column(AwareDateTime())

    user = db.Column(db.String(255))

    operation = db.Column(db.String(255))

    source_id = db.Column(db.Integer)

    source_unitstr = db.Column(db.Text(''))

    relation_id = db.Column(db.Integer)

    relation_name = db.Column(db.String(255))

    target_id = db.Column(db.Integer)

    target_unitstr = db.Column(db.Text(''))

    @classmethod
    def sort_by(cls, field, direction):
        """
        Validate the sort field and direction.

        :param field: Field name
        :type field: str
        :param direction: Direction
        :type direction: str
        :return: tuple
        """
        if field not in cls.__table__.columns:
            field = 'id'

        if direction not in ('asc', 'desc'):
            direction = 'desc'

        return field, direction

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if not query:
            return ''

        search_query = '%{0}%'.format(query)
        search_chain = (TrackerSynsetsRelationsHistory.id.ilike(search_query),
                        TrackerSynsetsRelationsHistory.datetime.ilike(search_query),
                        TrackerSynsetsRelationsHistory.user.ilike(search_query))

        return or_(*search_chain)

    @classmethod
    def search_by_form_filter(cls, date_from, date_to, synset_id, user, relation_type):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        search_chain = list()

        if date_from is not '':
            search_chain.append(func.DATE(TrackerSynsetsRelationsHistory.datetime) >= date_from)
        if date_to is not '':
            search_chain.append(func.DATE(TrackerSynsetsRelationsHistory.datetime) <= date_to)
        if synset_id is not '':
            search_chain.append(TrackerSynsetsRelationsHistory.source_id == synset_id)
        if user is not '':
            search_chain.append(TrackerSynsetsRelationsHistory.user == user)
        if relation_type is not '':
            search_chain.append(TrackerSynsetsRelationsHistory.relation_id == relation_type)
        return and_(*search_chain)


class Tracker(db.Model):
    __tablename__ = 'tracker'
    id = db.Column(db.Integer, primary_key=True)

    tid = db.Column(db.Integer)

    datetime = db.Column(AwareDateTime())

    table = db.Column(db.String(255))

    inserted = db.Column(db.Boolean())

    deleted = db.Column(db.Boolean())

    data_before_change = db.Column(db.Integer)

    user = db.Column(db.String(255))

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(Tracker, self).__init__(**kwargs)

    @classmethod
    def sort_by(cls, field, direction):
        """
        Validate the sort field and direction.

        :param field: Field name
        :type field: str
        :param direction: Direction
        :type direction: str
        :return: tuple
        """
        if field not in cls.__table__.columns:
            field = 'datetime'

        if direction not in ('asc', 'desc'):
            direction = 'desc'

        return field, direction

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if not query:
            return ''

        search_query = '%{0}%'.format(query)
        search_chain = (Tracker.datetime.ilike(search_query),
                        Tracker.user.ilike(search_query))

        return or_(*search_chain)


def get_user_name_list():
    user_names = cache.get('user-names')

    if user_names is None:
        user_names = []

        sql = text('select distinct user from tracker')
        result = db.engine.execute(sql)
        for row in result:
            user_names.append(row[0])
            cache.set('user-names', user_names, timeout=7200)

    return user_names


def get_user_emotion_list():
    user_names = cache.get('user-emotions-names')

    if user_names is None:
        user_names = []

        sql = text('select distinct owner from emotion')
        result = db.engine.execute(sql)
        for row in result:
            user_names.append(row[0])
            cache.set('user-emotions-names', user_names, timeout=7200)

    return user_names


def get_synset_relation_list():
    relations = cache.get('synset-relations')

    if relations is None:
        relations = []

        sql = text(
            'select distinct tsr.REL_ID, r.name  from tracker_synsetrelation tsr join relationtype r on r.ID=tsr.REL_ID')
        result = db.engine.execute(sql)
        for row in result:
            relations.append(row)
            cache.set('synset-relations', relations, timeout=7200)

    return relations


def find_synset_incoming_relations(id):
    sql = text(
        'SELECT rtype.name as relation_name, s.ID as id, s.unitsstr as unitstr \
         FROM synsetrelation rel LEFT JOIN relationtype rtype ON (rtype.ID=rel.REL_ID) \
         LEFT JOIN synset s ON (s.ID=rel.PARENT_ID) \
         WHERE rel.CHILD_ID = :id')
    return db.engine.execute(sql, {'id': id})


def find_synset_outgoing_relations(id):
    sql = text(
        'SELECT rtype.name as relation_name, s.ID as id, s.unitsstr as unitstr \
         FROM synsetrelation rel LEFT JOIN relationtype rtype ON (rtype.ID=rel.REL_ID) \
         LEFT JOIN synset s ON (s.ID=rel.CHILD_ID) \
         WHERE rel.PARENT_ID = :id')
    return db.engine.execute(sql, {'id': id})


def find_synset_senses(id):
    sql = text(
        'Select lu.id as id, concat(lu.lemma, " ", lu.variant) as lemma, lu.pos \
         from unitandsynset uas \
         left join lexicalunit lu ON (uas.LEX_ID = lu.id) \
         WHERE uas.SYN_ID = :id \
         ORDER BY uas.unitindex ASC'
    )
    return db.engine.execute(sql, {'id': id})


def find_synset_sense_history(id):
    sql = text('SELECT t.datetime, t.user, \
            case \
                when t.inserted = 1 and t.table ="unitandsynset" then "attached sense" \
                when t.deleted = 1 and t.table ="unitandsynset" then "detached sense" \
            end as operation, l.id as sense_id, concat(l.lemma," ",l.variant) as lemma \
            FROM tracker t \
            LEFT JOIN tracker_unitandsynset uas ON (uas.tid=t.tid AND t.table="unitandsynset") \
            LEFT JOIN lexicalunit l ON (uas.lex_id=l.id) \
            WHERE  uas.tid IS NOT NULL AND ( t.inserted = 1 OR t.deleted = 1 OR t.data_before_change IS NOT NULL) \
            And uas.SYN_ID = :id ORDER BY t.id DESC')
    return db.engine.execute(sql, {'id': id})


def find_synset_history(id):
    sql = text('SELECT t.datetime, t.user, \
            case \
	            when t.inserted = 1  then "created" \
	            when t.deleted = 1  then "removed" \
                when t.inserted = 0 and t.deleted = 0 then "modified" \
            end as operation, ts.definition, ts.comment, ts.isabstract, \
            ts.owner, ts.unitsstr FROM tracker t \
            LEFT JOIN tracker_synset ts ON (ts.tid=t.tid AND t.table="synset") \
            WHERE ts.tid IS NOT NULL AND ( t.inserted = 1 OR t.deleted = 1 OR t.data_before_change IS NOT NULL) \
            AND ts.ID = :id ORDER BY t.id DESC')
    return db.engine.execute(sql, {'id': id})

class SynsetTracker(db.Model):
    __tablename__ = 'tracker_synset'

    id = db.Column('ID', db.Integer, primary_key=True)

    tid = db.Column(db.Integer)

    split = db.Column(db.Integer)

    definition = db.Column(db.String(255))

    isabstract = db.Column(db.Boolean())

    status = db.Column(db.Integer)

    comment = db.Column(db.String(255))

    owner = db.Column(db.String(255))

    unitstr = db.Column(db.String(1024))

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(SynsetTracker, self).__init__(**kwargs)

    @classmethod
    def sort_by(cls, field, direction):
        """
        Validate the sort field and direction.

        :param field: Field name
        :type field: str
        :param direction: Direction
        :type direction: str
        :return: tuple
        """
        if field not in cls.__table__.columns:
            field = 'tid'

        if direction not in ('asc', 'desc'):
            direction = 'desc'

        return field, direction

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if not query:
            return ''

        search_query = '%{0}%'.format(query)
        search_chain = (SynsetTracker.definition.ilike(search_query),
                        SynsetTracker.comment.ilike(search_query),
                        SynsetTracker.owner.ilike(search_query),
                        SynsetTracker.unitstr.ilike(search_query))

        return or_(*search_chain)


class UnitAndSynsetTracker(db.Model):
    __tablename__ = 'tracker_unitandsynset'

    tid = db.Column('tid', db.Integer, primary_key=True)

    sense_id = db.Column("LEX_ID", db.Integer)

    synset_id = db.Column("SYN_ID", db.Integer)

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(UnitAndSynsetTracker, self).__init__(**kwargs)

    @classmethod
    def sort_by(cls, field, direction):
        """
        Validate the sort field and direction.

        :param field: Field name
        :type field: str
        :param direction: Direction
        :type direction: str
        :return: tuple
        """
        if field not in cls.__table__.columns:
            field = 'tid'

        if direction not in ('asc', 'desc'):
            direction = 'desc'

        return field, direction

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if not query:
            return ''

        search_query = '%{0}%'.format(query)
        search_chain = (UnitAndSynsetTracker.sense_id.ilike(search_query),
                        UnitAndSynsetTracker.synset_id.ilike(search_query))

        return or_(*search_chain)


class Synset(db.Model):
    __tablename__ = 'synset'

    id = db.Column('ID', db.Integer, primary_key=True)

    split = db.Column(db.Integer)

    definition = db.Column(db.String(255))

    isabstract = db.Column(db.Boolean())

    status = db.Column(db.Integer)

    comment = db.Column(db.String(255))

    owner = db.Column(db.String(255))

    unitsstr = db.Column(db.String(1024))

    error_comment = db.Column(db.String(255))

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(SynsetTracker, self).__init__(**kwargs)

    @classmethod
    def sort_by(cls, field, direction):
        """
        Validate the sort field and direction.

        :param field: Field name
        :type field: str
        :param direction: Direction
        :type direction: str
        :return: tuple
        """
        if field not in cls.__table__.columns:
            field = 'id'

        if direction not in ('asc', 'desc'):
            direction = 'desc'

        return field, direction

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if not query:
            return ''

        search_query = '%{0}%'.format(query)
        search_chain = (Synset.id == query,
                        Synset.unitsstr.ilike(search_query))

        return or_(*search_chain)
