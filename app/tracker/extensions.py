import os

from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.contrib import cache as __cache_module

from tracker.exceptions import ImproperlyConfigured

debug_toolbar = DebugToolbarExtension()
csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)

cache_supported_backends = {
    None: __cache_module.NullCache,
    'memcached': __cache_module.MemcachedCache,
    'redis': __cache_module.RedisCache
}

__cache_uri = os.environ.get('CACHE_SERVICE')

if __cache_uri:
    try:
        # example __cache_uri is 'redis:dev_redis_1:6379'
        [__cache_type, __url, __port] = __cache_uri.split(':')
    except ValueError as e:
        raise ImproperlyConfigured('CACHE_SERVICE is wrongly formatted. Use "redis:dev_redis_1:6379" as example.')
    if __cache_type == 'redis':
        cache = __cache_module.RedisCache(host=__url, port=__port, default_timeout=os.environ.get('CACHE_TIMEOUT'))
    elif __cache_type == 'memcached':
        cache = __cache_module.MemcachedCache(
            servers=["{url}:{port}".format(url=__url, port=__port)],
            default_timeout=os.environ.get('CACHE_TIMEOUT')
        )
    else:
        raise ImproperlyConfigured('Unknown cache service, only Memcached and Redis are supported at the moment.')
else:
    cache = __cache_module.NullCache



