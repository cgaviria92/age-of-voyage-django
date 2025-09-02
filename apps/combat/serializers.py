"""Serializers for combat app."""

from rest_framework import serializers
from .models import Battle


class BattleSerializer(serializers.ModelSerializer):
    """Serializer for Battle model."""
    
    class Meta:
        model = Battle
        fields = '__all__'