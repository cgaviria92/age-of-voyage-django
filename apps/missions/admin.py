# from django.contrib import admin
# from .models import Mission, PlayerMission

# Temporarily disabled to fix admin errors


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'mission_type', 'difficulty', 'required_level', 'is_active']
    list_filter = ['mission_type', 'difficulty', 'required_level', 'is_active']
    search_fields = ['title', 'description']


@admin.register(PlayerMission)
class PlayerMissionAdmin(admin.ModelAdmin):
    list_display = ['player', 'mission', 'status', 'progress', 'started_at']
    list_filter = ['status', 'started_at', 'completed_at']
    search_fields = ['player__user__username', 'mission__title']
    readonly_fields = ['started_at', 'completed_at']
