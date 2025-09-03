from django.contrib import admin
from .models import Guild, GuildMember, GuildInvitation, GuildEvent


@admin.register(Guild)
class GuildAdmin(admin.ModelAdmin):
    list_display = ['name', 'leader', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'leader__user__username']
    readonly_fields = ['created_at']


@admin.register(GuildMember)
class GuildMemberAdmin(admin.ModelAdmin):
    list_display = ['player', 'guild', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['player__user__username', 'guild__name']
    readonly_fields = ['joined_at']


@admin.register(GuildInvitation)
class GuildInvitationAdmin(admin.ModelAdmin):
    list_display = ['guild', 'invited_player', 'invited_by', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['guild__name', 'invited_player__user__username', 'invited_by__user__username']
    readonly_fields = ['created_at']


@admin.register(GuildEvent)
class GuildEventAdmin(admin.ModelAdmin):
    list_display = ['guild', 'event_type', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['guild__name', 'description']
    readonly_fields = ['created_at']
