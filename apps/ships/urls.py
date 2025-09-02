"""URL configuration for ships app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ShipViewSet, ShipTypeViewSet

router = DefaultRouter()
router.register(r'types', ShipTypeViewSet)
router.register(r'', ShipViewSet)

urlpatterns = [
    path('', include(router.urls)),
]