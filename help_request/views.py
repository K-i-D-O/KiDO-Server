import json
import random
import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt 
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import HelpRequest, HelperProfile
from .utils import send_push_notification_to_helpers, send_push_notification_to_requester


KAKAO_CLIENT_ID = 'efb6faf4cdddaddd5f04d3cda75e0612'
KAKAO_REDIRECT_URI = 'http://localhost:3000/help_req/settings_helper_main'

def generate_random_phone_number():
    return f'010-{random.randint(1000,9999)}-{random.randint(1000,9999)}'

@csrf_exempt
def save_token(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('token')
        username = data.get('username')
        
        if not token or not username:
            return JsonResponse({'status': 'error', 'message': 'Token or username missing'}, status=400)
        
        try:
            user = User.objects.get(username=username)
            profile, created = HelperProfile.objects.get_or_create(user=user)
            profile.device_token = token
            profile.save()
            print(f"Token for {username}: {token}")  # 저장된 토큰을 확인
            return JsonResponse({'status': 'success'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def guest_login(request):
    if request.method == 'POST':
        username = f'guest_{random.randint(1000,9999)}'
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_unusable_password()
            user.save()
            HelperProfile.objects.create(user=user)
            print(user)
        login(request, user)
        return JsonResponse({'status': 'success', 'username': username}, status=200)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def become_helper(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        is_helper = data.get('is_helper')
        username = data.get('username')
        if not username:
            return JsonResponse({'status': 'error', 'message': 'No username provided'}, status=400)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=404)

        if user.username.startswith('guest_'):
            return JsonResponse({'status': 'error', 'message': 'Guest users cannot become helpers'}, status=200)
        
        if is_helper is not None:
            profile = user.helperprofile
            profile.is_helper = is_helper
            profile.save()
            return JsonResponse({'status': 'success', 'message': f'Helper status set to {is_helper}'}, status=200)
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def kakao_login_helper(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        kakao_id = data['id']
        nickname = data['nickname']
        # print(data)
        try:
            # Check if a user with the given kakao_id already exists
            user = User.objects.get(username=kakao_id)
            # print(f'User already exists: {user.username}')
        except User.DoesNotExist:
            # Check if there is any guest user
            guest_users = User.objects.filter(username__startswith='guest_')
            if guest_users.exists():
                user = guest_users.first()  # Get the first guest user
                user.username = kakao_id  # Change username to Kakao ID
                user.first_name = nickname
                user.save()
                # print(f'Updated user: {user.username}')
            else:
                user = User.objects.create(username=kakao_id, first_name=nickname)
                user.set_unusable_password()
                user.save()
                HelperProfile.objects.create(user=user)
                # print(f'Created user: {user.username}')

        # Update the user's profile to become a helper
        profile, created = HelperProfile.objects.get_or_create(user=user)
        profile.is_helper = True
        profile.save()
        print("This user is now a helper user")

        return JsonResponse({'status': 'success', 'username': user.username}, status=200)

    return JsonResponse({'status': 'error'}, status=400)


@csrf_exempt
def kakao_callback(request):
    data = json.loads(request.body)
    code = data.get('code')
    print(code)
    if not code:
        return JsonResponse({'status': 'error', 'message': 'No code provided'}, status=400)

    # Get access token
    token_response = requests.post('https://kauth.kakao.com/oauth/token', data={
        'grant_type': 'authorization_code',
        'client_id': KAKAO_CLIENT_ID,
        'redirect_uri': KAKAO_REDIRECT_URI,
        'code': code,
    })

    token_json = token_response.json()
    access_token = token_json.get('access_token')
    if not access_token:
        return JsonResponse({'status': 'error', 'message': 'Failed to get access token'}, status=400)

    # Get user info
    user_response = requests.get('https://kapi.kakao.com/v2/user/me', headers={
        'Authorization': f'Bearer {access_token}',
    })

    user_json = user_response.json()
    kakao_id = user_json['id']
    nickname = user_json['properties']['nickname']

    # Send user data to the helper endpoint
    user_data = {
        'id': kakao_id,
        'nickname': nickname
    }
    # Redirect to frontend with user data as query parameters
    return JsonResponse({'status': 'success', 'user_data': user_data}, status=200)

@csrf_exempt
def request_help(request):
    if request.method == "POST":
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        username = data.get('username')
        
        if not phone_number or not username:
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=404)
        
        help_request = HelpRequest(requester=user, phone_number=phone_number)
        help_request.save()
        
        # 모든 헬퍼에게 푸시 알림
        send_push_notification_to_helpers(help_request)
        
        return JsonResponse({'status': 'success'}, status=200)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

#도움요청 목록
@csrf_exempt
def get_requests(request):
    if request.method == 'GET':
        requests = HelpRequest.objects.filter(is_accepted=False).values('id', 'created_at', 'phone_number')
        requests_list = list(requests)
        return JsonResponse({'requests': requests_list}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def get_request_details(request, request_id):
    if request.method == 'GET':
        try:
            help_request = HelpRequest.objects.get(id=request_id)
            data = {
                'id': help_request.id,
                'created_at': help_request.created_at,
                'phone_number': help_request.phone_number,
                'requester_username': help_request.requester.username,
            }
            return JsonResponse({'status': 'success', 'data': data}, status=200)
        except HelpRequest.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Request not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def respond_to_request(request, request_id, response):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            kakao_id = data.get('kakao_id')

            if not kakao_id:
                return JsonResponse({'status': 'error', 'message': 'Kakao ID not provided'}, status=400)

            try:
                helper_profile = HelperProfile.objects.get(user__username=kakao_id)
                if not helper_profile.is_helper:
                    return JsonResponse({'status': 'error', 'message': 'User is not a helper'}, status=403)

                try:
                    help_request = HelpRequest.objects.get(id=request_id)
                    if response == 'accept':
                        help_request.helper = helper_profile.user
                        help_request.is_accepted = True
                        help_request.save()
                        send_push_notification_to_requester(help_request)
                    elif response == 'reject':
                        help_request.is_accepted = False
                        help_request.delete()
                        # 요청 거절 처리 로직 추가 가능
                    else:
                        return JsonResponse({'status': 'error', 'message': 'Invalid response type'}, status=400)

                    return JsonResponse({'status': 'success'}, status=200)
                except HelpRequest.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Request not found'}, status=404)
            except HelperProfile.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Helper profile not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)