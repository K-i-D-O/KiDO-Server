import firebase_admin
from firebase_admin import messaging
from django.contrib.auth.models import User
from .models import HelperProfile
from math import radians, sin, cos, sqrt, atan2

helper_url = 'https://ki-do.kr/help_req/settings_helper_main'
requester_url = 'https://ki-do.kr/help_req/req_success'

def calculate_distance(lat1, lon1, lat2, lon2):
    # 지구 반지름 (km)
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def send_push_notification(device_token, title, body, data):
    """
    FCM을 통해 푸시 알림을 보내는 함수
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=device_token,
        data={key: str(value) for key, value in data.items()}  # 모든 값을 문자열로 변환
    )

    try:
        print(f"Attempting to send message to token: {device_token}")
        print(f"Message: {message}")
        response = messaging.send(message)
        print(f"Message sent successfully: {response}")
        return {'success': True, 'response': response}
    except firebase_admin.exceptions.FirebaseError as e:
        print(f"FCM API call error: {e}")
        return {'success': False, 'error': str(e)}
    except Exception as e:
        print(f"General error: {e}")
        return {'success': False, 'error': str(e)}


def send_push_notification_to_helpers(help_request):
    print("send_push_notification_to_helpers called")
    # helpers = HelperProfile.objects.filter(is_helper=True)
    # nearby_helpers = []
    # for helper in helpers:
    #     if helper.latitude is not None and helper.longitude is not None:
    #         distance = calculate_distance(help_request.latitude, help_request.longitude, helper.latitude, helper.longitude)
    #         if distance <= 5:  # 5km 이내의 헬퍼만 포함
    #             nearby_helpers.append(helper)

    # for helper in nearby_helpers:
    #     if helper.device_token:
    #         print(f"Sending notification to {helper.user.username} with token {helper.device_token}")
    #         result = send_push_notification(
    #             helper.device_token,
    #             'New Help Request',
    #             f'New help request from {help_request.requester.username}',
    #             {'request_id': str(help_request.id), 'url': helper_url }
    #         )
    #         print(result)
    #         if not result['success']:
    #             print(f"Failed to send notification to {helper.user.username}: {result['error']}")
    helpers = HelperProfile.objects.filter(is_helper=True)
    print(f"Found {helpers.count()} helpers")
    for helper in helpers:
        if helper.device_token:
            print(f"Sending notification to {helper.user.username} with token {helper.device_token}")
            result = send_push_notification(
                helper.device_token,
                'KI-DO 도움요청',
                f'주변에서 도움을 요청하였습니다. 요청한사람:{help_request.requester.username}',
                {'request_id': str(help_request.id), 'url': helper_url }
            )
            print(result)
            if not result['success']:
                print(f"Failed to send notification to {helper.user.username}: {result['error']}")


def send_push_notification_to_requester(help_request):
    """
    헬퍼가 도움 요청을 수락했을 때 요청자에게 푸시 알림을 보내는 함수
    """
    if help_request.requester.helperprofile.device_token:
        print(f"Requester token: {help_request.requester.helperprofile.device_token}")
        result = send_push_notification(
            help_request.requester.helperprofile.device_token,
            'KI-DO 도움요청',
            f'KI-DO 도움요청서비스가 수락되었습니다. 수락한사람:{help_request.helper.username}.',
            {'helper_phone': help_request.helper.helperprofile.phone_number, 'url': requester_url}
        )
        print(f"Send notification result: {result}")
        return result
    else:
        print("No device token found for requester.")
        return {'success': False, 'error': 'No device token found'}



