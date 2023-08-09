from celery import shared_task

@shared_task
def send_daily_notification():
    from .views import send_daily_notification_to_users
    send_daily_notification_to_users()