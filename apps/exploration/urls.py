"""URL configuration for exploration app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegionViewSet, WorldRegionViewSet

router = DefaultRouter()
router.register(r'regions', RegionViewSet)
router.register(r'world-regions', WorldRegionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]