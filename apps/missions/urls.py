from django.urls import path
from . import views

app_name = 'missions'

urlpatterns = [
    path('', views.missions_dashboard, name='missions_dashboard'),
    path('<int:mission_id>/', views.mission_detail, name='mission_detail'),
    path('<int:mission_id>/start/', views.start_mission, name='start_mission'),
    path('progress/<int:progress_id>/', views.mission_progress, name='mission_progress'),
    path('progress/<int:progress_id>/update/', views.update_mission_progress, name='update_mission_progress'),
    path('progress/<int:progress_id>/abandon/', views.abandon_mission, name='abandon_mission'),
    path('progress/<int:progress_id>/claim/', views.claim_reward, name='claim_reward'),
    path('daily/', views.daily_missions, name='daily_missions'),
    path('categories/', views.mission_categories, name='mission_categories'),
]
