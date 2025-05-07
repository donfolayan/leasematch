from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import CustomUser
from django.core.cache import cache
from django.contrib.auth.tokens import default_token_generator

class AuthenticationViewsTestCase(TestCase):
    def setUp(self):
        """
        Set up test data and client.
        """
        self.client = APIClient()

        # Ensure no user with the email donfolayan@gmail.com exists
        CustomUser.objects.filter(email="donfolayan@gmail.com").delete()

        # Create a test user with the email donfolayan@gmail.com
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="donfolayan@gmail.com",  # Use the Mailtrap demo email
            password="password123",
            is_active=True
        )

        # URLs for the views
        self.register_url = reverse('register')
        self.verify_otp_url = reverse('verify_otp')
        self.resend_otp_url = reverse('resend_otp')
        self.forgot_password_url = reverse('forgot_password')
        self.verify_password_reset_otp_url = reverse('verify_password_reset_otp')
        self.reset_password_url = reverse('reset_password')
        self.reactivate_account_url = reverse('reactivate_account')

    def test_register(self):
        """
        Test user registration.
        """
        data = {
        "username": "donfolayan",
        "email": "donfolayan@gmail.com",
        "password": "myPassword",
        "first_name": "Donald",
        "last_name": "Folayan",
        "user_type": "agent"
        }   
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(CustomUser.objects.filter(email="donfolayan@gmail.com").exists())

    def test_verify_otp(self):
        """
        Test OTP verification.
        """
        # Generate OTP and store it in the cache
        otp = "123456"
        cache.set(f'otp_{self.user.id}', otp, timeout=300)

        data = {
            "user_id": self.user.id,
            "otp": otp
        }
        response = self.client.post(self.verify_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)

    def test_resend_otp(self):
        """
        Test resending OTP.
        """
        data = {
            "user_id": self.user.id
        }
        response = self.client.post(self.resend_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)

    def test_forgot_password(self):
        """
        Test forgot password.
        """
        data = {
            "email": self.user.email  # Use the Mailtrap demo email
        }
        response = self.client.post(self.forgot_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)

    def test_verify_password_reset_otp(self):
        """
        Test verifying password reset OTP.
        """
        # Generate OTP and store it in the cache
        otp = "123456"
        cache.set(f'otp_{self.user.id}', otp, timeout=300)

        data = {
            "email": self.user.email,  # Use the Mailtrap demo email
            "otp": otp
        }
        response = self.client.post(self.verify_password_reset_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)

    def test_reset_password(self):
        """
        Test resetting the password.
        """
        data = {
            "email": self.user.email,  # Use the Mailtrap demo email
            "new_password": "newpassword123"
        }
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)

        # Verify the password was updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_reactivate_account(self):
        """
        Test reactivating an account.
        """
        # Generate a token for the user
        token = default_token_generator.make_token(self.user)

        data = {
            "user_id": self.user.id,
            "token": token
        }
        response = self.client.post(self.reactivate_account_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)

        # Verify the user is active
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)