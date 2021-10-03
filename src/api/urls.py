from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import MovieViewSet


router = DefaultRouter()
router.register(r'movies', MovieViewSet, basename='movie')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
