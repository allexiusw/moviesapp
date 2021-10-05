# Create your views here.
from django.contrib.admin.models import LogEntry
from rest_framework import viewsets, status, permissions
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action

from core.models import Movie, Rent
from api.serializers import (
    LogEntryMovieSerializer,
    MovieImageSerializer,
    MovieSerializer,
    RentSerializer,
)

from api.constants import Messages


class MovieViewSet(viewsets.ModelViewSet):
    '''Define the HTTP endpoint against the serializer mapping CRUD
        operations to HTTP verbs, (Create -> POST, Update -> PATCH ...)
    '''
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()

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
            data = Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST,
                headers=headers)
        else:
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


class RentViewSet(viewsets.ModelViewSet):
    '''Define the HTTP endpoint against the serializer mapping CRUD
        operations to HTTP verbs, (Create -> POST, Update -> PATCH ...)
    '''
    serializer_class = RentSerializer
    queryset = Rent.objects.all()


class LogEntryMovieViewSet(ListModelMixin, viewsets.GenericViewSet):
    '''Define the HTTP endpoint against the serializer mapping CRUD
        operations to HTTP verbs, (Create -> POST, Update -> PATCH ...)
    '''
    serializer_class = LogEntryMovieSerializer
    permission_classes = (permissions.IsAdminUser,)
    queryset = LogEntry.objects.filter(content_type__model='movie')
