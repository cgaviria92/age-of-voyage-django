"""URL configuration for missions app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MissionViewSet, PlayerMissionViewSet

router = DefaultRouter()
router.register(r'player-missions', PlayerMissionViewSet)
router.register(r'', MissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]