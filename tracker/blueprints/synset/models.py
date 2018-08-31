from _operator import or_

from lib.util_sqlalchemy import AwareDateTime
from tracker.extensions import db


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

    sense_id = db.Column("LEX_ID",db.Integer)

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

    unitstr = db.Column(db.String(1024))

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
        search_chain = (Synset.definition.ilike(search_query),
                        Synset.comment.ilike(search_query),
                        Synset.owner.ilike(search_query),
                        Synset.status.ilike(search_query),
                        Synset.unitstr.ilike(search_query))

        return or_(*search_chain)
