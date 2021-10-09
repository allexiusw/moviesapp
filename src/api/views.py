from datetime import datetime
from decimal import Decimal
from django.conf import settings

from django.contrib.admin.models import LogEntry

from rest_framework import viewsets, status, permissions
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

import stripe

from core.models import Movie, Rent, Sale
from api.filters import MovieFilterSet
from api.serializers import (
    LogEntryMovieSerializer,
    MovieImageSerializer,
    MovieSerializer,
    RentSerializer,
    SaleSerializer,
)
from api.constants import Messages


class MovieViewSet(viewsets.ModelViewSet):
    '''Define the HTTP endpoint against the serializer mapping CRUD
        operations to HTTP verbs, (Create -> POST, Update -> PATCH ...)
    '''
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()
    filter_class = MovieFilterSet

    def get_queryset(self):
        queryset = super().get_queryset()
        # Ensure other user not admin user will show only available movies
        if not self.request.user.is_superuser:
            queryset = queryset.filter(availability=True)
        return queryset

    def create(self, request, *args, **kwargs):
        ''''Perform create and take care of validation when no images

        Be carefull here, we create the MovieImage dict list
        data = [{'image': i} for i in request.FILES.getlist('images')]
        If is valid to our serializer we can save after save the movie
        else we return HTTP_400_BAD_REQUEST

        Return:
            Response object
        '''
        data = [{'image': i} for i in request.FILES.getlist('images')]
        many = len(data) > 0
        serializer = MovieImageSerializer(data=data, many=many)
        if not serializer.is_valid():
            headers = self.get_success_headers(serializer.data)
            data = Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST,
                headers=headers)
        else:
            # Save Movie before, we need the id to relate with all MovieImage
            data = super().create(request, *args, **kwargs)
            serializer.save(movie_id=data.data.get('id'))
        return data

    @action(detail=True, methods=['patch'])
    def set_available(self, request, pk=None):
        '''Change availability in movie to True

        Endpoint api/movies/<:pk>/set_available/
        return: Message.MOVIE_AVAILABLE -> str
        '''
        movie = self.get_object()
        movie.availability = True
        movie.save()
        return Response({'message': Messages.MOVIE_AVAILABLE})

    @action(detail=True, methods=['patch'])
    def set_unavailable(self, request, pk=None):
        '''Change movie to unavailable

        Endpoint api/movies/<:pk>/set_unavailable/
        return: Message.MOVIE_UNAVAILABLE -> str
        '''
        movie = self.get_object()
        movie.availability = False
        movie.save()
        return Response({'message': Messages.MOVIE_UNAVAILABLE})

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rent_it(self, request, pk=None):
        '''Allow any user logged in rent a movie that has stock

        Endpoint api/movies/rent-it/<:pk>/
            quantity: N
        return:
            Message.RENT_SUCCESSFULLY -> str (HTTP 200)
                And return the session.id
            Json with validated data (HTTP 400)
        '''
        movie = self.get_object()
        serializer = RentSerializer(data={
            'movie': movie.id,
            'due_date': request.data['due_date'],
            'quantity': request.data['quantity'],
            'rented_by': request.user.id,
        })
        if serializer.is_valid(raise_exception=True):
            rent = serializer.save()
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.create(
                # Not use reverse here 'cause we don't care about UI
                # in this project.
                success_url=f'{settings.YOUR_SERVER}success/',
                cancel_url=f'{settings.YOUR_SERVER}cancel/',
                payment_method_types=["card"],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(rent.amount * 100),
                        'product_data': {'name': rent.movie.title}
                    },
                    "quantity": 1,
                }], mode="payment")
            response = Response({
                    'message': Messages.RENT_SUCCESSFULLY,
                    'session_id': session.id,
                    'rent': serializer.data,
                }, status=status.HTTP_201_CREATED)
        else:
            response = Response({
                    'data': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        return response

    @action(
        detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def buy_it(self, request, pk=None):
        '''Allow any user logged in buy a movie that has stock

        Endpoint api/movies/buy-it/<:pk>/
            quantity: N
        return:
            Message.MOVIE_BUYED -> str (HTTP 200)
            Message.MOVIE_WITHOUT_STOCK (HTTP 400)
        '''
        movie = self.get_object()
        serializer = SaleSerializer(data={
            'movie': movie.id,
            'amount': movie.sale_price * Decimal(request.data['quantity']),
            'quantity': request.data['quantity'],
            'buyed_by': request.user.id,
            'user': request.user.id,
            'date': datetime.now()
        })
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {'message': Messages.MOVIE_BUYED}, status=status.HTTP_200_OK)
        return Response(
            {'data': serializer.data}, status=status.HTTP_400_BAD_REQUEST)


class RentViewSet(viewsets.ModelViewSet):
    '''Define the HTTP endpoint against the serializer mapping CRUD
        operations to HTTP verbs, (Create -> POST, Update -> PATCH ...)
    '''
    serializer_class = RentSerializer
    queryset = Rent.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        '''Filter data by user if not superadmin'''
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(rented_by=self.request.user)
        return queryset


class LogEntryMovieViewSet(ListModelMixin, viewsets.GenericViewSet):
    '''Define the HTTP endpoint against the serializer mapping CRUD
        operations to HTTP verbs, (Create -> POST, Update -> PATCH ...)
    '''
    serializer_class = LogEntryMovieSerializer
    permission_classes = (permissions.IsAdminUser,)
    queryset = LogEntry.objects.filter(content_type__model='movie')


class SaleViewSet(viewsets.ModelViewSet):
    '''Define the HTTP endpoint against the serializer mapping CRUD
        operations to HTTP verbs, (Create -> POST, Update -> PATCH ...)
    '''
    serializer_class = SaleSerializer
    queryset = Sale.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        '''Filter data by user if not superadmin'''
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(rented_by=self.request.user)
        return queryset
