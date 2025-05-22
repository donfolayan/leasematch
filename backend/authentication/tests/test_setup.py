from rest_framework.test import APITestCase
from django.urls import reverse

class TestSetup(APITestCase):
    
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

        user_data = {
            "email": "test@test.test",
            "username": "user",
            "password": "password",
        }


    def tearDown(self):
        return super().tearDown()
