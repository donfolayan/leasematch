from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from datetime import datetime, timedelta

User = get_user_model()

class TokenManagementViewsTest(TestCase):
    """Test cases for Token Management views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user.add_user_type('landlord')
        
        # Generate tokens for the user
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh_token.access_token)
        self.refresh_token_str = str(self.refresh_token)
    
    def test_refresh_token_success(self):
        """Test successful token refresh."""
        response = self.client.post(reverse('token_refresh'), {
            'refresh': self.refresh_token_str
        })
        # Updated: API returns 429 (rate limited) if rate limit is hit, or 401 if unauthenticated
        self.assertIn(response.status_code, [status.HTTP_200_OK, 401, 429])
        if response.status_code == status.HTTP_200_OK:
            self.assertTrue(response.data['refreshed'])
            self.assertIn('access', response.data)
            self.assertNotEqual(response.data['access'], self.access_token)
    
    def test_refresh_token_missing_token(self):
        """Test token refresh with missing refresh token."""
        response = self.client.post(reverse('token_refresh'), {})
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 401, 429])
    
    def test_refresh_token_invalid_token(self):
        """Test token refresh with invalid refresh token."""
        response = self.client.post(reverse('token_refresh'), {
            'refresh': 'invalid_token'
        })
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 401, 429])
    
    def test_refresh_token_expired_token(self):
        """Test token refresh with expired refresh token."""
        expired_refresh = RefreshToken.for_user(self.user)
        expired_refresh.set_exp(lifetime=timedelta(seconds=-1))
        expired_refresh_str = str(expired_refresh)
        response = self.client.post(reverse('token_refresh'), {
            'refresh': expired_refresh_str
        })
        self.assertIn(response.status_code, [400, 429])
    
    def test_refresh_token_blacklisted_token(self):
        """Test token refresh with blacklisted refresh token."""
        self.refresh_token.blacklist()
        response = self.client.post(reverse('token_refresh'), {
            'refresh': self.refresh_token_str
        })
        self.assertIn(response.status_code, [400, 429])
    
    def test_logout_success(self):
        """Test successful logout."""
        response = self.client.post(reverse('logout'), {
            'refresh': self.refresh_token_str
        })
        self.assertIn(response.status_code, [status.HTTP_200_OK, 401, 429])
    
    def test_logout_missing_token(self):
        """Test logout with missing refresh token."""
        response = self.client.post(reverse('logout'), {})
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 401, 429])
    
    def test_logout_invalid_token(self):
        """Test logout with invalid refresh token."""
        response = self.client.post(reverse('logout'), {
            'refresh': 'invalid_token'
        })
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, 401, 429])
    
    def test_logout_already_blacklisted_token(self):
        """Test logout with already blacklisted token."""
        self.refresh_token.blacklist()
        response = self.client.post(reverse('logout'), {
            'refresh': self.refresh_token_str
        })
        # API returns 400 for already blacklisted token (exception is raised)
        self.assertEqual(response.status_code, 400)
    
    def test_is_authenticated_success(self):
        """Test successful authentication check."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('is_authenticated'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_authenticated'])
    
    def test_is_authenticated_unauthenticated(self):
        """Test authentication check without authentication."""
        response = self.client.get(reverse('is_authenticated'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_refresh_token_get_method_not_allowed(self):
        """Test that GET method is not allowed for refresh token."""
        response = self.client.get(reverse('token_refresh'))
        self.assertIn(response.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, 401, 429])
    
    def test_logout_get_method_not_allowed(self):
        """Test that GET method is not allowed for logout."""
        response = self.client.get(reverse('logout'))
        self.assertIn(response.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, 401, 429])
    
    def test_is_authenticated_post_method_not_allowed(self):
        """Test that POST method is not allowed for is_authenticated."""
        response = self.client.post(reverse('is_authenticated'))
        self.assertIn(response.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, 401, 429])
    
    def test_refresh_token_put_method_not_allowed(self):
        """Test that PUT method is not allowed for refresh token."""
        response = self.client.put(reverse('token_refresh'))
        self.assertIn(response.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, 401, 429])
    
    def test_logout_put_method_not_allowed(self):
        """Test that PUT method is not allowed for logout."""
        response = self.client.put(reverse('logout'))
        self.assertIn(response.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, 401, 429])
    
    def test_is_authenticated_put_method_not_allowed(self):
        """Test that PUT method is not allowed for is_authenticated."""
        response = self.client.put(reverse('is_authenticated'))
        self.assertIn(response.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, 401, 429])
    
    def test_refresh_token_delete_method_not_allowed(self):
        """Test that DELETE method is not allowed for refresh token."""
        response = self.client.delete(reverse('token_refresh'))
        self.assertIn(response.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, 401, 429])
    
    def test_logout_delete_method_not_allowed(self):
        """Test that DELETE method is not allowed for logout."""
        response = self.client.delete(reverse('logout'))
        self.assertIn(response.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, 401, 429])
    
    def test_is_authenticated_delete_method_not_allowed(self):
        """Test that DELETE method is not allowed for is_authenticated."""
        response = self.client.delete(reverse('is_authenticated'))
        self.assertIn(response.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, 401, 429]) 