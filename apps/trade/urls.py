from django.urls import path
from . import views

app_name = 'trade'

urlpatterns = [
    path('', views.trade_dashboard, name='trade_dashboard'),
    path('posts/', views.trade_posts, name='trade_posts'),
    path('routes/create/', views.create_trade_route, name='create_trade_route'),
    path('routes/<int:route_id>/', views.trade_route_detail, name='trade_route_detail'),
    path('routes/<int:route_id>/complete/', views.complete_trade, name='complete_trade'),
    path('history/', views.trade_history, name='trade_history'),
]
