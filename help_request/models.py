from django.db import models
from django.contrib.auth.models import User

class HelperProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    device_token = models.CharField(max_length=255, blank=True, null=True)
    is_helper = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} HelperProfile'
    
class HelpRequest(models.Model):
    requester = models.ForeignKey(User, related_name='requests', on_delete=models.CASCADE)
    helper = models.ForeignKey(User, related_name='helps', on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=20)  # Add this line
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Request by {self.requester.username} (Accepted: {self.is_accepted})'
