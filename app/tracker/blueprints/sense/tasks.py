from celery.utils.log import get_task_logger

from tracker.celery import celery

logger = get_task_logger(__name__)

