from django.urls import path
from . import views

app_name = 'combat'

urlpatterns = [
    path('', views.combat_overview, name='overview'),
    path('battle/<int:battle_id>/', views.battle_detail, name='battle_detail'),
    path('challenge/<int:player_id>/', views.challenge_player, name='challenge'),
    path('pirates/', views.pirate_fleets, name='pirates'),
    path('attack-pirates/<int:fleet_id>/', views.attack_pirates, name='attack_pirates'),
]
