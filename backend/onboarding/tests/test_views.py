import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import CustomUser, UserType
from onboarding.models import AgentProfile, LandlordProfile, TenantProfile
from onboarding.serializers import AgentProfileSerializer, LandlordProfileSerializer, TenantProfileSerializer

class OnboardingViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create user types
        self.tenant_type = UserType.objects.create(name='tenant')
        self.landlord_type = UserType.objects.create(name='landlord')
        self.agent_type = UserType.objects.create(name='agent')
        
        # Create users
        self.tenant_user = CustomUser.objects.create_user(
            username='tenant@test.com',
            email='tenant@test.com',
            password='testpass123'
        )
        self.tenant_user.add_user_type('tenant')
        
        self.landlord_user = CustomUser.objects.create_user(
            username='landlord@test.com',
            email='landlord@test.com',
            password='testpass123'
        )
        self.landlord_user.add_user_type('landlord')
        
        self.agent_user = CustomUser.objects.create_user(
            username='agent@test.com',
            email='agent@test.com',
            password='testpass123'
        )
        self.agent_user.add_user_type('agent')
        
        # Create profiles with correct fields
        self.tenant_profile = TenantProfile.objects.create(
            user=self.tenant_user,
            budget=1000.00,
            lease_interval='year',
            preferred_location='Lagos',
            move_in_date='2024-01-01'
        )
        
        self.landlord_profile = LandlordProfile.objects.create(
            user=self.landlord_user
        )
        
        self.agent_profile = AgentProfile.objects.create(
            user=self.agent_user,
            agency_name='Test Agency',
            agency_address='456 Agency St',
            service_areas=['Lagos', 'Abuja'],
            service_states=['Lagos', 'FCT'],
            agency_registration_number='REG123'
        )

    def test_update_agent_profile_authenticated_agent(self):
        """Test updating agent profile as authenticated agent."""
        self.client.force_authenticate(user=self.agent_user)
        data = {'agency_name': 'Updated Agency'}
        response = self.client.post(reverse('update_agent_profile'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_update_agent_profile_authenticated_non_agent(self):
        """Test updating agent profile as non-agent should be forbidden."""
        self.client.force_authenticate(user=self.landlord_user)
        data = {'agency_name': 'Updated Agency'}
        response = self.client.post(reverse('update_agent_profile'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_agent_profile_unauthenticated(self):
        """Test updating agent profile without authentication."""
        data = {'agency_name': 'Updated Agency'}
        response = self.client.post(reverse('update_agent_profile'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_landlord_profile_authenticated_landlord(self):
        """Test updating landlord profile as authenticated landlord."""
        self.client.force_authenticate(user=self.landlord_user)
        data = {'documents': 'test_document.pdf'}
        response = self.client.post(reverse('update_landlord_profile'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_update_landlord_profile_authenticated_non_landlord(self):
        """Test updating landlord profile as non-landlord should be forbidden."""
        self.client.force_authenticate(user=self.agent_user)
        data = {'documents': 'test_document.pdf'}
        response = self.client.post(reverse('update_landlord_profile'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_tenant_profile_authenticated_tenant(self):
        """Test updating tenant profile as authenticated tenant."""
        self.client.force_authenticate(user=self.tenant_user)
        data = {'budget': 1500.00}
        response = self.client.post(reverse('update_tenant_profile'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_update_tenant_profile_authenticated_non_tenant(self):
        """Test updating tenant profile as non-tenant should be forbidden."""
        self.client.force_authenticate(user=self.landlord_user)
        data = {'budget': 1500.00}
        response = self.client.post(reverse('update_tenant_profile'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_onboarding_status_authenticated(self):
        """Test getting onboarding status as authenticated user."""
        self.client.force_authenticate(user=self.tenant_user)
        response = self.client.get(reverse('get_onboarding_status'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_type', response.data)
        self.assertIn('current_step', response.data)
        self.assertIn('next_action', response.data)

    def test_get_onboarding_status_unauthenticated(self):
        """Test getting onboarding status without authentication."""
        response = self.client.get(reverse('get_onboarding_status'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_onboarding_step_authenticated(self):
        """Test updating onboarding step as authenticated user."""
        self.client.force_authenticate(user=self.tenant_user)
        data = {'next_step': 2}
        response = self.client.put(reverse('update_onboarding_step'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_update_onboarding_step_missing_data(self):
        """Test updating onboarding step with missing data."""
        self.client.force_authenticate(user=self.tenant_user)
        response = self.client.put(reverse('update_onboarding_step'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complete_onboarding_authenticated(self):
        """Test completing onboarding as authenticated user."""
        # Set user to final step for tenant (step 2)
        self.tenant_user.onboarding_step = 2
        self.tenant_user.save()
        
        self.client.force_authenticate(user=self.tenant_user)
        response = self.client.post(reverse('complete_onboarding'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_complete_onboarding_incomplete(self):
        """Test completing onboarding when not on final step."""
        self.client.force_authenticate(user=self.tenant_user)
        response = self.client.post(reverse('complete_onboarding'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_skip_onboarding_authenticated(self):
        """Test skipping onboarding as authenticated user."""
        self.client.force_authenticate(user=self.tenant_user)
        response = self.client.post(reverse('skip_onboarding'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success']) 