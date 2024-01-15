import requests


APP_AUTHEN_WORKCHAT = 'Basic YWRtaW46YWRtaW4='
URL_NOTIFICATION_WORKCHAT = 'http://172.27.230.25:4000/notification_mgmt/api/notify_user_text_msg/'


def send_notification_to_workchat(email, text):

    header = {
        'Authorization': APP_AUTHEN_WORKCHAT,
        'Content-Type': 'application/json'
    }
    body = {
        "to_email": f"{email}",
        "type": "facebook_workplace",
        "content": f"{text}"
    }
    try:
        response = requests.post(
            url=URL_NOTIFICATION_WORKCHAT,
            json=body,
            headers=header
        )
    except Exception as e:
        print(e)
