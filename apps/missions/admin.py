from django.contrib import admin
from .models import Mission, MissionProgress, MissionReward


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'mission_type', 'category', 'required_level', 'is_active', 'created_at']
    list_filter = ['mission_type', 'category', 'is_active', 'required_level', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']


@admin.register(MissionProgress)
class MissionProgressAdmin(admin.ModelAdmin):
    list_display = ['player', 'mission', 'current_progress', 'is_completed', 'started_at']
    list_filter = ['is_completed', 'started_at', 'completed_at']
    search_fields = ['player__user__username', 'mission__title']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(MissionReward)
class MissionRewardAdmin(admin.ModelAdmin):
    list_display = ['mission', 'reward_type', 'amount']
    list_filter = ['reward_type']
    search_fields = ['mission__title', 'reward_type']
