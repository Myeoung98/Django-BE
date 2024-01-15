# Generated by Django 4.2.5 on 2023-10-08 16:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_remove_calendar_id_calender_calendar_id_calendar_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="calendar",
            name="creator",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="calendar",
            name="htmlLink",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="calendar",
            name="iCalUID",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="calendar",
            name="location",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="calendar",
            name="status",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]