from django.contrib import admin
from .models import Guild, GuildMembership


@admin.register(Guild)
class GuildAdmin(admin.ModelAdmin):
    list_display = ['name', 'founder', 'level', 'member_count', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['name', 'founder__user__username']
    readonly_fields = ['created_at']


@admin.register(GuildMembership)
class GuildMembershipAdmin(admin.ModelAdmin):
    list_display = ['player', 'guild', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['player__user__username', 'guild__name']
    readonly_fields = ['joined_at']
