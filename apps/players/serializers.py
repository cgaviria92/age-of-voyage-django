"""Serializers for players app."""

from rest_framework import serializers
from .models import Player, Faction, Specialization, PlayerSpecialization, FactionReputation


class FactionSerializer(serializers.ModelSerializer):
    """Serializer for Faction model."""
    
    class Meta:
        model = Faction
        fields = ['id', 'name', 'description', 'color', 'emblem']


class SpecializationSerializer(serializers.ModelSerializer):
    """Serializer for Specialization model."""
    
    class Meta:
        model = Specialization
        fields = ['id', 'name', 'description', 'icon']


class PlayerSpecializationSerializer(serializers.ModelSerializer):
    """Serializer for PlayerSpecialization model."""
    
    specialization = SpecializationSerializer(read_only=True)
    
    class Meta:
        model = PlayerSpecialization
        fields = ['specialization', 'level', 'experience']


class FactionReputationSerializer(serializers.ModelSerializer):
    """Serializer for FactionReputation model."""
    
    faction = FactionSerializer(read_only=True)
    reputation_status = serializers.CharField(read_only=True)
    
    class Meta:
        model = FactionReputation
        fields = ['faction', 'reputation', 'reputation_status']


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for Player model."""
    
    specializations = PlayerSpecializationSerializer(many=True, read_only=True)
    faction_reputations = FactionReputationSerializer(many=True, read_only=True)
    total_resources = serializers.DictField(read_only=True)
    display_name = serializers.CharField(source='user.display_name', read_only=True)
    
    class Meta:
        model = Player
        fields = [
            'id', 'captain_name', 'motto', 'flag_design', 'level', 'experience',
            'experience_to_next_level', 'gold', 'wood', 'iron', 'food', 'ammunition',
            'spices', 'silk', 'current_region', 'created_at', 'last_active',
            'specializations', 'faction_reputations', 'total_resources', 'display_name'
        ]
        read_only_fields = ['id', 'experience', 'level', 'created_at', 'last_active']