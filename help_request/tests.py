from django.test import TestCase
from django.contrib.auth.models import User
from .models import HelperProfile, HelpRequest
from .utils import calculate_distance, send_push_notification_to_helpers
from unittest.mock import patch

class DistanceCalculationTestCase(TestCase):

    def setUp(self):
        # Create a guest user
        self.guest_user = User.objects.create(username='guest_user')
        self.guest_profile = HelperProfile.objects.create(
            user=self.guest_user,
            latitude=37.5665,  # Seoul, South Korea (latitude)
            longitude=126.9780  # Seoul, South Korea (longitude)
        )

        # Create a helper user within 5km
        self.helper_user = User.objects.create(username='helper_user')
        self.helper_profile = HelperProfile.objects.create(
            user=self.helper_user,
            is_helper=True,
            latitude=37.5700,  # Latitude slightly different
            longitude=126.9800,  # Longitude slightly different
            device_token='token_within_5km'
        )

        # Create a helper user slightly outside 5km
        self.helper_user_far = User.objects.create(username='helper_user_far')
        self.helper_profile_far = HelperProfile.objects.create(
            user=self.helper_user_far,
            is_helper=True,
            latitude=37.6150,  # Latitude farther away
            longitude=127.0000,  # Longitude farther away
            device_token='token_outside_5km'
        )

    def test_calculate_distance_within_5km(self):
        distance = calculate_distance(
            self.guest_profile.latitude,
            self.guest_profile.longitude,
            self.helper_profile.latitude,
            self.helper_profile.longitude
        )
        self.assertLessEqual(distance, 5, "Helper user is within 5km range.")

    def test_calculate_distance_outside_5km(self):
        distance = calculate_distance(
            self.guest_profile.latitude,
            self.guest_profile.longitude,
            self.helper_profile_far.latitude,
            self.helper_profile_far.longitude
        )
        self.assertGreater(distance, 5, "Helper user is outside 5km range.")

    @patch('help_request.utils.send_push_notification')
    def test_send_push_notification_to_helpers(self, mock_send_push_notification):
        # Create a help request
        help_request = HelpRequest.objects.create(
            requester=self.guest_user,
            phone_number='010-1234-5678',
            latitude=self.guest_profile.latitude,
            longitude=self.guest_profile.longitude
        )

        # Send push notifications to helpers
        send_push_notification_to_helpers(help_request)

        # Check that notification was sent to the nearby helper
        mock_send_push_notification.assert_any_call(
            'token_within_5km',
            'New Help Request',
            f'New help request from {help_request.requester.username}',
            {'request_id': str(help_request.id), 'url': 'http://localhost:3000/help_req/settings_helper_main'}
        )

        # Ensure that notification was not sent to the far away helper
        calls = [call[0][0] for call in mock_send_push_notification.call_args_list]
        self.assertNotIn('token_outside_5km', calls, "Notification should not be sent to helpers outside 5km range.")
