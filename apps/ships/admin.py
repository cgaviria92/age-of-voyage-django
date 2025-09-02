from django.contrib import admin
from .models import ShipType, Ship, ShipUpgrade, ShipCargo, CrewMember


@admin.register(ShipType)
class ShipTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'required_level', 'purchase_cost', 'base_speed', 'base_firepower', 'base_cargo_capacity']
    list_filter = ['required_level']
    search_fields = ['name']


@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'ship_type', 'status', 'hull_health', 'crew_count']
    list_filter = ['ship_type', 'status', 'created_at']
    search_fields = ['name', 'owner__captain_name']
    readonly_fields = ['created_at']


@admin.register(ShipUpgrade)
class ShipUpgradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'upgrade_type', 'bonus_amount', 'cost', 'required_level']
    list_filter = ['upgrade_type', 'required_level']


@admin.register(ShipCargo)
class ShipCargoAdmin(admin.ModelAdmin):
    list_display = ['ship', 'resource', 'quantity']
    list_filter = ['resource']


@admin.register(CrewMember)
class CrewMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'ship', 'crew_type', 'skill_level', 'salary_per_day']
    list_filter = ['crew_type', 'skill_level']
    search_fields = ['name', 'ship__name']
