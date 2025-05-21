from unittest import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import MagicMock, patch

class AccountManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = MagicMock()
        self.test_user.id = '1'
        self.test_user.email = 'testuser@example.com'
        self.test_user.first_name = 'Test'
        self.test_user.last_name = 'User'
        self.test_user.user_type = 'tenant'
        self.test_user.is_active = True
        self.client.force_authenticate(user=self.test_user)

    @patch('account_management.views.cancel_user_scheduled_deletion')
    @patch('account_management.views.ScheduledDeletion.objects.filter')
    def test_cancel_scheduled_deletion(self, mock_filter, mock_cancel_deletion):
        mock_query_result = MagicMock()
        mock_query_result.exists.return_value = True
        mock_filter.return_value = mock_query_result
        mock_cancel_deletion.return_value = True

        url = reverse('cancel_scheduled_deletion')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        mock_cancel_deletion.assert_called_once_with(self.test_user)

    @patch('account_management.views.schedule_deletion')
    @patch('account_management.views.ScheduledDeletion.objects.filter')
    @patch('account_management.views.send_email')
    def test_schedule_user_deletion(self, mock_send_email, mock_filter, mock_schedule_deletion):
        mock_query_result = MagicMock()
        mock_query_result.exists.return_value = False
        mock_filter.return_value = mock_query_result

        url = reverse('schedule_user_deletion')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        mock_schedule_deletion.assert_called_once_with(self.test_user, deletion_type='user', days=7)
        mock_send_email.assert_called_once()

    @patch('account_management.views.ScheduledDeletion.objects.filter')
    def test_schedule_user_deletion_already_scheduled(self, mock_filter):
        mock_query_result = MagicMock()
        mock_query_result.exists.return_value = True
        mock_filter.return_value = mock_query_result

        url = reverse('schedule_user_deletion')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertIn('error', response.data)

    def test_unauthenticated_access(self):
        unauthenticated_client = APIClient()
        url = reverse('schedule_user_deletion')
        response = unauthenticated_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)