from django.urls import path
from . import views

app_name = 'exploration'

urlpatterns = [
    path('', views.world_map, name='world_map'),
    path('region/<int:region_id>/', views.region_detail, name='region_detail'),
    path('explore/<int:region_id>/', views.start_exploration, name='start_exploration'),
    path('missions/', views.exploration_missions, name='missions'),
]
