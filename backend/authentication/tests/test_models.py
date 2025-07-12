import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import CustomUser, UserType

User = get_user_model()

class CustomUserModelTest(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create user types
        self.landlord_type = UserType.objects.create(name='landlord')
        self.tenant_type = UserType.objects.create(name='tenant')
        self.agent_type = UserType.objects.create(name='agent')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_user_creation(self):
        """Test user creation with valid data."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_creation_without_email(self):
        """Test user creation without email raises error."""
        user_data = self.user_data.copy()
        del user_data['email']
        
        with self.assertRaises(ValueError):
            User.objects.create_user(**user_data)

    def test_user_creation_without_password(self):
        """Test user creation without password raises error."""
        user_data = self.user_data.copy()
        del user_data['password']
        
        with self.assertRaises(ValueError):
            User.objects.create_user(**user_data)

    def test_user_type_management(self):
        """Test user type management methods."""
        user = User.objects.create_user(**self.user_data)
        
        # Test adding user type
        user.add_user_type('landlord')
        self.assertTrue(user.user_type.filter(name='landlord').exists())
        
        # Test adding multiple user types
        user.add_user_type('agent')
        self.assertTrue(user.user_type.filter(name='landlord').exists())
        self.assertTrue(user.user_type.filter(name='agent').exists())
        self.assertEqual(user.user_type.count(), 2)

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')

    def test_user_onboarding_status(self):
        """Test user onboarding status."""
        user = User.objects.create_user(**self.user_data)
        # Default onboarding step should be 1
        self.assertEqual(user.onboarding_step, 1)

    def test_user_is_onboarded(self):
        """Test user is_onboarded property."""
        user = User.objects.create_user(**self.user_data)
        # Default should be False
        self.assertFalse(user.is_onboarded)

    def test_user_is_onboarded_true(self):
        """Test user is_onboarded property when completed."""
        user = User.objects.create_user(**self.user_data)
        user.is_onboarded = True
        user.save()
        self.assertTrue(user.is_onboarded)

    def test_user_email_unique(self):
        """Test that email must be unique."""
        User.objects.create_user(**self.user_data)
        
        duplicate_user_data = self.user_data.copy()
        duplicate_user_data['username'] = 'testuser2'
        duplicate_user_data['email'] = 'test@example.com'
        
        with self.assertRaises(Exception):  # IntegrityError or similar
            User.objects.create_user(**duplicate_user_data)

    def test_user_username_unique(self):
        """Test that username must be unique."""
        User.objects.create_user(**self.user_data)
        
        duplicate_user_data = self.user_data.copy()
        duplicate_user_data['username'] = 'testuser'
        duplicate_user_data['email'] = 'test2@example.com'
        
        with self.assertRaises(Exception):  # IntegrityError or similar
            User.objects.create_user(**duplicate_user_data)

    def test_user_required_fields(self):
        """Test that required fields are enforced."""
        # Test without email
        user_data = self.user_data.copy()
        del user_data['email']
        
        with self.assertRaises(ValueError):
            User.objects.create_user(**user_data)

        # Test without password
        user_data = self.user_data.copy()
        del user_data['password']
        
        with self.assertRaises(ValueError):
            User.objects.create_user(**user_data)

    def test_user_optional_fields(self):
        """Test that optional fields can be null/blank."""
        user_data = self.user_data.copy()
        user_data.update({
            'first_name': '',
            'last_name': ''
        })
        
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, '')

    def test_user_password_hashing(self):
        """Test that passwords are properly hashed."""
        user = User.objects.create_user(**self.user_data)
        
        # Password should be hashed
        self.assertNotEqual(user.password, 'testpass123')
        
        # But should still validate correctly
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.check_password('wrongpassword'))

    def test_user_is_active_default(self):
        """Test that users are active by default."""
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(user.is_active)

    def test_user_is_staff_default(self):
        """Test that users are not staff by default."""
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_staff)

    def test_user_is_superuser_default(self):
        """Test that users are not superuser by default."""
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_superuser)
