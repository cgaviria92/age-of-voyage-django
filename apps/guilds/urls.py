from django.urls import path
from . import views

app_name = 'guilds'

urlpatterns = [
    path('', views.guild_list, name='list'),
    path('create/', views.create_guild, name='create'),
    path('<int:guild_id>/', views.guild_detail, name='detail'),
    path('<int:guild_id>/join/', views.join_guild, name='join'),
    path('<int:guild_id>/leave/', views.leave_guild, name='leave'),
]
