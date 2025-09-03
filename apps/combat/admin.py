# from django.contrib import admin
# from .models import Battle, CombatTurn, PirateFleet

# Temporarily disabled to fix admin errors, CombatEvent


@admin.register(Battle)
class BattleAdmin(admin.ModelAdmin):
    list_display = ['player', 'enemy_fleet', 'status', 'result', 'created_at']
    list_filter = ['status', 'result', 'created_at']
    search_fields = ['player__user__username']
    readonly_fields = ['created_at', 'ended_at']


@admin.register(CombatTurn)
class CombatTurnAdmin(admin.ModelAdmin):
    list_display = ['battle', 'turn_number', 'attacker_ship', 'defender_ship', 'damage_dealt']
    list_filter = ['turn_number']
    search_fields = ['battle__player__user__username']


@admin.register(PirateFleet)
class PirateFleetAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'threat_level', 'is_active']
    list_filter = ['threat_level', 'is_active']
    search_fields = ['name', 'region__name']


@admin.register(CombatEvent)
class CombatEventAdmin(admin.ModelAdmin):
    list_display = ['player', 'region', 'event_type', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['player__user__username', 'region__name']
    readonly_fields = ['created_at']
