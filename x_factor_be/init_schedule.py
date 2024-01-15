# -*- coding: utf-8 -*-
import json
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django_celery_beat.models import ClockedSchedule, PeriodicTask
from x_factor_be.users.models import Calendar
import uuid


def initialize_schedule_send_notion_calendar():
    current_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    end = current_time + timedelta(days=1)
    print("initialize_schedule_send_notion_calendar ******************************** ", " ^^^^^^^^^^^^^^^^^ ")
    list_calendar = Calendar.objects.filter(start_time__range=[current_time, end])
    for calendar in list_calendar:
        time_task = calendar.start_time - timedelta(minutes=5)
        schedule, _ = ClockedSchedule.objects.get_or_create(
            clocked_time=time_task
        )

        PeriodicTask.objects.create(
            clocked=schedule,                  # we created this above.
            # simply describes this periodic task.
            name=f'initialize_schedule_send_notion_calendar {uuid.uuid4()}',
            task='send_notion_calendar',  # name of task.
            kwargs=json.dumps({
                "email": calendar.user.email,
                "message": calendar.summary if calendar.summary else "",
                "location": calendar.location if calendar.location else "",
                "htmlLink": calendar.htmlLink if calendar.htmlLink else ""
            }),
            enabled=True,
            one_off=True,
        )
