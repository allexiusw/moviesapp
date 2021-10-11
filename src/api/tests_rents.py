from datetime import datetime, timedelta
from django.urls import reverse
from django.contrib.auth.models import User
# from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
# from rest_framework.exceptions import PermissionDenied
# from api.constants import Messages

from core.models import Movie, Rent


class RentTestCase(APITestCase):
    '''Test Rent endpoint'''
    rent_list_url = reverse('rent-list')

    def setUp(self) -> None:
        '''create a new movie'''
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

    def test_list_rents_as_normal_user(self):
        '''List rents as normal user authenticated

        Endpoint tested:
            api/rents/ GET
        '''
        self.authclient = APIClient()
        self.authclient.credentials(
            HTTP_AUTHORIZATION='Token ' + self.tokennotadmin)
        Rent.objects.all().delete()
        movie = Movie.objects.create(**self.movie)
        date_now = datetime.now().date()
        due_date = date_now + timedelta(days=2)
        data = {
            'movie': movie.id,
            'quantity': 2,
            'due_date': due_date.strftime("%d-%m-%Y"),
        }
        self.authclient.post(self.rent_list_url, data=data)
        response = self.authclient.get(self.rent_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
