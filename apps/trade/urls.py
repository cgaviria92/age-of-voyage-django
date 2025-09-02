"""URL configuration for trade app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CommodityViewSet, MarketViewSet

router = DefaultRouter()
router.register(r'commodities', CommodityViewSet)
router.register(r'markets', MarketViewSet)

urlpatterns = [
    path('', include(router.urls)),
]