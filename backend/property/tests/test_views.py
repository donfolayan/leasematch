import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import CustomUser, UserType
from property.models import Property
from property.serializers import PropertySerializer
import json
from datetime import date, timedelta

class PropertyViewsTestCase(TestCase):
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
        
        # Sample property data
        self.property_data = {
            'address': '123 Test St',
            'city': 'Lagos',
            'state': 'lagos',
            'zip_code': '12345',
            'country': 'nigeria',
            'property_type': 'apartment',
            'bedrooms': 2,
            'bathrooms': 1,
            'square_footage': 1000,
            'rent_price': 1000.00,
            'available_from': date.today() + timedelta(days=7),
            'lease_terms': '12 months lease with option to renew'
        }

    def test_add_property_authenticated_landlord(self):
        """Test adding property as authenticated landlord."""
        self.client.force_authenticate(user=self.landlord_user)
        response = self.client.post(reverse('add-property'), self.property_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(Property.objects.count(), 1)

    def test_add_property_authenticated_agent(self):
        """Test adding property as authenticated agent."""
        self.client.force_authenticate(user=self.agent_user)
        response = self.client.post(reverse('add-property'), self.property_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])

    def test_add_property_authenticated_tenant_forbidden(self):
        """Test adding property as tenant should be forbidden."""
        self.client.force_authenticate(user=self.tenant_user)
        response = self.client.post(reverse('add-property'), self.property_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_property_unauthenticated(self):
        """Test adding property without authentication."""
        response = self.client.post(reverse('add-property'), self.property_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_properties_authenticated(self):
        """Test listing properties as authenticated user."""
        # Create a property first
        property = Property.objects.create(
            uploader=self.landlord_user,
            uploader_user_type='landlord',
            **self.property_data
        )
        
        self.client.force_authenticate(user=self.tenant_user)
        response = self.client.get(reverse('list-properties'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('properties', response.data)

    def test_list_properties_unauthenticated(self):
        """Test listing properties without authentication."""
        # Create a property first
        property = Property.objects.create(
            uploader=self.landlord_user,
            uploader_user_type='landlord',
            **self.property_data
        )
        
        response = self.client.get(reverse('list-properties'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('properties', response.data)

    def test_update_property_owner(self):
        """Test updating property by owner."""
        property = Property.objects.create(
            uploader=self.landlord_user,
            uploader_user_type='landlord',
            **self.property_data
        )
        
        self.client.force_authenticate(user=self.landlord_user)
        update_data = {'address': 'Updated Address'}
        response = self.client.patch(
            reverse('update-property', kwargs={'property_id': property.id}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_update_property_non_owner(self):
        """Test updating property by non-owner."""
        property = Property.objects.create(
            uploader=self.landlord_user,
            uploader_user_type='landlord',
            **self.property_data
        )
        
        self.client.force_authenticate(user=self.agent_user)
        update_data = {'address': 'Updated Address'}
        response = self.client.patch(
            reverse('update-property', kwargs={'property_id': property.id}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_property_owner(self):
        """Test getting property by owner."""
        property = Property.objects.create(
            uploader=self.landlord_user,
            uploader_user_type='landlord',
            **self.property_data
        )
        
        self.client.force_authenticate(user=self.landlord_user)
        response = self.client.get(
            reverse('get-property', kwargs={'property_id': property.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('property', response.data)

    def test_get_property_non_owner(self):
        """Test getting property by non-owner."""
        property = Property.objects.create(
            uploader=self.landlord_user,
            uploader_user_type='landlord',
            **self.property_data
        )
        
        self.client.force_authenticate(user=self.agent_user)
        response = self.client.get(
            reverse('get-property', kwargs={'property_id': property.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_property_owner(self):
        """Test deleting property by owner."""
        property = Property.objects.create(
            uploader=self.landlord_user,
            uploader_user_type='landlord',
            **self.property_data
        )
        
        self.client.force_authenticate(user=self.landlord_user)
        response = self.client.delete(
            reverse('delete-property', kwargs={'property_id': property.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Property.objects.count(), 0)

    def test_delete_property_non_owner(self):
        """Test deleting property by non-owner."""
        property = Property.objects.create(
            uploader=self.landlord_user,
            uploader_user_type='landlord',
            **self.property_data
        )
        
        self.client.force_authenticate(user=self.agent_user)
        response = self.client.delete(
            reverse('delete-property', kwargs={'property_id': property.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Property.objects.count(), 1) 