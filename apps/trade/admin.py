from django.contrib import admin
from .models import TradeRoute, TradePost, TradeTransaction


@admin.register(TradeRoute)
class TradeRouteAdmin(admin.ModelAdmin):
    list_display = ['player', 'ship', 'origin', 'destination', 'cargo_type', 'is_active', 'created_at']
    list_filter = ['is_active', 'cargo_type', 'created_at']
    search_fields = ['player__user__username', 'cargo_type']
    readonly_fields = ['created_at']


@admin.register(TradePost)
class TradePostAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'trade_bonus', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'location']


@admin.register(TradeTransaction)
class TradeTransactionAdmin(admin.ModelAdmin):
    list_display = ['player', 'trade_route', 'cargo_type', 'quantity', 'profit', 'created_at']
    list_filter = ['cargo_type', 'created_at']
    search_fields = ['player__user__username', 'cargo_type']
    readonly_fields = ['created_at']
