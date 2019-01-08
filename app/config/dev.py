import os

from datetime import timedelta

# FLASK
DEBUG = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
LOG_LEVEL = 'DEBUG'

SERVER_NAME = 'localhost:9000'

REMEMBER_COOKIE_DURATION = timedelta(minutes=30)
SECRET_KEY = '!$flhgsdf324NO%$#SOET!$!'

# SQL ALCHEMY
mysql_uri_template = 'mysql+pymysql://{user}:{password}@{host}:3306/{db_name}'
SQLALCHEMY_DATABASE_URI = mysql_uri_template.format(**{
    'user': 'root',
    'password': os.environ['MYSQL_WORDNET_ROOT_PASSWORD'],
    'host': os.environ['MYSQL_WORDNET_HOST'],
    'port': os.environ['MYSQL_WORDNET_PORT'],
    'db_name': os.environ['MYSQL_WORDNET_DATABASE']
})

SQLALCHEMY_BINDS = {
    'users': mysql_uri_template.format(**{
        'user': 'root',
        'password': os.environ['MYSQL_USERS_ROOT_PASSWORD'],
        'host': os.environ['MYSQL_USERS_HOST'],
        'port': os.environ['MYSQL_USERS_PORT'],
        'db_name': os.environ['MYSQL_USERS_DATABASE']
    }),
    'tracker': mysql_uri_template.format(**{
        'user': 'root',
        'password': os.environ['MYSQL_TRACKER_ROOT_PASSWORD'],
        'host': os.environ['MYSQL_TRACKER_HOST'],
        'port': os.environ['MYSQL_TRACKER_PORT'],
        'db_name': os.environ['MYSQL_TRACKER_DATABASE'],
    })
}

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# CELERY
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')

ADMIN_QUERY_TASK_PERIOD = os.environ.get("ADMIN_QUERY_TASK_PERIOD")
ADMIN_QUERY_TASK_EXPIRE = os.environ.get("ADMIN_QUERY_TASK_EXPIRE")
ADMIN_QUERY_CACHE_TIMEOUT = os.environ.get("ADMIN_QUERY_CACHE_TIMEOUT", 6*3600)

CELERYBEAT_MAX_LOOP_INTERVAL = os.environ.get("CELERYBEAT_MAX_LOOP_INTERVAL", 300)  # 300 is library default
