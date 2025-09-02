"""Serializers for missions app."""

from rest_framework import serializers
from .models import Mission, PlayerMission


class MissionSerializer(serializers.ModelSerializer):
    """Serializer for Mission model."""
    
    class Meta:
        model = Mission
        fields = '__all__'


class PlayerMissionSerializer(serializers.ModelSerializer):
    """Serializer for PlayerMission model."""
    
    class Meta:
        model = PlayerMission
        fields = '__all__'