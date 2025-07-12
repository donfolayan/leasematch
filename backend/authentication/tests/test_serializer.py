from django.test import TestCase
from django.contrib.auth import get_user_model
from authentication.serializer import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    UserProfileSerializer
)
from rest_framework.exceptions import ValidationError

User = get_user_model()

class UserRegistrationSerializerTest(TestCase):
    """Test cases for UserRegistrationSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_user_registration_serializer_valid_data(self):
        """Test UserRegistrationSerializer with valid data."""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_user_registration_serializer_missing_required_fields(self):
        """Test UserRegistrationSerializer with missing required fields."""
        invalid_data = self.valid_data.copy()
        del invalid_data['username']
        
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
    
    def test_user_registration_serializer_password_mismatch(self):
        """Test UserRegistrationSerializer with password mismatch."""
        invalid_data = self.valid_data.copy()
        invalid_data['confirm_password'] = 'differentpassword'
        
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_user_registration_serializer_weak_password(self):
        """Test UserRegistrationSerializer with weak password."""
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = '123'
        invalid_data['confirm_password'] = '123'
        
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_user_registration_serializer_invalid_email(self):
        """Test UserRegistrationSerializer with invalid email."""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_user_registration_serializer_duplicate_username(self):
        """Test UserRegistrationSerializer with duplicate username."""
        # Create user with same username
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='testpass123'
        )
        
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
    
    def test_user_registration_serializer_duplicate_email(self):
        """Test UserRegistrationSerializer with duplicate email."""
        # Create user with same email
        User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='testpass123'
        )
        
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_user_registration_serializer_create_user(self):
        """Test UserRegistrationSerializer create method."""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpass123'))


class UserLoginSerializerTest(TestCase):
    """Test cases for UserLoginSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.valid_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
    
    def test_user_login_serializer_valid_data(self):
        """Test UserLoginSerializer with valid data."""
        serializer = UserLoginSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_user_login_serializer_missing_username(self):
        """Test UserLoginSerializer with missing username."""
        invalid_data = self.valid_data.copy()
        del invalid_data['username']
        
        serializer = UserLoginSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
    
    def test_user_login_serializer_missing_password(self):
        """Test UserLoginSerializer with missing password."""
        invalid_data = self.valid_data.copy()
        del invalid_data['password']
        
        serializer = UserLoginSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_user_login_serializer_invalid_credentials(self):
        """Test UserLoginSerializer with invalid credentials."""
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'wrongpassword'
        
        serializer = UserLoginSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_user_login_serializer_nonexistent_user(self):
        """Test UserLoginSerializer with nonexistent user."""
        invalid_data = self.valid_data.copy()
        invalid_data['username'] = 'nonexistentuser'
        
        serializer = UserLoginSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_user_login_serializer_validate_method(self):
        """Test UserLoginSerializer validate method."""
        serializer = UserLoginSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validate(self.valid_data)
        self.assertEqual(validated_data['user'], self.user)


class PasswordResetSerializerTest(TestCase):
    """Test cases for PasswordResetSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.valid_data = {
            'email': 'test@example.com'
        }
    
    def test_password_reset_serializer_valid_data(self):
        """Test PasswordResetSerializer with valid data."""
        serializer = PasswordResetSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_password_reset_serializer_missing_email(self):
        """Test PasswordResetSerializer with missing email."""
        invalid_data = {}
        
        serializer = PasswordResetSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_password_reset_serializer_invalid_email(self):
        """Test PasswordResetSerializer with invalid email."""
        invalid_data = {'email': 'invalid-email'}
        
        serializer = PasswordResetSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_password_reset_serializer_nonexistent_email(self):
        """Test PasswordResetSerializer with nonexistent email."""
        invalid_data = {'email': 'nonexistent@example.com'}
        
        serializer = PasswordResetSerializer(data=invalid_data)
        self.assertTrue(serializer.is_valid())  # Should still be valid for security


class PasswordResetConfirmSerializerTest(TestCase):
    """Test cases for PasswordResetConfirmSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.valid_data = {
            'token': 'valid_token',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        }
    
    def test_password_reset_confirm_serializer_valid_data(self):
        """Test PasswordResetConfirmSerializer with valid data."""
        serializer = PasswordResetConfirmSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_password_reset_confirm_serializer_missing_token(self):
        """Test PasswordResetConfirmSerializer with missing token."""
        invalid_data = self.valid_data.copy()
        del invalid_data['token']
        
        serializer = PasswordResetConfirmSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('token', serializer.errors)
    
    def test_password_reset_confirm_serializer_missing_password(self):
        """Test PasswordResetConfirmSerializer with missing password."""
        invalid_data = self.valid_data.copy()
        del invalid_data['password']
        
        serializer = PasswordResetConfirmSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_password_reset_confirm_serializer_password_mismatch(self):
        """Test PasswordResetConfirmSerializer with password mismatch."""
        invalid_data = self.valid_data.copy()
        invalid_data['confirm_password'] = 'differentpassword'
        
        serializer = PasswordResetConfirmSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_password_reset_confirm_serializer_weak_password(self):
        """Test PasswordResetConfirmSerializer with weak password."""
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = '123'
        invalid_data['confirm_password'] = '123'
        
        serializer = PasswordResetConfirmSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)


class UserProfileSerializerTest(TestCase):
    """Test cases for UserProfileSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user.add_user_type('landlord')
        
        self.valid_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
    
    def test_user_profile_serializer_valid_data(self):
        """Test UserProfileSerializer with valid data."""
        serializer = UserProfileSerializer(self.user, data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_user_profile_serializer_invalid_email(self):
        """Test UserProfileSerializer with invalid email."""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        serializer = UserProfileSerializer(self.user, data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_user_profile_serializer_duplicate_email(self):
        """Test UserProfileSerializer with duplicate email."""
        # Create another user with different email
        User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'other@example.com'
        
        serializer = UserProfileSerializer(self.user, data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_user_profile_serializer_update_user(self):
        """Test UserProfileSerializer update method."""
        serializer = UserProfileSerializer(self.user, data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertEqual(updated_user.email, 'updated@example.com')
    
    def test_user_profile_serializer_serialization(self):
        """Test UserProfileSerializer serialization."""
        serializer = UserProfileSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['last_name'], 'User')
        self.assertIn('user_types', data)
        self.assertIn('is_onboarded', data)
        self.assertIn('onboarding_step', data)


