import os

from celery import Celery
from celery.schedules import crontab

app = Celery(
    'lamba',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    include=['app.tasks'],
)

app.conf.update(
    result_expires=3600,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

app.conf.beat_schedule = {
    'execute-strategy-every-minute': {
        'task': 'app.tasks.execute_strategy_task',
        'schedule': crontab(minute='*/1'),
    },
}
