from django_filters import rest_framework as filters
from core.models import Movie


class MovieFilterSet(filters.FilterSet):

    class Meta:
        model = Movie
        fields = ('title', 'availability')
