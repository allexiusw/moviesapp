from rest_framework import serializers

from core.models import Movie, MovieImage, Rent


class MovieImageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = MovieImage


class MovieSerializer(serializers.ModelSerializer):
    '''Movie translate models to JSON and perform actions to CRUD op'''
    images = MovieImageSerializer(
        source='movieimage_set', many=True, read_only=True)

    class Meta:
        fields = (
            'id',
            'title',
            'description',
            'stock',
            'rental_price',
            'sale_price',
            'images',
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
