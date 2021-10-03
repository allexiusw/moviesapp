# Create your views here.
from rest_framework import viewsets
from api.serializers import MovieSerializer
from core.models import Movie


class MovieViewSet(viewsets.ModelViewSet):
    '''Define the HTTP endpoint against the serializer mapping CRUD
        operations to HTTP verbs, (Create -> POST, Update -> PATCH ...)
    '''
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()
