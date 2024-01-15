# Generated by Django 4.2.5 on 2023-10-08 14:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_user_phone_no_user_referral_user_registration_method"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="calendar",
            name="id_calender",
        ),
        migrations.AddField(
            model_name="calendar",
            name="id_calendar",
            field=models.CharField(null=True),
        ),
        migrations.CreateModel(
            name="CalendarList",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("id_list", models.CharField(null=True)),
                ("summary", models.CharField(blank=True, max_length=255, null=True)),
                ("detail", models.TextField(null=True)),
                ("background_color", models.CharField(blank=True, max_length=255, null=True)),
                ("foreground_color", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="list_calendar_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="calendar",
            name="calendar",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="users.calendarlist"),
        ),
    ]