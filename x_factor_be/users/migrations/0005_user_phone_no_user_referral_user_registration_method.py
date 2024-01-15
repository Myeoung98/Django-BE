# Generated by Django 4.2.5 on 2023-10-07 15:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_user_first_name_user_last_name_user_username_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="phone_no",
            field=models.CharField(null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="referral",
            field=models.CharField(null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="registration_method",
            field=models.CharField(default="google", null=True),
        ),
    ]