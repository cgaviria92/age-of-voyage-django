from django.urls import path
from . import views

app_name = 'exploration'

urlpatterns = [
    path('', views.exploration_map, name='map'),
    path('select-ship/<int:ship_id>/', views.select_ship, name='select_ship'),
    path('start/', views.start_exploration, name='start_exploration'),
    path('missions/', views.exploration_missions, name='missions'),
]
