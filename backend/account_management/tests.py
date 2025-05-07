from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import CustomUser, ScheduledDeletion

class AccountManagementViewsTestCase(TestCase):
    def setUp(self):
        """
        Set up test data and client.
        """
        self.client = APIClient()

        # Ensure the user with the email is deleted first
        CustomUser.objects.filter(email="donfolayan@gmail.com").delete()

        # Create a test user with the required email
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="donfolayan@gmail.com",
            password="password123",
            is_active=True
        )

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # URLs for the views
        self.schedule_user_deletion_url = reverse('schedule_user_deletion')
        self.schedule_inactive_user_deletion_url = reverse('schedule_inactive_user_deletion')
        self.cancel_scheduled_deletion_url = reverse('cancel_scheduled_deletion')

    def test_schedule_user_deletion(self):
        """
        Test scheduling a user deletion.
        """
        response = self.client.post(self.schedule_user_deletion_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ScheduledDeletion.objects.filter(user=self.user, deletion_type='user').exists())
        self.assertEqual(response.data['success'], True)
        self.assertIn('Deletion scheduled successfully', response.data['message'])

    def test_schedule_user_deletion_already_scheduled(self):
        """
        Test scheduling a user deletion when one is already scheduled.
        """
        # Schedule a deletion first
        ScheduledDeletion.objects.create(user=self.user, deletion_type='user', cancelled=False)

        # Try scheduling again
        response = self.client.post(self.schedule_user_deletion_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertIn('Deletion already scheduled', response.data['error'])

    def test_schedule_inactive_user_deletion(self):
        """
        Test scheduling a deletion for an inactive user.
        """
        # Mark the user as inactive
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.schedule_inactive_user_deletion_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ScheduledDeletion.objects.filter(user=self.user, deletion_type='inactive_user').exists())
        self.assertEqual(response.data['success'], True)
        self.assertIn('Deletion scheduled successfully', response.data['message'])

    def test_schedule_inactive_user_deletion_active_user(self):
        """
        Test scheduling a deletion for an active user (should fail).
        """
        response = self.client.post(self.schedule_inactive_user_deletion_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertIn('User is active', response.data['error'])

    def test_cancel_scheduled_deletion(self):
        """
        Test canceling a scheduled deletion.
        """
        # Schedule a deletion first
        ScheduledDeletion.objects.create(user=self.user, deletion_type='user', cancelled=False)

        response = self.client.post(self.cancel_scheduled_deletion_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertIn('Deletion cancelled successfully', response.data['message'])
        self.assertTrue(ScheduledDeletion.objects.filter(user=self.user, deletion_type='user', cancelled=True).exists())

    def test_cancel_scheduled_deletion_no_deletion(self):
        """
        Test canceling a deletion when no deletion is scheduled.
        """
        response = self.client.post(self.cancel_scheduled_deletion_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertIn('No scheduled deletion found', response.data['error'])