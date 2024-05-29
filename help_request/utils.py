import firebase_admin
from firebase_admin import messaging
from django.contrib.auth.models import User
from .models import HelperProfile

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
        response = messaging.send(message)
        return {'success': True, 'response': response}
    except firebase_admin.exceptions.FirebaseError as e:
        print(f"FCM API call error: {e}")
        return {'success': False, 'error': str(e)}
    except Exception as e:
        print(f"General error: {e}")
        return {'success': False, 'error': str(e)}

def send_push_notification_to_helpers(help_request):
    """
    도움 요청을 헬퍼에게 푸시 알림으로 보내는 함수
    """
    helpers = HelperProfile.objects.filter(is_helper=True)  # 헬퍼로 설정된 사용자 필터링
    for helper in helpers:
        if helper.device_token:
            print(f"Sending notification to {helper.user.username} with token {helper.device_token}")
            result = send_push_notification(
                helper.device_token,
                'KI-DO 도움요청',
                f'주변에서 도움을 요청하였습니다. 요청한사람:{help_request.requester.username}',
                {'request_id': str(help_request.id), 'url': 'http://localhost:3000/help_req/settings_helper_main'}
            )
            print(result)
            if not result['success']:
                print(f"Failed to send notification to {helper.user.username}: {result['error']}")

def send_push_notification_to_requester(help_request):
    """
    헬퍼가 도움 요청을 수락했을 때 요청자에게 푸시 알림을 보내는 함수
    """
    if help_request.requester.helperprofile.device_token:
        send_push_notification(
            help_request.requester.helperprofile.device_token,
            'KI-DO 도움요청이 수락되었습니다.',
            f'KI-DO 도움요청서비스가 수락되었습니다. 수락한사람:{help_request.helper.username}.',
            {'helper_phone': help_request.helper.helperprofile.phone_number, 'url': 'http://localhost:3000/help_req/req_success'}
        )
