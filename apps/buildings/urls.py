from django.urls import path
from . import views

app_name = 'buildings'

urlpatterns = [
    path('', views.buildings_overview, name='overview'),
    path('build/<int:region_id>/', views.build_structure, name='build'),
    path('manage/<int:building_id>/', views.manage_building, name='manage'),
]
