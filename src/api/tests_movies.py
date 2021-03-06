# Create your tests here.
from datetime import datetime, timedelta
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from api.constants import Messages

from core.models import Movie


class MovieTestCase(APITestCase):
    '''Test Movie endpoint'''
    user_create_url = reverse('movie-list')

    def setUp(self) -> None:
        '''create a new user making a post request to djoser endpoint
        And 2 user normal and superadmin.
        '''
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
        self.normal_user = User.objects.create(
            username='notadmin',
            password='SuperSecret',
            is_active=True,
            email='william.al1379@gmail.com',
        )
        self.token = str(Token.objects.create(user=user))
        self.tokennotadmin = str(Token.objects.create(
            user=self.normal_user))

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
            response.data['detail'], PermissionDenied.default_detail)

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
        movie = Movie.objects.create(**self.movie)
        with open(f'{settings.STATIC_ROOT}/test.png', 'rb') as file:
            self.movie['images'] = [file]
            self.movie['title'] = 'Other title'
            user_update_url = reverse('movie-detail', args=[movie.id])
            response = self.authclient.put(
                user_update_url, data=self.movie, format="multipart")
        movie = Movie.objects.first()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(movie.title, self.movie['title'])

    def test_set_movie_unavailable_as_admin(self):
        '''Test movie set as unavailable as admin.

        Endpoint tested:
            api/movies/<:id>/set_unavailable/ PATCH

        Return:
            Messages.MOVIE_UNAVAILABLE -> str
        '''
        self.authclient = APIClient()
        self.authclient.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # By default movies has availability=True
        movie = Movie.objects.create(**self.movie)
        movie_url = reverse('movie-set-unavailable', args=[movie.id])
        response = self.authclient.patch(movie_url, data=self.movie)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('message'), Messages.MOVIE_UNAVAILABLE)

    def test_set_movie_unavailable_as_normaluser(self):
        '''Test movie set as unavailable normal user should fail.

        Endpoint tested:
            api/movies/<:id>/set_unavailable/ PATCH

        Return:
            Messages.MOVIE_UNAVAILABLE -> str
        '''
        movie = Movie.objects.create(**self.movie)
        movie_url = reverse('movie-set-unavailable', args=[movie.id])
        response = self.client.patch(movie_url, data=self.movie)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_set_movie_available_as_admin(self):
        '''Test movie set as available as admin should be success.

        Endpoint tested:
            api/movies/<:id>/set_available/ PATCH

        Return:
            Messages.MOVIE_AVAILABLE -> str
        '''
        self.authclient = APIClient()
        self.authclient.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        movie_unavailabe = {**self.movie, **{'availability': False}}
        movie = Movie.objects.create(**movie_unavailabe)
        movie_url = reverse('movie-set-available', args=[movie.id])
        response = self.authclient.patch(movie_url, data=self.movie)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('message'), Messages.MOVIE_AVAILABLE)

    def test_set_movie_available_as_normaluser(self):
        '''Test movie set as available normal user should fail.

        Endpoint tested:
            api/movies/<:id>/set_available/ PATCH

        Return:
            Messages.MOVIE_AVAILABLE -> str
        '''
        movie_unavailabe = {**self.movie, **{'availability': False}}
        movie = Movie.objects.create(**movie_unavailabe)
        movie_url = reverse('movie-set-available', args=[movie.id])
        response = self.client.patch(movie_url, data=self.movie)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_movie_as_admin(self):
        '''Test delete movie as an admin.

        It uses the user's token to perform actions as an admin.
        The API return HTTP_200_OK and create Movie instance related.

        Endpoint tested:
            api/movies/1/ DELETE
        '''
        self.authclient = APIClient()
        self.authclient.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        movie = Movie.objects.create(**self.movie)
        user_update_url = reverse('movie-detail', args=[movie.id])
        response = self.authclient.delete(user_update_url)
        movie = Movie.objects.filter(pk=movie.id)
        self.assertFalse(movie.exists())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_rent_available_movie_as_anonymous(self):
        '''Test rent a movie as anonymous user.

        Endpoint tested:
            api/movies/<:id>/rent-it/ PATCH

        Return:
            Messages.HTTP_401_UNAUTHORIZED -> str
        '''
        movie = {**self.movie, **{'availability': True}}
        movie = Movie.objects.create(**movie)
        movie_url = reverse('movie-rent-it', args=[movie.id])
        response = self.client.post(movie_url, data=self.movie)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rent_available_movie_as_normaluser(self):
        '''Test rent an availabe movie as normal user, should succed.

        Endpoint tested:
            api/movies/<:id>/rent_it/ POST

        Return:
            Messages.RENT_SUCCESSFULLY -> str
        '''
        self.authclient = APIClient()
        self.authclient.credentials(
            HTTP_AUTHORIZATION='Token ' + self.tokennotadmin)
        movie = Movie.objects.create(**self.movie)
        rent_url = reverse('movie-rent-it', args=[movie.id])
        date_now = datetime.now().date()
        due_date = date_now + timedelta(days=2)
        data = {
            'quantity': 2,
            'due_date': due_date.strftime("%d-%m-%Y"),
            'rented_by': self.normal_user,
        }
        response = self.authclient.post(rent_url, data=data)
        days = (due_date - datetime.now().date()).days
        movie = Movie.objects.get(pk=movie.id)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], Messages.RENT_SUCCESSFULLY)
        self.assertEqual(
            movie.rent_set.first().amount,
            data['quantity'] * movie.rental_price * days
        )

    def test_like_movie(self):
        '''Test like movie as normal user authenticated.

        Endpoint tested:
            api/movies/<:id>/like/ POST

        Return:
            response -> HTTP
        '''
        self.authclient = APIClient()
        self.authclient.credentials(
            HTTP_AUTHORIZATION='Token ' + self.tokennotadmin)
        movie = Movie.objects.create(**self.movie)
        movie_url = reverse('movie-like', args=[movie.id])
        response = self.authclient.patch(movie_url)
        movie.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(movie.likes.count(), 1)
