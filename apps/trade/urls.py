from django.urls import path
from . import views

app_name = 'trade'

urlpatterns = [
    path('', views.trade_hub, name='trade_hub'),
    path('market/<int:region_id>/', views.market_view, name='market'),
    path('routes/', views.trade_routes, name='routes'),
    path('missions/', views.trade_missions, name='missions'),
    path('start-mission/', views.start_trade_mission, name='start_mission'),
]
