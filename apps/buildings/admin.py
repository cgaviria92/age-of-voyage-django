from django.contrib import admin
from .models import BuildingType, PlayerBuilding

@admin.register(BuildingType)
class BuildingTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'build_cost', 'required_level']
    list_filter = ['category', 'required_level']

@admin.register(PlayerBuilding)
class PlayerBuildingAdmin(admin.ModelAdmin):
    list_display = ['building_type', 'owner', 'region', 'status', 'level']
    list_filter = ['status', 'building_type', 'level']
