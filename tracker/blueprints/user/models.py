import base64
import hashlib
from collections import OrderedDict
from hashlib import md5

from flask import current_app
from sqlalchemy import or_
from flask_login import UserMixin

from itsdangerous import URLSafeTimedSerializer, \
    TimedJSONWebSignatureSerializer

from tracker.extensions import db


class User(UserMixin, db.Model):
    ROLE = OrderedDict([
        ('USER', 'User'),
        ('ANONYMOUS', 'Anonymous'),
        ('ADMIN', 'Administrator')
    ])
    __bind_key__ = 'users'
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # Authentication.
    role = db.Column(db.Enum(*ROLE, name='role', native_enum=False),
                     index=True, nullable=False, server_default='USER')

    first_name = db.Column('firstname', db.String(255), unique=False, index=True)

    last_name = db.Column('lastname', db.String(255), unique=False, index=True)

    email = db.Column(db.String(255), unique=True, index=True, nullable=False,
                      server_default='')

    password = db.Column(db.String(128), nullable=False, server_default='')

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(User, self).__init__(**kwargs)

        self.password = User.encrypt_password(kwargs.get('password', ''))

    @classmethod
    def find_by_email(cls, email):
        """
        Find a user by their e-mail or username.

        :param email: Email
        :type email: str
        :return: User instance
        """
        return User.query.filter(User.email == email).first()

    @classmethod
    def encrypt_password(cls, plaintext_password):
        """
        Hash a plaintext string using SHA-256 with base64 encoding.

        :param plaintext_password: Password in plain text
        :type plaintext_password: str
        :return: str
        """
        if plaintext_password:
            hash_object = hashlib.sha256(plaintext_password.encode())
            hex_dig = hash_object.digest()
            return base64.b64encode(hex_dig).decode()

        return None

    @classmethod
    def deserialize_token(cls, token):
        """
        Obtain a user from de-serializing a signed token.

        :param token: Signed token.
        :type token: str
        :return: User instance or None
        """
        private_key = TimedJSONWebSignatureSerializer(
            current_app.config['SECRET_KEY'])
        try:
            decoded_payload = private_key.loads(token)

            return User.find_by_identity(decoded_payload.get('user_email'))
        except Exception:
            return None

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
        search_chain = (User.email.ilike(search_query),
                        User.first_name.ilike(search_query),
                        User.last_name.ilike(search_query),
                        User.id.ilike(search_query),
                        User.role.ilike(search_query))

        return or_(*search_chain)

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
            direction = 'asc'

        return field, direction

    def fullname(self):
        """
        Get user fullname
        :return: str
        """
        return self.first_name + " " + self.last_name

    def is_active(self):
        """
        Return whether or not the user account is active, this satisfies
        Flask-Login by overwriting the default value.

        :return: bool
        """
        return True

    def get_auth_token(self):
        """
        Return the user's auth token. Use their password as part of the token
        because if the user changes their password we will want to invalidate
        all of their logins across devices. It is completely fine to use
        md5 here as nothing leaks.

        This satisfies Flask-Login by providing a means to create a token.

        :return: str
        """
        private_key = current_app.config['SECRET_KEY']

        serializer = URLSafeTimedSerializer(private_key)
        data = [str(self.id), md5(self.password.encode('utf-8')).hexdigest()]

        return serializer.dumps(data)

    def authenticated(self, with_password=True, password=''):
        """
        Ensure a user is authenticated, and optionally check their password.

        :param with_password: Optionally check their password
        :type with_password: bool
        :param password: Optionally verify this as their password
        :type password: str
        :return: bool
        """

        if with_password:
            return self.password == self.encrypt_password(password)

        return True

    def serialize_token(self, expiration=3600):
        """
        Sign and create a token that can be used for things such as resetting
        a password or other tasks that involve a one off token.

        :param expiration: Seconds until it expires, defaults to 1 hour
        :type expiration: int
        :return: JSON
        """
        private_key = current_app.config['SECRET_KEY']

        serializer = TimedJSONWebSignatureSerializer(private_key, expiration)
        return serializer.dumps({'user_email': self.email}).decode('utf-8')
