from datetime import timedelta

DEBUG = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
LOG_LEVEL = 'DEBUG'

SERVER_NAME = 'localhost:9000'

REMEMBER_COOKIE_DURATION = timedelta(minutes=30)
SECRET_KEY = '!$flhgsdf324NO%$#SOET!$!'

db_uri = 'mysql+pymysql://wordnet:password@localhost:3306/wordnet_work'
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_BINDS = {
    'users': 'mysql+pymysql://wordnet:root@localhost:3306/wordnet',
}

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# Cache
MEMCACHED_SERVERS = 'memcached:11211'