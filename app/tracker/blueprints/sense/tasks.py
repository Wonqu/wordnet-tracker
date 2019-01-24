import os
from datetime import timedelta

from celery.task import periodic_task
from celery.utils.log import get_task_logger

from lib.util_sqlalchemy import paginate
from tracker.app import create_app_celery
from tracker.blueprints.sense import models
from tracker.celery import celery

logger = get_task_logger(__name__)


@periodic_task(run_every=timedelta(seconds=int(os.environ['VIEW_COUNT_TASK_PERIOD'])))
def cache_tracker_sense_history():
    # tasks called by celery beat are unfortunatelly outside of app context, so it needs to be added manually
    with create_app_celery().app_context():
        paginated_synsets = models.TrackerSenseHistory.query.filter(
            models.TrackerSenseHistory.search_by_form_filter('', '', '', '', '', '')
        )
        cache_key = "luh-count-{}_{}_{}_{}_{}_{}".format('', '', '', '', '', '')
        paginate(paginated_synsets, 1, 50, total_cache_key=cache_key, update=True)


@periodic_task(run_every=timedelta(seconds=int(os.environ['VIEW_COUNT_TASK_PERIOD'])))
def cache_tracker_sense_relations_history():
    # tasks called by celery beat are unfortunatelly outside of app context, so it needs to be added manually
    with create_app_celery().app_context():
        paginated_synsets = models.TrackerSenseRelationsHistory.query.filter(
            models.TrackerSenseRelationsHistory.search_by_form_filter('', '', '', '', '')
        )
        cache_key = "lurh-count-{}_{}_{}_{}_{}".format('', '', '', '', '')
        paginate(paginated_synsets, 1, 50, total_cache_key=cache_key, update=True)
