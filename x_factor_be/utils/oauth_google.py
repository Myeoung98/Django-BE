import requests
from typing import Dict, Any
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://accounts.google.com/o/oauth2/token"
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'


def generate_tokens_for_user(user):
    """
    Generate access and refresh tokens for the given user
    """
    serializer = TokenObtainPairSerializer()
    token_data = serializer.get_token(user)
    access_token = token_data.access_token
    refresh_token = token_data
    return access_token, refresh_token


def google_get_access_token(code: str, redirect_uri: str) -> str:
    payload = f'grant_type=authorization_code&code={code}&client_secret=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&client_id=1043814527362-klum246ongvvjbkbiq56dq91lfq23fag.apps.googleusercontent.com&redirect_uri={redirect_uri}'
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = "scope=email%20https://www.googleapis.com/auth/calendar&access_type=offline"
    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=payload, headers=headers, params=params)
    if response.status_code != 200:
        raise ValidationError('Failed to obtain access token from Google.')
    return response.json()


def google_get_user_info(access_token:  str) -> Dict[str, Any]:
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )
    if not response.status_code == 200:
        raise ValidationError('Failed to obtain user info from Google.')

    return response.json()
