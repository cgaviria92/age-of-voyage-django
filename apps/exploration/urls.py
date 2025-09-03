from django.urls import path
from . import views

app_name = 'exploration'

urlpatterns = [
    path('', views.exploration_dashboard, name='exploration_dashboard'),
    path('regions/', views.regions_list, name='regions_list'),
    path('region/<int:region_id>/', views.region_detail, name='region_detail'),
    path('start-mission/', views.start_exploration_mission, name='start_exploration_mission'),
    path('mission/<int:mission_id>/', views.mission_detail, name='mission_detail'),
    path('mission/<int:mission_id>/complete/', views.complete_mission, name='complete_mission'),
    path('events/', views.exploration_events, name='exploration_events'),
]
