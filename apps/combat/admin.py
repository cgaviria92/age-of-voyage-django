from django.contrib import admin
from .models import Battle, Fleet, CombatReport


@admin.register(Battle)
class BattleAdmin(admin.ModelAdmin):
    list_display = ['attacker', 'defender', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['attacker__user__username', 'defender__user__username']
    readonly_fields = ['created_at']


@admin.register(Fleet)
class FleetAdmin(admin.ModelAdmin):
    list_display = ['player', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['player__user__username', 'name']
    readonly_fields = ['created_at']
    filter_horizontal = ['ships']


@admin.register(CombatReport)
class CombatReportAdmin(admin.ModelAdmin):
    list_display = ['attacker', 'defender', 'winner', 'loot_gold', 'created_at']
    list_filter = ['created_at']
    search_fields = ['attacker__user__username', 'defender__user__username', 'winner__user__username']
    readonly_fields = ['created_at']
