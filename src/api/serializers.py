from datetime import datetime

from django.contrib.admin.models import LogEntry, ACTION_FLAG_CHOICES

from rest_framework import serializers
from api.constants import Messages

from core.models import Movie, MovieImage, Rent, Sale


class MovieImageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'image']
        model = MovieImage


class MovieSerializer(serializers.ModelSerializer):
    '''Movie translate models to JSON and perform actions to CRUD op'''
    images = MovieImageSerializer(
        source='movieimage_set', many=True, read_only=True)
    quantity = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        fields = (
            'id',
            'title',
            'description',
            'stock',
            'rental_price',
            'sale_price',
            'availability',
            'images',
            'quantity',
        )
        model = Movie


class RentSerializer(serializers.ModelSerializer):
    '''Rent translate models to JSON and perform actions to CRUD op
    User will use it to perform CRUD action in database and map this
    actions to HTTP verbs.
    '''
    amount = serializers.IntegerField(required=False)
    due_date = serializers.DateField()

    class Meta:
        fields = (
            'id',
            'rented_by',
            'created_at',
            'due_date',
            'movie',
            'quantity',
            'returned',
            'returned_at',
            'extra_charge',
            'amount',
        )
        model = Rent

    def validate(self, attrs):
        '''Check if quantity is enough to rent'''
        quantity = attrs['quantity']
        if not quantity > 0:
            raise serializers.ValidationError(
                {'quantity': Messages.RENT_QUANTITY_LOW})
        if not quantity <= attrs['movie'].stock:
            raise serializers.ValidationError(
                {'quantity': Messages.RENT_QUANTITY_NOT_AVAI})
        date_now = datetime.now().date()
        if attrs['due_date'] <= date_now:
            raise serializers.ValidationError(
                {'due_date': Messages.DUE_DATE_TOO_LONG})
        days = (attrs['due_date'] - date_now).days
        attrs['amount'] = quantity * attrs['movie'].rental_price * days
        return attrs


class LogEntryMovieSerializer(serializers.ModelSerializer):
    '''Rent translate models to JSON and perform history view of
    actions that any user has done.
    '''
    title = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    rental_price = serializers.SerializerMethodField()
    sale_price = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = [
            'action_time',
            'action_flag',
            'action',
            'username',
            'title',
            'rental_price',
            'sale_price',
        ]

    def get_username(self, obj):
        return obj.user.username

    def get_title(self, obj):
        return obj.get_edited_object().title

    def get_rental_price(self, obj):
        return obj.get_edited_object().rental_price

    def get_sale_price(self, obj):
        return obj.get_edited_object().sale_price

    def get_action(self, obj):
        return dict(ACTION_FLAG_CHOICES).get(obj.action_flag)


class SaleSerializer(serializers.ModelSerializer):
    '''Sale translate models to JSON and perform actions to CRUD op
    User will use it to perform CRUD action in database and map this
    actions to HTTP verbs.
    '''
    buyed_by = serializers.SerializerMethodField(
        read_only=True, required=False)
    quantity = serializers.IntegerField(
        write_only=True, required=False)

    class Meta:
        fields = [
            'movie',
            'user',
            'buyed_by',
            'created_at',
            'date',
            'amount',
            'quantity',
        ]
        model = Sale

    def validate(self, attrs):
        '''Check if quantity is enough to sale'''
        quantity = attrs['quantity']
        if not quantity > 0:
            raise serializers.ValidationError(
                {'message': Messages.RENT_QUANTITY_LOW})
        if not quantity <= attrs['movie'].stock:
            raise serializers.ValidationError(
                {'message': Messages.RENT_QUANTITY_NOT_AVAI})
        del attrs['quantity']
        return attrs

    def get_buyed_by(self, obj):
        return obj.user.username
