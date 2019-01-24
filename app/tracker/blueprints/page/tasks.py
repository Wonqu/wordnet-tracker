import time

from datetime import timedelta

from celery.task import periodic_task
from celery.utils.log import get_task_logger

from tracker.app import create_app_celery
from tracker.blueprints.page.models import user_activity_cached
from tracker.celery import celery

logger = get_task_logger(__name__)


@periodic_task(run_every=timedelta(seconds=1800))
def cache_user_activity_now():
    # tasks called by celery beat are unfortunatelly outside of app context, so it needs to be added manually
    with create_app_celery().app_context():
        today = time.strftime("%Y-%m-%d", time.gmtime())
        user_activity_cached(today, '', update=True)


@periodic_task(run_every=timedelta(seconds=6*3600))
def cache_user_activity_yesterday():
    # tasks called by celery beat are unfortunatelly outside of app context, so it needs to be added manually
    with create_app_celery().app_context():
        today = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 24*3600))
        user_activity_cached(today, '', update=True, timeout=12*3600)
