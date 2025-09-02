"""Admin configuration for players app."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Faction, Specialization, Player, PlayerSpecialization, FactionReputation


@admin.register(Faction)
class FactionAdmin(admin.ModelAdmin):
    """Admin for Faction model."""
    list_display = ('name', 'color')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    """Admin for Specialization model."""
    list_display = ('get_name_display', 'name', 'icon')
    search_fields = ('name',)
    list_filter = ('name',)


class PlayerSpecializationInline(admin.TabularInline):
    """Inline for player specializations."""
    model = PlayerSpecialization
    extra = 0


class FactionReputationInline(admin.TabularInline):
    """Inline for faction reputations."""
    model = FactionReputation
    extra = 0


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """Admin for Player model."""
    list_display = ('captain_name', 'user', 'level', 'gold', 'current_region', 'last_active')
    list_filter = ('level', 'current_region', 'created_at')
    search_fields = ('captain_name', 'user__email', 'user__username')
    readonly_fields = ('created_at', 'last_active')
    
    fieldsets = (
        (_('Captain Identity'), {
            'fields': ('user', 'captain_name', 'motto', 'flag_design')
        }),
        (_('Progression'), {
            'fields': ('level', 'experience', 'experience_to_next_level')
        }),
        (_('Resources'), {
            'fields': ('gold', 'wood', 'iron', 'food', 'ammunition', 'spices', 'silk')
        }),
        (_('Location'), {
            'fields': ('current_region',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'last_active')
        })
    )
    
    inlines = [PlayerSpecializationInline, FactionReputationInline]


@admin.register(PlayerSpecialization)
class PlayerSpecializationAdmin(admin.ModelAdmin):
    """Admin for PlayerSpecialization model."""
    list_display = ('player', 'specialization', 'level', 'experience')
    list_filter = ('specialization', 'level')
    search_fields = ('player__captain_name', 'specialization__name')


@admin.register(FactionReputation)
class FactionReputationAdmin(admin.ModelAdmin):
    """Admin for FactionReputation model."""
    list_display = ('player', 'faction', 'reputation', 'reputation_status')
    list_filter = ('faction', 'reputation')
    search_fields = ('player__captain_name', 'faction__name')
    
    def reputation_status(self, obj):
        return obj.reputation_status
    reputation_status.short_description = 'Status'
