"""Serializers for ships app."""

from rest_framework import serializers
from .models import Ship, ShipType


class ShipTypeSerializer(serializers.ModelSerializer):
    """Serializer for ShipType model."""
    
    class Meta:
        model = ShipType
        fields = '__all__'


class ShipSerializer(serializers.ModelSerializer):
    """Serializer for Ship model."""
    
    ship_type_details = ShipTypeSerializer(source='ship_type', read_only=True)
    health_percentage = serializers.ReadOnlyField()
    cargo_space_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = Ship
        fields = '__all__'
        read_only_fields = ['owner', 'acquired_at', 'last_maintenance']