from django.urls import path
from . import views

app_name = 'missions'

urlpatterns = [
    path('', views.mission_board, name='board'),
    path('<int:mission_id>/', views.mission_detail, name='detail'),
    path('accept/<int:mission_id>/', views.accept_mission, name='accept'),
    path('my-missions/', views.my_missions, name='my_missions'),
]
