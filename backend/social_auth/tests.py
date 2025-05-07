from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth

CustomUser = get_user_model()


class SocialAuthViewsTestCase(APITestCase):
    def setUp(self):
        """
        Set up test data and client.
        """
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123"
        )
        self.social_auth_url = reverse('social_auth', args=['google-oauth2'])
        self.disconnect_social_account_url = reverse('disconnect_social_account')

    @patch('backend.utils.social_auth.authenticate_social_user')
    def test_social_auth_success(self, mock_authenticate):
        """
        Test successful social authentication.
        """
        mock_authenticate.return_value = self.user  # Simulate successful authentication
        response = self.client.post(self.social_auth_url, data={"access_token": "valid_access_token"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    @patch('backend.utils.social_auth.authenticate_social_user')
    def test_social_auth_inactive_user(self, mock_authenticate):
        """
        Test social authentication for an inactive user.
        """
        self.user.is_active = False
        self.user.save()
        mock_authenticate.return_value = self.user  # Simulate successful authentication

        response = self.client.post(self.social_auth_url, data={"access_token": "valid_access_token"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)  # User should now be active
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    @patch('backend.utils.social_auth.authenticate_social_user')
    def test_social_auth_invalid_credentials(self, mock_authenticate):
        """
        Test social authentication with invalid credentials.
        """
        mock_authenticate.side_effect = Exception("Invalid credentials provided")
        response = self.client.post(self.social_auth_url, data={"access_token": "invalid_access_token"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid credentials provided')

    def test_social_auth_missing_provider(self):
        """
        Test social authentication with missing provider.
        """
        response = self.client.post(reverse('social_auth', args=['invalid-provider']), data={"access_token": "valid_access_token"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], "Provider 'invalid-provider' is not supported.")

    def test_social_auth_missing_access_token(self):
        """
        Test social authentication with missing access token.
        """
        response = self.client.post(self.social_auth_url, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Missing provider or access token')

    def test_disconnect_social_account_success(self):
        """
        Test successful disconnection of a social account.
        """
        UserSocialAuth.objects.create(user=self.user, provider="google-oauth2", uid="12345")
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.disconnect_social_account_url, data={"provider": "google-oauth2"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertFalse(UserSocialAuth.objects.filter(user=self.user, provider="google-oauth2").exists())

    def test_disconnect_social_account_missing_provider(self):
        """
        Test disconnection of a social account with missing provider.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.disconnect_social_account_url, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Provider is required')

    def test_disconnect_social_account_not_linked(self):
        """
        Test disconnection of a social account that is not linked.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.disconnect_social_account_url, data={"provider": "google-oauth2"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'google-oauth2 account not linked')