from datetime import datetime
import requests
from django.contrib.auth import get_user_model
from django.conf import settings
from config import celery_app
from x_factor_be.utils.notion_work_chat import send_notification_to_workchat

User = get_user_model()


@celery_app.task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


@celery_app.task(name='calendar_send_task')
def calendar_send_task(access_token: str = None):
    response = requests.get(
        settings.API_GOOGLE_LIST_CALENDAR,
        params={'access_token': access_token}
    )


@celery_app.task(name='sync_calendar_users')
def sync_calendar_users(access_token: str = None):
    response = requests.get(
        settings.API_GOOGLE_LIST_CALENDAR,
        params={'access_token': access_token}
    )
    if response.status_code != 200:
        return "Error sync calendar by access token"

    return User.objects.count()


@celery_app.task(name='send_notion_calendar')
def send_notion_calendar(
    **kwargs
):
    email = kwargs.get('email', None)
    message = f"{kwargs.get('message', '')}" if kwargs.get('message') else ""
    htmlLink = f"\n Link Google Calendar: {kwargs.get('htmlLink', '')}" if kwargs.get('htmlLink') else ""
    location = f"\n Link Meet: {kwargs.get('location', '')}" if kwargs.get('location') else ""
    msg = str(message + location + htmlLink)
    send_notification_to_workchat(email, msg)
    print(" **************************** Inprogress **************************** ")
