from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.contrib.cache import MemcachedCache

debug_toolbar = DebugToolbarExtension()
csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
cache = MemcachedCache(['memcached:11211'])



