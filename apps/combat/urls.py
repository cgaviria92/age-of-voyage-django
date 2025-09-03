from django.urls import path
from . import views

app_name = 'combat'

urlpatterns = [
    path('', views.combat_dashboard, name='combat_dashboard'),
    path('fleet/', views.fleet_management, name='fleet_management'),
    path('fleet/create/', views.create_fleet, name='create_fleet'),
    path('attack/', views.attack_player, name='attack_player'),
    path('battle/<int:battle_id>/', views.battle_detail, name='battle_detail'),
    path('battle/<int:battle_id>/resolve/', views.resolve_battle, name='resolve_battle'),
    path('history/', views.combat_history, name='combat_history'),
]
