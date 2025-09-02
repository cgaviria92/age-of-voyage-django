from django.contrib import admin
from .models import Player, PlayerAchievement, PlayerSettings


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['captain_name', 'level', 'gold', 'reputation', 'total_battles_won', 'regions_discovered']
    list_filter = ['reputation', 'level', 'created_at']
    search_fields = ['captain_name', 'user__username']
    readonly_fields = ['created_at', 'last_active']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'captain_name', 'level', 'experience', 'gold', 'reputation')
        }),
        ('Estadísticas', {
            'fields': ('total_battles_won', 'total_battles_lost', 'total_trade_profit', 'regions_discovered')
        }),
        ('Habilidades', {
            'fields': ('navigation_skill', 'combat_skill', 'trade_skill', 'leadership_skill', 'diplomacy_skill')
        }),
        ('Fechas', {
            'fields': ('created_at', 'last_active'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(admin.ModelAdmin):
    list_display = ['player', 'name', 'achievement_type', 'earned_at', 'gold_reward']
    list_filter = ['achievement_type', 'earned_at']
    search_fields = ['player__captain_name', 'name']


@admin.register(PlayerSettings)
class PlayerSettingsAdmin(admin.ModelAdmin):
    list_display = ['player', 'notifications_enabled', 'auto_repair_ships', 'preferred_language']
    list_filter = ['notifications_enabled', 'auto_repair_ships', 'preferred_language']
