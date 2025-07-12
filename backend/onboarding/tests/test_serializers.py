import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import LandlordProfile, AgentProfile, TenantProfile
from ..serializers import LandlordProfileSerializer, AgentProfileSerializer, TenantProfileSerializer
from authentication.models import UserType

User = get_user_model()

class LandlordProfileSerializerTest(TestCase):
    def setUp(self):
        # Create user type
        self.landlord_type = UserType.objects.create(name='landlord')
        
        self.user = User.objects.create_user(
            username='landlord',
            email='landlord@test.com',
            password='testpass123'
        )
        self.user.add_user_type('landlord')
        self.profile = LandlordProfile.objects.create(user=self.user)

    def test_landlord_profile_serializer_serialization(self):
        """Test LandlordProfileSerializer serialization of existing profile."""
        serializer = LandlordProfileSerializer(self.profile)
        data = serializer.data
        self.assertIn('user', data)
        self.assertIn('documents', data)

    def test_landlord_profile_serializer_valid_data(self):
        """Test LandlordProfileSerializer with valid data."""
        data = {
            'user': self.user.id,
            'documents': None
        }
        serializer = LandlordProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_landlord_profile_serializer_missing_required_fields(self):
        """Test LandlordProfileSerializer with missing required fields."""
        data = {}
        serializer = LandlordProfileSerializer(data=data)
        # 'user' is read-only, so serializer should be valid even if input is empty
        self.assertTrue(serializer.is_valid())

    def test_landlord_profile_serializer_optional_fields(self):
        """Test that optional fields can be null/blank."""
        data = {
            'user': self.user.id,
            'documents': None
        }
        serializer = LandlordProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class AgentProfileSerializerTest(TestCase):
    def setUp(self):
        # Create user type
        self.agent_type = UserType.objects.create(name='agent')
        
        self.user = User.objects.create_user(
            username='agent',
            email='agent@test.com',
            password='testpass123'
        )
        self.user.add_user_type('agent')
        self.profile = AgentProfile.objects.create(
            user=self.user,
            agency_name='Test Agency',
            agency_address='123 Test St',
            service_areas=['Lagos', 'Abuja'],
            service_states=['Lagos', 'FCT'],
            agency_registration_number='REG123'
        )

    def test_agent_profile_serializer_serialization(self):
        """Test AgentProfileSerializer serialization of existing profile."""
        serializer = AgentProfileSerializer(self.profile)
        data = serializer.data
        self.assertIn('user', data)
        self.assertIn('agency_name', data)
        self.assertIn('agency_address', data)
        self.assertIn('service_areas', data)
        self.assertIn('service_states', data)
        self.assertIn('agency_registration_number', data)

    def test_agent_profile_serializer_valid_data(self):
        """Test AgentProfileSerializer with valid data."""
        data = {
            'user': self.user.id,
            'agency_name': 'New Agency',
            'agency_address': '456 New St',
            'service_areas': ['Port Harcourt'],
            'service_states': ['rivers'],  # Use key, not display name
            'agency_registration_number': 'REG456'
        }
        serializer = AgentProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_agent_profile_serializer_missing_required_fields(self):
        """Test AgentProfileSerializer with missing required fields."""
        data = {}
        serializer = AgentProfileSerializer(data=data)
        # 'user' is read-only, so serializer should be valid even if input is empty
        self.assertTrue(serializer.is_valid())

    def test_agent_profile_serializer_optional_fields(self):
        """Test that optional fields can be null/blank or empty, should be valid if serializer allows."""
        data = {
            'user': self.user.id,
            'agency_name': '',
            'agency_address': '',
            'service_areas': [],
            'service_states': [],
            'agency_registration_number': None  # Use None instead of empty string
        }
        serializer = AgentProfileSerializer(data=data)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())


class TenantProfileSerializerTest(TestCase):
    def setUp(self):
        # Create user type
        self.tenant_type = UserType.objects.create(name='tenant')
        
        self.user = User.objects.create_user(
            username='tenant',
            email='tenant@test.com',
            password='testpass123'
        )
        self.user.add_user_type('tenant')
        self.profile = TenantProfile.objects.create(
            user=self.user,
            preferred_property_type=['apartment', 'house'],
            budget=50000.00,
            preferred_location='Lagos',
            move_in_date='2024-06-01',
            lease_duration=12,
            lease_interval='year'
        )

    def test_tenant_profile_serializer_serialization(self):
        """Test TenantProfileSerializer serialization of existing profile."""
        serializer = TenantProfileSerializer(self.profile)
        data = serializer.data
        self.assertIn('user', data)
        self.assertIn('preferred_property_type', data)
        self.assertIn('budget', data)
        self.assertIn('preferred_location', data)
        self.assertIn('move_in_date', data)
        self.assertIn('lease_duration', data)
        self.assertIn('lease_interval', data)

    def test_tenant_profile_serializer_valid_data(self):
        """Test TenantProfileSerializer with valid data."""
        data = {
            'user': self.user.id,
            'preferred_property_type': ['studio', 'apartment'],
            'budget': 75000.00,
            'preferred_location': 'Abuja',
            'move_in_date': '2099-07-01',  # Use a future date
            'lease_duration': 6,
            'lease_interval': 'month'
        }
        serializer = TenantProfileSerializer(data=data)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())

    def test_tenant_profile_serializer_missing_required_fields(self):
        """Test TenantProfileSerializer with missing required fields."""
        data = {}
        serializer = TenantProfileSerializer(data=data)
        # All fields are optional except user, which is read-only, so should be valid
        self.assertTrue(serializer.is_valid())

    def test_tenant_profile_serializer_invalid_budget(self):
        """Test TenantProfileSerializer with invalid budget."""
        data = {
            'user': self.user.id,
            'budget': -1000.00
        }
        serializer = TenantProfileSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_tenant_profile_serializer_invalid_lease_interval(self):
        """Test TenantProfileSerializer with invalid lease interval."""
        data = {
            'user': self.user.id,
            'lease_interval': 'invalid'
        }
        serializer = TenantProfileSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_tenant_profile_serializer_invalid_preferred_property_type(self):
        """Test TenantProfileSerializer with invalid preferred property type."""
        data = {
            'user': self.user.id,
            'preferred_property_type': 'invalid_type'
        }
        serializer = TenantProfileSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_tenant_profile_serializer_optional_fields(self):
        """Test that optional fields can be null/blank."""
        data = {
            'user': self.user.id,
            'preferred_property_type': [],
            'budget': None,
            'preferred_location': '',
            'move_in_date': None,
            'lease_duration': None,
            'lease_interval': None  # Use None instead of empty string
        }
        serializer = TenantProfileSerializer(data=data)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid()) 