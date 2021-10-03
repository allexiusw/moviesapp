from rest_framework import serializers


class MovieSerializer(serializers.ModelSerializer):
    '''Movie translate models to JSON and perform actions to CRUD op'''
    class Meta:
        fields = ('id', 'title', 'description')
