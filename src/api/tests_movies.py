# Create your tests here.
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from core.models import Movie


class MovieTestCase(APITestCase):
    '''Test Movie endpoint'''
    user_create_url = reverse('movie-list')

    def setUp(self) -> None:
        '''create a new user making a post request to djoser endpoint'''
        self.movie = {
            'title': 'Demo movie',
            'description': 'Demo movie 123',
            'stock': 20,
            'rental_price': 0.5,
            'sale_price': 40,
        }
        user = User.objects.create(
            username='allex',
            password='SuperSecret',
            is_superuser=True,
            is_active=True,
        )
        self.token = str(Token.objects.create(user=user))

    def test_create_movie_as_admin_any_images(self):
        '''Test create images as an admin without at least one image should fail.

        It uses the user's token to perform actions as an admin.
        The API return HTTP_400_BAD_REQUEST because (images field missing)

        Endpoint tested:
            api/movies/ POST
        '''
        self.authclient = APIClient()
        self.authclient.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.authclient.post(
            self.user_create_url, self.movie, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_movie_as_admin_one_images(self):
        '''Test create images as an admin with one image should be saved.

        It uses the user's token to perform actions as an admin.
        The API return HTTP_201_CREATED as required and
        create Movie and MovieImage instances related.

        Endpoint tested:
            api/movies/ POST
                payload = self.movie -> dict
        '''
        self.authclient = APIClient()
        self.authclient.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        with open(f'{settings.STATIC_ROOT}/test.png', 'rb') as file:
            self.movie['images'] = [file]
            response = self.authclient.post(
                self.user_create_url, self.movie, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_movies(self):
        '''List movies without authorization token

        Endpoint tested:
            api/movies/ GET
        '''
        Movie.objects.all().delete()
        response = self.client.get(self.user_create_url, data={})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [])
