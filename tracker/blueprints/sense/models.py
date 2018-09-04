from sqlalchemy import and_, text, or_

from lib.util_sqlalchemy import AwareDateTime
from tracker.extensions import db, cache


class Sense(db.Model):

    __tablename__ = 'lexicalunit'

    id = db.Column('ID', db.Integer, primary_key=True)

    lemma = db.Column(db.String(255))

    domain = db.Column(db.Integer)

    pos = db.Column(db.Integer)

    isabstract = db.Column(db.Boolean())

    status = db.Column(db.Integer)

    comment = db.Column(db.String(2048))

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
            cache.set('sense-relations', relations, timeout=10 * 60)

    return relations


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
            search_chain.append(TrackerSenseRelationsHistory.datetime >= date_from)
        if date_to is not '':
            search_chain.append(TrackerSenseRelationsHistory.datetime <= date_to)
        if sense_id is not '':
            search_chain.append(TrackerSenseRelationsHistory.source_id == sense_id)
        if user is not '':
            search_chain.append(TrackerSenseRelationsHistory.user == user)
        if relation_type is not '':
            search_chain.append(TrackerSenseRelationsHistory.relation_id == relation_type)
        return and_(*search_chain)
