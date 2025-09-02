from django.urls import path
from . import views

app_name = 'ships'

urlpatterns = [
    # Lista y detalle de barcos
    path('', views.ship_list, name='ship_list'),
    path('<int:ship_id>/', views.ship_detail, name='ship_detail'),
    
    # Astillero
    path('shipyard/', views.shipyard, name='shipyard'),
    path('purchase/<int:ship_type_id>/', views.purchase_ship, name='purchase_ship'),
    
    # Mantenimiento y mejoras
    path('<int:ship_id>/repair/', views.repair_ship, name='repair_ship'),
    path('<int:ship_id>/upgrade/', views.upgrade_ship, name='upgrade_ship'),
    
    # Tripulación
    path('<int:ship_id>/hire-crew/', views.hire_crew, name='hire_crew'),
    
    # API
    path('api/<int:ship_id>/status/', views.ship_status_api, name='ship_status_api'),
]
