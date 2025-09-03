from django.urls import path
from . import views

app_name = 'guilds'

urlpatterns = [
    path('', views.guild_dashboard, name='guild_dashboard'),
    path('list/', views.guild_list, name='guild_list'),
    path('create/', views.create_guild, name='create_guild'),
    path('<int:guild_id>/', views.guild_detail, name='guild_detail'),
    path('<int:guild_id>/join/', views.join_guild, name='join_guild'),
    path('leave/', views.leave_guild, name='leave_guild'),
    path('invitation/<int:invitation_id>/respond/', views.respond_invitation, name='respond_invitation'),
    path('manage/', views.manage_guild, name='manage_guild'),
]
