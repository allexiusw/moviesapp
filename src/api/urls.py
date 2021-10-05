from django.urls import path, include
from django.conf.urls import url
from django.conf import settings

from rest_framework.routers import DefaultRouter

from api.views import LogEntryMovieViewSet, MovieViewSet, RentViewSet


swaggerurls = []
if settings.DEBUG:
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    schema_view = get_schema_view(
        openapi.Info(
            title="Snippets API",
            default_version='v1',
            description="Test description",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="contact@snippets.local"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
    )
    swaggerurls = [
        url(
            r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
        url(
            r'^swagger/$',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
        url(
            r'^redoc/$',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
    ]

router = DefaultRouter()
router.register(r'movies', MovieViewSet, basename='movie')
router.register(r'rents', RentViewSet, basename='rent')
router.register(r'sales', RentViewSet, basename='sale')
router.register(
    r'logentrymovies', LogEntryMovieViewSet, basename='logentrymovie')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
] + swaggerurls
