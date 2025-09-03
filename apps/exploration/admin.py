from django.contrib import admin
from .models import Region, ExplorationEvent, ExplorationMission, RegionResource


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'region_type', 'danger_level', 'is_discovered']
    list_filter = ['region_type', 'danger_level', 'is_discovered']
    search_fields = ['name', 'description']


@admin.register(ExplorationEvent)
class ExplorationEventAdmin(admin.ModelAdmin):
    list_display = ['player', 'region', 'event_type', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['player__user__username', 'region__name']
    readonly_fields = ['created_at']


@admin.register(ExplorationMission)
class ExplorationMissionAdmin(admin.ModelAdmin):
    list_display = ['player', 'target_region', 'status', 'started_at']
    list_filter = ['status', 'started_at']
    search_fields = ['player__user__username', 'target_region__name']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(RegionResource)
class RegionResourceAdmin(admin.ModelAdmin):
    list_display = ['region', 'resource_type', 'quantity', 'is_renewable']
    list_filter = ['resource_type', 'is_renewable']
    search_fields = ['region__name', 'resource_type']
