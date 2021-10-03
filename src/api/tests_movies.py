# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


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

    def test_list_movies(self):
        '''List movies without authorization token

        Endpoint tested:
            api/movies/ GET
        '''
        response = self.client.get(self.user_create_url, data={})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [])
