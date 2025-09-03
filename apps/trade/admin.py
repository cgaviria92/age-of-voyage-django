from django.contrib import admin
from .models import Resource, TradeRoute, TradeMission, TradeMissionCargo, Market, PriceHistory


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_price', 'rarity']
    list_filter = ['category', 'rarity']
    search_fields = ['name', 'description']


@admin.register(TradeRoute)
class TradeRouteAdmin(admin.ModelAdmin):
    list_display = ['player', 'ship', 'origin_region', 'destination_region', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['player__user__username']
    readonly_fields = ['created_at']


@admin.register(TradeMission)
class TradeMissionAdmin(admin.ModelAdmin):
    list_display = ['player', 'trade_route', 'status', 'started_at']
    list_filter = ['status', 'started_at']
    search_fields = ['player__user__username']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ['region', 'is_active']
    list_filter = ['is_active']
    search_fields = ['region__name']


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['market', 'resource', 'price', 'recorded_at']
    list_filter = ['recorded_at']
    search_fields = ['market__region__name', 'resource__name']
    readonly_fields = ['recorded_at']
