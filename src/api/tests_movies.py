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
        user_normal = User.objects.create(
            username='notadmin',
            password='SuperSecret',
            is_active=True,
        )
        self.token = str(Token.objects.create(user=user))
        self.tokennotadmin = str(Token.objects.create(user=user_normal))

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

    def test_create_movie_as_normaluser_one_images(self):
        '''Test create images as a normal user should not be saved.

        It uses the user's token to perform actions as a normal user.
        The API return HTTP_201_CREATED as required and
        create Movie and MovieImage instances related.

        Endpoint tested:
            api/movies/ POST
                payload = self.movie -> dict
        '''
        self.authclient = APIClient()
        self.authclient.credentials(
            HTTP_AUTHORIZATION='Token ' + self.tokennotadmin)
        with open(f'{settings.STATIC_ROOT}/test.png', 'rb') as file:
            self.movie['images'] = [file]
            response = self.authclient.post(
                self.user_create_url, self.movie, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            'You do not have permission to perform this action.')

    def test_list_movies(self):
        '''List movies without authorization token

        Endpoint tested:
            api/movies/ GET
        '''
        Movie.objects.all().delete()
        response = self.client.get(self.user_create_url, data={})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [])

    def test_update_movie_as_admin(self):
        '''Test update movie as an admin.

        It uses the user's token to perform actions as an admin.
        The API return HTTP_200_OK and create Movie instance related.

        Endpoint tested:
            api/movies/ PUT
                payload = self.movie -> dict
        '''
        self.authclient = APIClient()
        self.authclient.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        movie = Movie.objects.create(
            **self.movie
        )
        with open(f'{settings.STATIC_ROOT}/test.png', 'rb') as file:
            self.movie['images'] = [file]
            self.movie['title'] = 'Other title'
            user_update_url = reverse('movie-detail', args=[movie.id])
            response = self.authclient.put(
                user_update_url, data=self.movie, format="multipart")
        movie = Movie.objects.first()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(movie.title, self.movie['title'])

    def test_delete_movie_as_admin(self):
        '''Test delete movie as an admin.

        It uses the user's token to perform actions as an admin.
        The API return HTTP_200_OK and create Movie instance related.

        Endpoint tested:
            api/movies/1/ DELETE
        '''
        self.authclient = APIClient()
        self.authclient.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        movie = Movie.objects.create(
            **self.movie
        )
        user_update_url = reverse('movie-detail', args=[movie.id])
        response = self.authclient.delete(user_update_url)
        movie = Movie.objects.filter(pk=movie.id)
        self.assertFalse(movie.exists())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
