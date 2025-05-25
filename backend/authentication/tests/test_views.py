from .test_setup import TestSetup
from unittest.mock import patch

class TestViews(TestSetup):

    def test_user_cannot_register_with_not_provided_data(self):
        res=self.client.post(self.register_url, {}, format='json')
        self.assertEqual(res.status_code, 400)
    
    def test_user_can_register(self):
        res=self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(res.status_code, 201)

    def test_user_cannot_register_with_invalid_email(self):
        invalid_user_data = self.user_data.copy()
        invalid_user_data['email'] = 'invalid_email'
        res=self.client.post(self.register_url, invalid_user_data, format='json')
        self.assertEqual(res.status_code, 400)

    def test_user_cannot_register_with_existing_email(self):
        self.client.post(self.register_url, self.user_data, format='json')
        res=self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(res.status_code, 400)

    @patch('authentication.views.cache.get')
    def test_user_can_verify_otp(self, mock_cache_get):

        def side_effect(key, default=None):
            if 'otp' in str(key).lower():
                return '123456'
            return default
        mock_cache_get.side_effect = side_effect
      
        user=self.client.post(self.register_url, {
            "email": "test2@test.test",
            "username": "user2",
            "password": "password",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "tenant",
        }, format='json')

        user_id = str(user.data['user_id'])

        res=self.client.post(self.verify_otp_url, {
            "user_id": user_id,
            "otp": "123456"
        }, format='json')
        # import pdb
        # pdb.set_trace()
        self.assertEqual(res.status_code, 200)

    def test_user_cannot_verify_otp_with_invalid_user_id(self):
        res=self.client.post(self.verify_otp_url, {
            "user_id": "8bedfb98-4d7b-44a0-92c2-62dd8bfc993b",
            "otp": "123456"
        }, format='json')
        self.assertEqual(res.status_code, 400)
    
    @patch('authentication.views.cache.get')
    def test_user_cannot_verify_otp_with_invalid_otp(self, mock_cache_get):
        def side_effect(key, default=None):
            if 'otp' in str(key).lower():
                return '123456'
            return default
        mock_cache_get.side_effect = side_effect
      
        user=self.client.post(self.register_url, {
            "email": "test2@test.test",
            "username": "user2",
            "password": "password",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "tenant",
        }, format='json')

        user_id = str(user.data['user_id'])

        res=self.client.post(self.verify_otp_url, {
            "user_id": user_id,
            "otp": "123457"
        }, format='json')
        # import pdb
        # pdb.set_trace()
        self.assertEqual(res.status_code, 400)

    def test_user_can_resend_otp(self):
        user=self.client.post(self.register_url, {
            "email": "test2@test.test",
            "username": "user2",
            "password": "password",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "tenant",
        }, format='json')

        user_id = str(user.data['user_id'])

        res=self.client.post(self.resend_otp_url, {
            "user_id": user_id
        }, format='json')

        self.assertEqual(res.status_code, 200)
    
    def test_user_cannot_resend_otp_with_invalid_user_id(self):
        res=self.client.post(self.resend_otp_url, {
            "user_id": "8bedfb98-4d7b-44a0-92c2-62dd8bfc993b"
        }, format='json')
        self.assertEqual(res.status_code, 400)

    def test_user_can_use_forgot_password(self):
        user=self.client.post(self.register_url, {
            "email": "test4@test.test",
            "username": "user2",
            "password": "password",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "tenant",
        }, format='json')

        res=self.client.post(self.forgot_password_url, {
            "email": "test4@test.test"
        }, format='json')

        self.assertEqual(res.status_code, 200)
    
    def test_user_cannot_use_forgot_password_with_invalid_email(self):
        
        res=self.client.post(self.forgot_password_url, {
            "email": "test10@test.test"
        }, format='json')

        self.assertEqual(res.status_code, 400)

    