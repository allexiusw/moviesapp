from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.http import HttpResponse
from django.contrib.admin.models import LogEntry
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string

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
            return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST,
                headers=headers)
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
                # It is the Rent pk to meet session_id with rent
                client_reference_id=rent.id,
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(rent.amount * 100),
                        'product_data': {'name': rent.movie.title}
                    },
                    "quantity": 1,
                }], mode="payment")
            rent.payment_reference = session.payment_intent
            rent.payment_url = session.url
            rent.save()
            return Response({
                    'message': Messages.RENT_SUCCESSFULLY,
                    'session_id': session.id,
                    'session_url': session.url,
                    'rent': serializer.data,
                }, status=status.HTTP_201_CREATED)
        return Response({
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(rented_by=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(
        detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def return_movie(self, request, pk=None):
        '''Allow any user return his movies and generate extrapayment if needed

        Endpoint api/rents/return-movie/<:pk>/

        return:
            Message.MOVIE_RETURNED -> str (HTTP 200)
            Message.EXTRA_PAYMENT_GENERATED (HTTP 201)
        '''
        rent = self.get_object()
        if rent.due_date < datetime.now().date():
            return Response(
                {'message': "Extra charges"}, status=status.HTTP_201_CREATED)
        return Response(
            {'data': "Returned"}, status=status.HTTP_200_OK)


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


@csrf_exempt
def stripe_webhook(request):
    '''It listen payment updates comming from Stripe'''
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print(e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(e)
        return HttpResponse(status=400)

    # Handle succeeded charge
    if event['type'] == 'charge.succeeded':
        session = event['data']['object']
        id = session['payment_intent']
        rent = Rent.objects.filter(payment_reference=id).first()
        send_to = [settings.EMAIL_ADMINISTRATOR]
        title = 'Payment succesfully but not found invoice.'
        if rent is not None:
            send_to.append(rent.rented_by.email)
            title = f'Payment successfully: {rent.movie.title}'
            rent.is_paid = True
            rent.paid_at = datetime.now()
            rent.save()
            context = {'movie': rent.movie, 'rent': rent}
            template_txt = 'email/invoice_email.txt'
            template_html = 'email/invoice_email.html'
        else:
            template_txt = 'email/invoice_notfound.txt'
            template_html = 'email/invoice_notfound.html'
            context = {'id': id}
        msg_plain = render_to_string(template_txt, context=context)
        msg_html = render_to_string(template_html, context=context)
        send_mail(
            title,
            msg_plain,
            settings.DEFAULT_FROM_EMAIL,
            send_to,
            html_message=msg_html)
    return HttpResponse(status=200)
