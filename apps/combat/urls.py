from django.urls import path
from . import views

app_name = 'combat'

urlpatterns = [
    path('', views.combat_arena, name='arena'),
    path('challenge-npc/', views.challenge_npc, name='challenge_npc'),
    path('battle/<int:battle_id>/', views.battle_detail, name='battle_detail'),
    path('battle/<int:battle_id>/attack/', views.execute_attack, name='execute_attack'),
]
