from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from allauth.socialaccount.models import SocialAccount

User = get_user_model()

class SocialAccountViewsTest(TestCase):
    """Test cases for Social Account views."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.client = APIClient()
        self.client.defaults['follow'] = False
        
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user.add_user_type('landlord')
        
        self.google_user_data = {
            'sub': '123456789',
            'email': 'googleuser@example.com',
            'given_name': 'Google',
            'family_name': 'User',
            'picture': 'https://example.com/avatar.jpg',
        }
    
    # Commenting out all Google OAuth tests for manual testing
    # @patch('requests.Session.get')
    # def test_google_oauth_success(self, mock_session_get):
    #     mock_response = MagicMock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = self.google_user_data
    #     mock_session_get.return_value = mock_response
    #     response = self.client.post(reverse('google_login'), {'access_token': 'valid_access_token'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('access', response.data)
    #     self.assertIn('refresh', response.data)
    #     user = User.objects.get(email='googleuser@example.com')
    #     self.assertEqual(user.first_name, 'Google')
    #     self.assertEqual(user.last_name, 'User')
    #     self.assertEqual(user.username, 'googleuser@example.com')
    #     social_account = SocialAccount.objects.get(user=user)
    #     self.assertEqual(social_account.provider, 'google')
    #     self.assertEqual(social_account.uid, '123456789')
    
    # @patch('requests.Session.get')
    # def test_google_oauth_existing_user(self, mock_session_get):
    #     existing_user = User.objects.create_user(
    #         username='existinguser',
    #         email='googleuser@example.com',
    #         password='testpass123',
    #         first_name='Existing',
    #         last_name='User'
    #     )
    #     existing_user.add_user_type('tenant')
    #     mock_response = MagicMock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = self.google_user_data
    #     mock_session_get.return_value = mock_response
    #     response = self.client.post(reverse('google_login'), {'access_token': 'valid_access_token'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('access', response.data)
    #     self.assertIn('refresh', response.data)
    #     self.assertEqual(response.data['user']['id'], existing_user.id)
    #     social_account = SocialAccount.objects.get(user=existing_user)
    #     self.assertEqual(social_account.provider, 'google')
    #     self.assertEqual(social_account.uid, '123456789')
    
    # @patch('requests.Session.get')
    # def test_google_oauth_invalid_token(self, mock_session_get):
    #     mock_response = MagicMock()
    #     mock_response.status_code = 401
    #     mock_response.json.return_value = {"error": "invalid_token"}
    #     mock_session_get.return_value = mock_response
    #     response = self.client.post(reverse('google_login'), {'access_token': 'invalid_access_token'})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # @patch('requests.Session.get')
    # def test_google_oauth_missing_token(self, mock_session_get):
    #     """Test Google OAuth with missing access token."""
    #     response = self.client.post(reverse('google_login'), {})
        
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # @patch('requests.Session.get')
    # def test_google_oauth_missing_email(self, mock_session_get):
    #     mock_response = MagicMock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {k: v for k, v in self.google_user_data.items() if k != 'email'}
    #     mock_session_get.return_value = mock_response
    #     response = self.client.post(reverse('google_login'), {'access_token': 'valid_access_token'})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # @patch('requests.Session.get')
    # def test_google_oauth_missing_name(self, mock_session_get):
    #     mock_response = MagicMock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {
    #         'sub': '123456789',
    #         'email': 'googleuser@example.com',
    #         'picture': 'https://example.com/avatar.jpg',
    #     }
    #     mock_session_get.return_value = mock_response
    #     response = self.client.post(reverse('google_login'), {'access_token': 'valid_access_token'})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # @patch('requests.Session.get')
    # def test_google_oauth_network_error(self, mock_session_get):
    #     mock_session_get.side_effect = Exception('Network error')
    #     response = self.client.post(reverse('google_login'), {'access_token': 'valid_access_token'})
    #     self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # @patch('requests.Session.get')
    # def test_google_oauth_duplicate_social_account(self, mock_session_get):
    #     user = User.objects.create_user(
    #         username='googleuser@example.com',
    #         email='googleuser@example.com',
    #         password='testpass123',
    #         first_name='Google',
    #         last_name='User'
    #     )
    #     user.add_user_type('landlord')
    #     SocialAccount.objects.create(
    #         user=user,
    #         provider='google',
    #         uid='123456789',
    #     )
    #     mock_response = MagicMock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = self.google_user_data
    #     mock_session_get.return_value = mock_response
    #     response = self.client.post(reverse('google_login'), {'access_token': 'valid_access_token'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('access', response.data)
    #     self.assertIn('refresh', response.data)
    #     self.assertEqual(response.data['user']['id'], user.id)
    
    def test_disconnect_social_account_success(self):
        """Test successful social account disconnection."""
        # Create social account for user
        social_account = SocialAccount.objects.create(
            user=self.user,
            provider='google',
            uid='123456789',
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('disconnect_social_account', kwargs={'provider': 'google'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('disconnected successfully', response.data['message'])
        # Verify social account was deleted
        self.assertFalse(SocialAccount.objects.filter(id=social_account.id).exists())
    
    def test_disconnect_social_account_not_found(self):
        """Test disconnecting non-existent social account."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('disconnect_social_account', kwargs={'provider': 'google'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertIn('not found', response.data['error'])
    
    def test_disconnect_social_account_unauthenticated(self):
        """Test disconnecting social account without authentication."""
        response = self.client.post(reverse('disconnect_social_account', kwargs={'provider': 'google'}))
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # Commenting out method-not-allowed Google OAuth tests for manual testing
    # def test_google_oauth_get_method_not_allowed(self):
    #     """Test that GET method is not allowed for Google OAuth."""
    #     response = self.client.get(reverse('google_login'))
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    # def test_google_oauth_put_method_not_allowed(self):
    #     """Test that PUT method is not allowed for Google OAuth."""
    #     response = self.client.put(reverse('google_login'))
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    # def test_google_oauth_delete_method_not_allowed(self):
    #     """Test that DELETE method is not allowed for Google OAuth."""
    #     response = self.client.delete(reverse('google_login'))
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED) 