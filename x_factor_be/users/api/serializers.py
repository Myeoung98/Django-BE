from django.contrib.auth import get_user_model
from rest_framework import serializers

from x_factor_be.users.models import User as UserType, CalendarList, Calendar


User = get_user_model()


# class UserSerializer(serializers.ModelSerializer[UserType]):
#     class Meta:
#         model = User
#         fields = ["name", "url"]

#         extra_kwargs = {
#             "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
#         }

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'avatar']


class ListCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarList
        fields = "__all__"


class DetailsCalendarSerializer(serializers.Serializer):
    calendar_id = serializers.CharField(required=True)


class CalendarDetails(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = "__all__"
