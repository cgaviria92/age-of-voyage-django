from django.urls import path
from . import views

app_name = 'combat'

urlpatterns = [
    path('', views.combat_dashboard, name='dashboard'),
    path('pirate-hunt/', views.pirate_hunt, name='pirate_hunt'),
    path('start-pirate-battle/', views.start_pirate_battle, name='start_pirate_battle'),
    path('battle/<int:battle_id>/', views.battle_detail, name='battle_detail'),
    path('battle/<int:battle_id>/action/', views.combat_action, name='combat_action'),
    path('history/', views.battle_history, name='battle_history'),
]
