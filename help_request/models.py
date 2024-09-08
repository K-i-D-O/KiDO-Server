from django.db import models
from django.contrib.auth.models import User

class HelperProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    device_token = models.CharField(max_length=255, blank=True, null=True)
    is_helper = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    sendbird_user_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} HelperProfile'

    def generate_sendbird_user_id(self):
        # 헬퍼 프로파일에서 Sendbird User ID를 생성하는 로직
        if self.user.username.startswith('guest_'):
            return self.user.username
        else:
            return f'kakao_{self.user.username}'  # 예: 카카오 ID 기반으로 설정

    def save(self, *args, **kwargs):
        if not self.sendbird_user_id:
            self.sendbird_user_id = self.generate_sendbird_user_id()
        super().save(*args, **kwargs)
    
class HelpRequest(models.Model):
    requester = models.ForeignKey(User, related_name='requests', on_delete=models.CASCADE)
    helper = models.ForeignKey(User, related_name='helps', on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=20)  # Add this line
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f'Request by {self.requester.username} (Accepted: {self.is_accepted})'
