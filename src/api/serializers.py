from rest_framework import serializers

from core.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    '''Movie translate models to JSON and perform actions to CRUD op'''
    class Meta:
        fields = ('id', 'title', 'description')
        model = Movie
