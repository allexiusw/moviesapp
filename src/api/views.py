# Create your views here.
from rest_framework import viewsets
from api.serializers import MovieSerializer
from core.models import Movie


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()
