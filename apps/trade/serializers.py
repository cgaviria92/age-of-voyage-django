"""Serializers for trade app."""

from rest_framework import serializers
from .models import Commodity, Market


class CommoditySerializer(serializers.ModelSerializer):
    """Serializer for Commodity model."""
    
    class Meta:
        model = Commodity
        fields = '__all__'


class MarketSerializer(serializers.ModelSerializer):
    """Serializer for Market model."""
    
    class Meta:
        model = Market
        fields = '__all__'