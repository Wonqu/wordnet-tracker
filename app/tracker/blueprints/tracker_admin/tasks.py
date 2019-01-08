import os
from datetime import timedelta

from celery.task import periodic_task
from celery.utils.log import get_task_logger
from sqlalchemy import select

from tracker.app import create_app_celery
from tracker.blueprints.tracker_admin import models
from tracker.celery import celery
from tracker.extensions import db

logger = get_task_logger(__name__)


@celery.task
def run_admin_query(key):
    with create_app_celery().app_context():
        models.AdminQuery.results(key, update=True)


@periodic_task(run_every=timedelta(seconds=int(os.environ['ADMIN_QUERY_TASK_PERIOD'])))
def schedule_queries():
    # tasks called by celery beat are unfortunatelly outside of app context, so it needs to be added manually
    with create_app_celery().app_context():
        from flask import current_app
        engine = db.get_engine(current_app, models.AdminQuery.__bind_key__)
        connection = engine.connect()
        aqs = connection.execute(select([models.AdminQuery]).where(models.AdminQuery.enable_autorun == True))
        if aqs.returns_rows:
            aqs = [{key: value for (key, value) in o.items()} for o in aqs]
        for aq in aqs:
            run_admin_query.delay(aq['id'])
