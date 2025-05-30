from .test_setup import TestSetup

class TestViews(TestSetup):

    def test_user_cannot_register_with_not_provided_data(self):
        res=self.client.post(self.register_url, {}, format='json')
        self.assertEqual(res.status_code, 400)
    
    # def test_user_can_register(self):
    #     self.client.post(self.register_url, self.user_data, format='json')