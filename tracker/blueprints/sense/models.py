from _operator import or_

from tracker.extensions import db


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
