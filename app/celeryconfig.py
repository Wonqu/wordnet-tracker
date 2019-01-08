import os

from tracker.app import blueprints_to_import

CELERY_IMPORTS = (
    "tracker.blueprints.{}.tasks".format(blueprint) for blueprint in blueprints_to_import
)

redbeat_redis_url = os.environ['CELERY_BROKER_URL']
redbeat_lock_timeout = int(os.environ['ADMIN_QUERY_TASK_PERIOD']) + 10
