from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models

from x_factor_be.users.managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for x-factor-be.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name"), blank=True, max_length=255)
    first_name = CharField(_("First Name"), blank=True, max_length=255)  # type: ignore
    last_name = CharField(_("Last Name"), blank=True, max_length=255)  # type: ignore
    email = EmailField(_("email address"), unique=True)
    username = CharField(_("User Name"), blank=True, max_length=255)  # type: ignore
    avatar = CharField(null=True, max_length=500, blank=True)  # type: ignore
    # TODO: Calendar
    id_token_calendar = models.CharField(null=True, max_length=10000)
    access_token_calendar = models.CharField(null=True)
    # TODO: ...
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    registration_method = models.CharField(null=True, default='google')
    phone_no = models.CharField(null=True)
    referral = models.CharField(null=True)
    # USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


class CalendarList(models.Model):
    # TODO: GOOGLE
    id_list = models.CharField(null=True)
    # TODO: DETAIL CALENDAR
    summary = models.CharField(max_length=255, null=True, blank=True)
    detail = models.TextField(null=True)
    background_color = models.CharField(max_length=255, null=True, blank=True)
    foreground_color = models.CharField(max_length=255, null=True, blank=True)
    # TODE: USER REMIND
    user = models.ForeignKey(User, null=True, related_name='list_calendar_user', on_delete=models.SET_NULL)
    # TODO: UPDATE time
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class Calendar(models.Model):

    class UnitChoice(models.TextChoices):
        DAY = 'day'
        HOUR = 'hour'
        MINUTE = 'minute'
        SECOND = 'second'

    # TODO: GOOGLE
    calendar = models.ForeignKey(CalendarList, null=True, on_delete=models.SET_NULL)
    id_calendar = models.CharField(null=True)
    # TODO: DETAIL CALENDAR
    summary = models.CharField(max_length=12000, null=True, blank=True)
    detail = models.TextField(null=True, max_length=12000)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    htmlLink = models.CharField(max_length=12000, null=True, blank=True)
    status = models.CharField(max_length=12000, null=True, blank=True)
    location = models.CharField(max_length=12000, null=True, blank=True)
    creator = models.CharField(max_length=12000, null=True, blank=True)
    iCalUID = models.CharField(max_length=12000, null=True, blank=True)
    # TODO: TIME REMIND
    time_reminder = models.BigIntegerField(null=True, blank=True)
    repeat_time = models.IntegerField(null=True, blank=True)
    unit = models.CharField(max_length=30, default=UnitChoice.HOUR, choices=UnitChoice.choices)
    # TODE: USER REMIND
    user = models.ForeignKey(User, null=True, related_name='reminder_user', on_delete=models.SET_NULL)
    # TODO: UPDATE time
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
