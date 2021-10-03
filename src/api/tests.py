# Create your tests here.
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class userProfileTestCase(APITestCase):
    '''Test auth features'''
    user_create = reverse('user-list')

    def setUp(self) -> None:
        # create a new user making a post request to djoser endpoint
        self.username = 'foo'
        self.password = 'SuperSecret123'
        self.data = {
            'username': self.username,
            'password': self.password,
        }

    def test_create_user(self):
        '''Ensure new user is created'''
        response = self.client.post(self.user_create, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
