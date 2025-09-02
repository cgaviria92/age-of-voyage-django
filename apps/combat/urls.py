"""URL configuration for combat app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BattleViewSet

router = DefaultRouter()
router.register(r'battles', BattleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]