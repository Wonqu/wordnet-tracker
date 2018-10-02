from sqlalchemy import and_, text, or_, func

from lib.util_sqlalchemy import AwareDateTime
from tracker.extensions import db, cache


class Sense(db.Model):

    __tablename__ = 'lexicalunit'

    id = db.Column('ID', db.Integer, primary_key=True)

    lemma = db.Column(db.String(255))

    domain = db.Column(db.Integer)

    pos = db.Column(db.Integer)

    status = db.Column(db.Integer)

    comment = db.Column(db.Text(''))

    owner = db.Column(db.String(255))

    variant = db.Column(db.Integer)

    error_comment = db.Column(db.String(255))

    verb_aspect = db.Column(db.Integer)

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(Sense, self).__init__(**kwargs)

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
        search_chain = (Sense.lemma.ilike(search_query),
                        Sense.pos.ilike(search_query),
                        Sense.domain.ilike(search_query),
                        Sense.variant.ilike(search_query),
                        Sense.comment.ilike(search_query),
                        Sense.owner.ilike(search_query),
                        Sense.status.ilike(search_query),
                        )

        return or_(*search_chain)


def get_sense_relation_list():
    relations = cache.get('sense-relations')

    if relations is None:
        relations = []

        sql = text('select distinct tsr.REL_ID, r.name  from tracker_lexicalrelation tsr join relationtype r on r.ID=tsr.REL_ID')
        result = db.engine.execute(sql)
        for row in result:
            relations.append(row)
            cache.set('sense-relations', relations, timeout=7200)

    return relations


def find_sense_history(id):
    sql = text('SELECT t.datetime, t.user, \
                case \
	                when t.inserted = 1  then "created" \
	                when t.deleted = 1  then "removed" \
                    when t.inserted = 0 and t.deleted = 0 then "modified" \
                end as operation, ts.lemma, ts.variant, ts.pos, ts.domain, \
                ts.comment, ts.status \
                FROM tracker t \
                LEFT JOIN tracker_lexicalunit ts ON (ts.tid=t.tid AND t.table="lexicalunit") \
                WHERE ts.tid IS NOT NULL AND ( t.inserted = 1 OR t.deleted = 1 OR t.data_before_change IS NOT NULL) \
                AND ts.ID = :id ORDER BY t.id DESC')
    return db.engine.execute(sql, {'id': id})


def find_sense_incoming_relations(id):
    sql = text(
        'SELECT rtype.name as relation_name, s.ID as id, concat(s.lemma," ", s.variant) \
         FROM lexicalrelation rel LEFT JOIN relationtype rtype ON (rtype.ID=rel.REL_ID) \
         LEFT JOIN lexicalunit s ON (s.ID=rel.PARENT_ID) \
         WHERE rel.CHILD_ID = :id')
    return db.engine.execute(sql, {'id': id})


def find_sense_outgoing_relations(id):
    sql = text(
        'SELECT rtype.name as relation_name, s.ID as id, concat(s.lemma," ", s.variant) \
         FROM lexicalrelation rel LEFT JOIN relationtype rtype ON (rtype.ID=rel.REL_ID) \
         LEFT JOIN lexicalunit s ON (s.ID=rel.CHILD_ID) \
         WHERE rel.PARENT_ID = :id')
    return db.engine.execute(sql, {'id': id})


class TrackerSenseRelationsHistory(db.Model):
    __tablename__ = 'view_tracker_sense_relations_history'

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
        search_chain = (TrackerSenseRelationsHistory.id.ilike(search_query),
                        TrackerSenseRelationsHistory.datetime.ilike(search_query),
                        TrackerSenseRelationsHistory.user.ilike(search_query))

        return or_(*search_chain)

    @classmethod
    def search_by_form_filter(cls, date_from, date_to, sense_id, user, relation_type):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        search_chain = list()

        if date_from is not '':
            search_chain.append(func.DATE(TrackerSenseRelationsHistory.datetime) >= date_from)
        if date_to is not '':
            search_chain.append(func.DATE(TrackerSenseRelationsHistory.datetime) <= date_to)
        if sense_id is not '':
            search_chain.append(or_(TrackerSenseRelationsHistory.source_id == sense_id))
        if user is not '':
            search_chain.append(TrackerSenseRelationsHistory.user == user)
        if relation_type is not '':
            search_chain.append(TrackerSenseRelationsHistory.relation_id == relation_type)
        return and_(*search_chain)


class TrackerSenseHistory(db.Model):

    __tablename__ = 'view_tracker_sense_history'

    id = db.Column(db.Integer, primary_key=True)

    datetime = db.Column(AwareDateTime())

    user = db.Column(db.String(255))

    operation = db.Column(db.String(255))

    key_id = db.Column('k_id', db.Integer)

    key_lemma = db.Column('k_lemma', db.String(255))

    key_pos = db.Column('key_pos', db.Integer)

    key_status = db.Column('key_status', db.Integer)

    u1_lemma = db.Column('tu1_lemma', db.String(255))

    u1_variant = db.Column('tu1_variant', db.Integer)

    u1_domain = db.Column('tu1_domain', db.Integer)

    u1_pos = db.Column('tu1_pos', db.Integer)

    u1_status = db.Column('tu1_status', db.Integer)

    u1_comment = db.Column('tu1_comment', db.String(255))

    u1_owner = db.Column('tu1_owner', db.String(255))

    u2_lemma = db.Column('tu2_lemma', db.String(255))

    u2_variant = db.Column('tu2_variant', db.Integer)

    u2_domain = db.Column('tu2_domain', db.Integer)

    u2_pos = db.Column('tu2_pos', db.Integer)

    u2_status = db.Column('tu2_status', db.Integer)

    u2_comment = db.Column('tu2_comment', db.String(255))

    u2_owner = db.Column('tu2_owner', db.String(255))

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
    def search_by_form_filter(cls, date_from, date_to, sense_id, user, pos, status):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        search_chain = list()

        if date_from is not '':
            search_chain.append(func.DATE(TrackerSenseHistory.datetime) >= date_from)
        if date_to is not '':
            search_chain.append(func.DATE(TrackerSenseHistory.datetime) <= date_to)
        if sense_id is not '':
            search_chain.append(TrackerSenseHistory.key_id == sense_id)
        if user is not '':
            search_chain.append(TrackerSenseHistory.user == user)
        if pos is not '':
            search_chain.append(TrackerSenseHistory.key_pos == pos)
        if status is not '':
            search_chain.append(TrackerSenseHistory.key_status == status)
        return and_(*search_chain)
