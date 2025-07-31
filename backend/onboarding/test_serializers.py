from rest_framework.test import APITestCase
from onboarding.serializers import AgentProfileSerializer, TenantProfileSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class SerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

    def test_agent_profile_serializer_valid_data(self):
        """Test AgentProfileSerializer with valid data."""
        data = {
            'user': self.user.id,
            'agency_name': 'New Agency',
            'agency_address': '456 New St',
            'service_areas': ['port harcourt'],
            'service_states': ['lagos'],
            'agency_registration_number': 'REG456'
        }
        serializer = AgentProfileSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(valid)

    def test_tenant_profile_serializer_valid_data(self):
        """Test TenantProfileSerializer with valid data."""
        data = {
            'user': self.user.id,
            'preferred_property_type': ['apartment'],
            'budget': 75000.00,
            'preferred_location': 'abuja',
            'move_in_date': '2024-07-01',
            'lease_duration': 6,
            'lease_interval': 'year'
        }
        serializer = TenantProfileSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(valid)