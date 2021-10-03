# Create your tests here.
import uuid
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from djoser.conf import User
from djoser.utils import encode_uid


class UserTestCase(APITestCase):
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
        self.credentials = {
            'username': self.username,
            'password': self.password,
        }
        data = self.credentials.copy()
        data['email'] = 'test@test.com'
        response = self.client.post(self.user_create_url, data=data)
        # Be careful here, we saved the user pk to test user-detail endpoint
        self.pk = response.data['id']

    def test_create_user_without_username(self):
        '''Not create user without username and password

        Endpoint tested:
            api/auth/users/ POST
                payload = data
        '''
        data = {}
        response = self.client.post(self.user_create_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_user(self):
        '''Activate the created user using the api set is_active=True

        Endpoint tested:
            api/auth/users/activation/ POST
                payload = data
        '''
        user = User.objects.get(username=self.username)

        # UID and Tokenconfirmation are sent to the email address
        # In this case we get this data in this way because is test env.
        self.uid = encode_uid(user.pk)
        self.tokenconfirm = default_token_generator.make_token(user)

        data = {
            'uid': self.uid,
            'token': self.tokenconfirm,
        }
        response = self.client.post(self.user_activate_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_activate_user_invalid_token(self):
        '''Activate the created user using the api set is_active=True

        Endpoint tested:
            api/auth/users/activation/ POST
                payload = data
        '''

        # UID and Tokenconfirmation are sent to the email address
        # In this case we get this data in this way because is test env.

        data = {
            'uid': uuid.uuid4,
            'token': uuid.uuid4,
        }
        response = self.client.post(self.user_activate_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user(self):
        '''Do login user and get the token authentication

        Endpoint tested:
            api/auth/token/login/ POST
                payload = data

        Return:
            token: str
                Saved in self.token to be used in Authorization headers
        '''

        self.test_activate_user()
        response = self.client.post(reverse('login'), data=self.credentials)
        # Be careful here, we save the token.
        self.token = response.data['auth_token']
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_created_user(self):
        '''Ensure new user is created and test using user-detail

        Endpoint tested:
            api/auth/users/<pk>/ GET
                payload = pk
        '''

        self.test_login_user()
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(reverse('user-detail', args=[self.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
