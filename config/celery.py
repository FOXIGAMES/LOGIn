from celery import Celery
from datetime import timedelta
from django.conf import settings


app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.timezone = 'UTC'
app.conf.beat_schedule = {
    'send-daily-notification': {
        'task': 'myzloo.views.send_daily_notification_to_users',
        'schedule': timedelta(minutes=5),
    },
}
