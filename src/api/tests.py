# Create your tests here.
from django.urls import reverse
from rest_framework.test import APITestCase


class userTestCase(APITestCase):
    '''Test auth features'''
    user_create_url = reverse('user-list')
    user_activate_url = reverse('user-activation')

    def setUp(self) -> None:
        '''create a new user making a post request to djoser endpoint

        Endpoint tested:
            api/auth/users/ POST
                payload = data
        '''
        self.username = 'foo'
        self.password = 'SuperSecret123'
        self.email = 'test@test.com'
        self.data = {
            'username': self.username,
            'password': self.password,
            'email': self.email,
        }
        response = self.client.post(self.user_create_url, data=self.data)
        self.pk = response.data['id']
