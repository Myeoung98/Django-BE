# Generated by Django 4.2.5 on 2023-10-07 14:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_user_access_token_calendar_user_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="id_token_calendar",
            field=models.CharField(max_length=10000, null=True),
        ),
    ]
