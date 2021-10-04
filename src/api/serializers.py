from rest_framework import serializers

from core.models import Movie, MovieImage


class MovieImageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'image')
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
