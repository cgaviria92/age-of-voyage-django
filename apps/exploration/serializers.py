"""Serializers for exploration app."""

from rest_framework import serializers
from .models import Region, WorldRegion


class WorldRegionSerializer(serializers.ModelSerializer):
    """Serializer for WorldRegion model."""
    
    class Meta:
        model = WorldRegion
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    """Serializer for Region model."""
    
    world_region_details = WorldRegionSerializer(source='world_region', read_only=True)
    coordinates = serializers.ReadOnlyField()
    danger_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = Region
        fields = '__all__'