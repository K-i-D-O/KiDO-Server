from django.urls import path
from . import views

app_name = 'help_request'

urlpatterns = [
    path('api/guest-login/', views.guest_login, name='guest_login'),
    path('api/become-helper/', views.become_helper, name='become_helper'),
    path('api/kakao/callback/', views.kakao_callback, name='kakao_callback'),
    path('api/kakao-helper/', views.kakao_login_helper, name='kakao_helper'),
    path('api/request-help/', views.request_help, name='request_help'),
    path('api/requests/', views.get_requests, name='requests'),
    path('api/request-details/<int:request_id>/', views.get_request_details, name='request-details'),
    path('api/respond-to-request/<int:request_id>/<str:response>/', views.respond_to_request, name='respond_to_request'),
    path('api/save-token/', views.save_token, name='save_token'),
]
