from datetime import timedelta

DEBUG = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
LOG_LEVEL = 'DEBUG'

SERVER_NAME = 'localhost:5000'

REMEMBER_COOKIE_DURATION = timedelta(minutes=30)
SECRET_KEY = '!$flhgsdf324NO%$#SOET!$!'


# SQLAlchemy.
db_uri = 'mysql+pymysql://wordnet:root@192.168.1.106:3306/wordnet_work'
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_BINDS = {
    'users':        'mysql+pymysql://wordnet:root@192.168.1.106:3306/wordnet',
}
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Cache
MEMCACHED_SERVERS = 'memcached:11211'