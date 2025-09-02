from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'players'

urlpatterns = [
    # Página principal
    path('', views.home, name='home'),
    
    # Dashboard y perfil
    path('dashboard/', views.player_dashboard, name='dashboard'),
    path('profile/', views.player_profile, name='profile'),
    path('profile/<int:player_id>/', views.player_profile, name='profile_view'),
    
    # Registro y autenticación
    path('register/', views.register_player, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='players:home'), name='logout'),
    
    # Funcionalidades sociales
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('search/', views.search_players, name='search'),
    path('settings/', views.player_settings, name='settings'),
]
