import json
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from urllib.parse import urlencode
from rest_framework import serializers, permissions, viewsets
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import redirect
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from x_factor_be.users.views import PublicApiMixin
from x_factor_be.utils.oauth_google import google_get_access_token, google_get_user_info
from .serializers import UserSerializer
from typing import Dict, Any
import requests
import pytz
from x_factor_be.users.models import Calendar, CalendarList
from x_factor_be.users.api.serializers import ListCalendarSerializer, DetailsCalendarSerializer, CalendarDetails
from datetime import datetime, timedelta
from x_factor_be.users.tasks import calendar_send_task, send_notion_calendar
from django_celery_beat.models import ClockedSchedule, PeriodicTask
import uuid


User = get_user_model()


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


def generate_tokens_for_user(user):
    """
    Generate access and refresh tokens for the given user
    """
    serializer = TokenObtainPairSerializer()
    token_data = serializer.get_token(user)
    access_token = token_data.access_token
    refresh_token = token_data
    return access_token, refresh_token


class GoogleLoginApi(PublicApiMixin, APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get('code')
        error = validated_data.get('error')

        # login_url = f'{settings.BASE_FRONTEND_URL}/login'
        login_url = settings.LOGIN_REDIRECT_URL

        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        # redirect_uri = f'{settings.BASE_FRONTEND_URL}/google/'
        redirect_uri = settings.LOGIN_REDIRECT_URL
        result_token = google_get_access_token(
            code=code,
            redirect_uri=redirect_uri
        )
        print(result_token)
        print(" $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ ")
        user_data = google_get_user_info(access_token=result_token.get('access_token'))
        print(user_data, " ******************************** ------------------- ")
        try:
            user = User.objects.filter(email=user_data['email']).first()
            if user:
                user.access_token_calendar = result_token.get('access_token')
                user.id_token_calendar = result_token.get('id_token')
                user.avatar = user_data.get("picture")
                user.save()
                access_token, refresh_token = generate_tokens_for_user(user)
                response_data = {
                    'user': UserSerializer(user).data,
                    'access_token': str(access_token),
                    'refresh_token': str(refresh_token)
                }
                return Response(response_data)
            else:
                print(" ################################# ", user_data)
                username = user_data['email'].split('@')[0]
                first_name = user_data.get('given_name', '')
                last_name = user_data.get('family_name', '')

                user = User.objects.create(
                    username=username,
                    email=user_data['email'],
                    avatar=user_data['picture'],
                    first_name=first_name,
                    last_name=last_name,
                    registration_method='google',
                    access_token_calendar=result_token["access_token"],
                    id_token_calendar=result_token["id_token"],
                    phone_no=None,
                    referral=None,
                    password="eamil"
                )

                access_token, refresh_token = generate_tokens_for_user(user)
                response_data = {
                    'user': UserSerializer(user).data,
                    'access_token': str(access_token),
                    'refresh_token': str(refresh_token)
                }
                return Response(response_data)
        except Exception as e:
            return Response(f"Error generating tokens {e}")


class GetUrlAuth(PublicApiMixin, APIView):
    def get(self, request, *args):
        prefix_url = "https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?response_type=code"
        client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        scope = "profile%20email%20https://www.googleapis.com/auth/calendar"
        redirect_url = settings.LOGIN_REDIRECT_URL
        url = f"{prefix_url}&client_id={client_id}&scope={scope}&redirect_uri={redirect_url}&service=lso&o2v=2&theme=glif&flowName=GeneralOAuthFlow"
        return Response(status=status.HTTP_200_OK, data={"url": url})


class CalendarViewset(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=False, methods=['POST'], url_path="list")
    def get_list_calendar(self, request, *args, **kwargs):
        user = request.user
        current_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        iso8601_timestamp = current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        response = requests.get(
            settings.API_GOOGLE_LIST_CALENDAR,
            params={'access_token': user.access_token_calendar, "timeMin": iso8601_timestamp}
        )
        if response.status_code == 200:
            data_res = response.json()
            for data in data_res['items']:
                calendar_list = CalendarList.objects.filter(user=user, id_list=data['id']).first()
                if calendar_list:
                    calendar_list.summary = data.get('summary')
                    calendar_list.detail = data.get('description')
                    calendar_list.background_color = data.get('backgroundColor')
                    calendar_list.foreground_color = data.get('foregroundColor')
                    calendar_list.save()
                else:
                    calendar_list = CalendarList(
                        user=user,
                        summary=data.get('summary'),
                        detail=data.get('description'),
                        background_color=data.get('backgroundColor'),
                        foreground_color=data.get('foregroundColor'),
                        id_list=data.get('id')
                    )
                    calendar_list.save()
            # calendar_send_task.delay(user.access_token_calendar)
            return Response(status=status.HTTP_200_OK, data={"data": response.json()})
        else:
            cals = {
                "items": []
            }
            calendar_list = CalendarList.objects.filter(user=user)
            if calendar_list:
                for calendar in calendar_list:
                    data_calendar = {
                        "id": calendar.id_list,
                        "summary": calendar.summary,
                        "description": calendar.detail,
                        "backgroundColor": calendar.background_color,
                        "foregroundColor": calendar.foreground_color
                    }
                    cals['items'].append(data_calendar)
        return Response(status=status.HTTP_200_OK, data={"data": cals})

    @action(detail=False, methods=['POST'], url_path="sync-calendar")
    def sync_calendar(self, request, *args, **kwargs):
        user = request.user
        response = requests.get(
            settings.API_GOOGLE_LIST_CALENDAR,
            params={'access_token': user.access_token_calendar}
        )
        return Response(status=status.HTTP_200_OK, data={"data": response.json()})

    @action(detail=False, methods=['POST'], url_path="details")
    def get_details_calendar(self, request, *args, **kwargs):
        user = request.user
        sz = DetailsCalendarSerializer(data=request.data)
        sz.is_valid(raise_exception=True)
        calendar_id = sz.data['calendar_id']
        cals_list = CalendarList.objects.filter(user=user, id_list=calendar_id).first()
        if not cals_list:
            return Response(status=status.HTTP_200_OK, data={"data": {}})
        current_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        iso8601_timestamp = current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        response = requests.get(
            settings.API_GOOGLE_GET_DETAIL_CALENDAR.format(calendarId=calendar_id),
            params={
                'access_token': user.access_token_calendar,
                "timeMin": iso8601_timestamp
            }
        )
        if response.status_code == 200:
            for calendar in response.json()['items']:
                start_time = calendar.get('start').get('dateTime', None)
                end_time = calendar.get('end').get('dateTime', None)
                date_format = '%Y-%m-%dT%H:%M:%S%z'
                calendar, is_created = Calendar.objects.update_or_create(
                    calendar=cals_list,
                    user=user,
                    id_calendar=calendar["id"],
                    defaults={
                        "summary": calendar.get("summary"),
                        "detail": calendar.get("description"),
                        "htmlLink": calendar.get("htmlLink"),
                        "status": calendar.get("status"),
                        "location": calendar.get("location"),
                        "creator": calendar.get("creator"),
                        "iCalUID": calendar.get("iCalUID"),
                        "start_time": datetime.strptime(start_time, date_format) if start_time else datetime.utcnow(),
                        "end_time": datetime.strptime(end_time, date_format) if end_time else datetime.utcnow(),
                    },
                )
                # if is_created:
                if datetime.utcnow().timestamp() <= calendar.start_time.timestamp() <= (current_time + timedelta(days=1)).timestamp():
                    time_task = calendar.start_time - timedelta(minutes=5)
                    schedule, _ = ClockedSchedule.objects.get_or_create(
                        clocked_time=time_task
                    )

                    PeriodicTask.objects.get_or_create(
                        clocked=schedule,                  # we created this above.
                        # simply describes this periodic task.
                        name=f'Send notion calendar for {uuid.uuid4()}',
                        task='send_notion_calendar',  # name of task.
                        kwargs=json.dumps({
                            "email": user.email,
                            "message": calendar.summary if calendar.summary else "",
                            "location": calendar.location if calendar.location else "",
                            "htmlLink": calendar.htmlLink if calendar.htmlLink else ""
                        }),
                        enabled=True,
                        one_off=True,
                    )
        cals_details = Calendar.objects.filter(user=user, calendar=cals_list)
        if not cals_details:
            return Response(status=status.HTTP_200_OK, data={"data": sz.data})
        sz = CalendarDetails(cals_details, many=True)
        return Response(status=status.HTTP_200_OK, data={"data": sz.data})
