from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import Group
from django.urls import reverse
from django.test import override_settings

@override_settings(REST_FRAMEWORK={
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {}
})


class TestSetup(APITestCase):

    @classmethod
    def setUpTestData(cls):
        Group.objects.create(name='tenant')
        Group.objects.create(name='landlord')
        Group.objects.create(name='agent')
    
    def setUp(self):
        """
        Set up the test case by defining the URLs for the authentication endpoints.
        """
        self.register_url = reverse('register')
        self.login_url = reverse('token_obtain_pair')
        self.verify_otp_url = reverse('verify_otp')
        self.resend_otp_url = reverse('resend_otp')
        self.forgot_password_url = reverse('forgot_password')
        self.reset_password_url = reverse('reset_password')
        self.verify_password_reset_otp_url = reverse('verify_password_reset_otp')
        self.change_password_url = reverse('change_password')
        self.send_activation_token_url = reverse('send_activation_token')
        self.activate_account_url = reverse('activate_account')

        self.user_data = {
            "email": "test@test.test",
            "username": "user",
            "password": "password",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "tenant",
        }

        self.client = APIClient()
        self.client.default_format = 'json'
        self.client.defaults.update({
            'HTTP_X_TEST_CLIENT': 'true'
        })


    def tearDown(self):
        return super().tearDown()
