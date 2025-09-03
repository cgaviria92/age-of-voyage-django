from django.contrib import admin
from .models import Expedition, Discovery, ExplorationMap


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ['player', 'ship', 'destination', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['player__user__username', 'destination']
    readonly_fields = ['created_at']


@admin.register(Discovery)
class DiscoveryAdmin(admin.ModelAdmin):
    list_display = ['player', 'discovery_type', 'name', 'discovered_at']
    list_filter = ['discovery_type', 'discovered_at']
    search_fields = ['player__user__username', 'name']
    readonly_fields = ['discovered_at']


@admin.register(ExplorationMap)
class ExplorationMapAdmin(admin.ModelAdmin):
    list_display = ['player', 'created_at']
    search_fields = ['player__user__username']
    readonly_fields = ['created_at']
