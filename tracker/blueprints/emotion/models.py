from sqlalchemy import and_, or_

from lib.util_sqlalchemy import AwareDateTime
from tracker.extensions import db


class Emotion(db.Model):
    __tablename__ = 'emotion'

    id = db.Column(db.Integer, primary_key=True)

    sense_id = db.Column('lexicalunit_id', db.Integer)

    emotions = db.Column(db.String(255))

    valuations = db.Column(db.String(255))

    markedness = db.Column(db.String(255))

    status = db.Column('unitStatus', db.Integer)

    example1 = db.Column(db.String(255))

    example2 = db.Column(db.String(255))

    owner = db.Column(db.String(255))

    creation_date = db.Column(AwareDateTime())

    super_annotation = db.Column('super_anotation', db.Integer)


class EmotionDisagreement(db.Model):
    __tablename__ = 'view_emotion_disagreement'

    sense_id = db.Column(db.Integer, primary_key=True)

    lemma = db.Column(db.String(255))

    status = db.Column(db.Integer)

    owner0 = db.Column(db.String(255))

    owner1 = db.Column(db.String(255))

    markedness0 = db.Column(db.String(10))

    markedness1 = db.Column(db.String(10))

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
            field = 'sense_id'

        if direction not in ('asc', 'desc'):
            direction = 'desc'

        return field, direction

    @classmethod
    def search_by_form_filter(cls, sense_id, user):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        search_chain = list()

        if sense_id is not '':
            search_chain.append(EmotionDisagreement.sense_id == sense_id)
        if user is not '':
            search_chain.append(or_(EmotionDisagreement.owner0 == user, EmotionDisagreement.owner1 == user))

        return and_(*search_chain)
