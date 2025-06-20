from celery import Celery
from celery.schedules import crontab

import db_worker

celery_app = Celery('tasks', broker=('redis://localhost:6379/0'))
celery_app.conf.update(
    timezone='Europe/Moscow'
)


@celery_app.task
def db_fill():
    db_worker.worker()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """запуск обновления базы каждые 12 часов. в полночь и 12 дня"""
    sender.add_periodic_task(crontab(minute=0, hour='*/12', day_of_week='*'), db_fill.s())
