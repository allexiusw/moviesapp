from django.contrib.admin.models import LogEntry, ACTION_FLAG_CHOICES

from rest_framework import serializers
from api.constants import Messages

from core.models import Movie, MovieImage, Rent


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
        quantity = attrs['quantity']
        if not quantity > 0:
            raise serializers.ValidationError(
                {'message': Messages.RENT_QUANTITY_LOW})
        if not quantity <= attrs['movie'].stock:
            raise serializers.ValidationError(
                {'message': Messages.RENT_QUANTITY_NOT_AVAI})
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
