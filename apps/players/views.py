from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Player, PlayerAchievement
from apps.ships.models import Ship
from apps.exploration.models import Region


def home(request):
    """Página principal del juego"""
    if request.user.is_authenticated:
        return redirect('players:dashboard')
    
    context = {
        'total_players': Player.objects.count(),
        'total_regions': Region.objects.count(),
        'total_ships': Ship.objects.count(),
    }
    return render(request, 'players/home.html', context)


@login_required
def player_dashboard(request):
    """Dashboard principal del jugador"""
    player = get_object_or_404(Player, user=request.user)
    
    # Obtener estadísticas del jugador
    player_ships = Ship.objects.filter(owner=player)
    recent_achievements = PlayerAchievement.objects.filter(player=player).order_by('-earned_at')[:5]
    
    context = {
        'player': player,
        'player_ships': player_ships,
        'recent_achievements': recent_achievements,
        'ship_count': player_ships.count(),
    }
    return render(request, 'players/dashboard.html', context)


@login_required
def player_profile(request, player_id=None):
    """Perfil del jugador (propio o de otro)"""
    if player_id:
        player = get_object_or_404(Player, id=player_id)
    else:
        player = get_object_or_404(Player, user=request.user)
    
    achievements = PlayerAchievement.objects.filter(player=player).order_by('-earned_at')
    ships = Ship.objects.filter(owner=player)
    
    context = {
        'profile_player': player,
        'achievements': achievements,
        'ships': ships,
        'is_own_profile': request.user == player.user,
    }
    return render(request, 'players/profile.html', context)


@login_required
def leaderboard(request):
    """Tabla de clasificaciones"""
    # Top jugadores por nivel y experiencia
    top_players = Player.objects.order_by('-level', '-experience')[:50]
    
    # Top por diferentes categorías
    top_combat = Player.objects.order_by('-total_battles_won')[:10]
    top_trade = Player.objects.order_by('-total_trade_profit')[:10]
    top_exploration = Player.objects.order_by('-regions_discovered')[:10]
    
    context = {
        'top_players': top_players,
        'top_combat': top_combat,
        'top_trade': top_trade,
        'top_exploration': top_exploration,
    }
    return render(request, 'players/leaderboard.html', context)


def register_player(request):
    """Registro de nuevo jugador"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        captain_name = request.POST.get('captain_name')
        
        if form.is_valid() and captain_name:
            # Verificar que el nombre de capitán no esté en uso
            if Player.objects.filter(captain_name=captain_name).exists():
                messages.error(request, 'Este nombre de capitán ya está en uso.')
                return render(request, 'registration/register.html', {'form': form})
            
            user = form.save()
            
            # Crear perfil de jugador
            player = Player.objects.create(
                user=user,
                captain_name=captain_name,
                gold=1000,  # Oro inicial
            )
            
            # Autenticar y hacer login
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'¡Bienvenido a Age of Voyage, Capitán {captain_name}!')
                return redirect('player_dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def search_players(request):
    """Búsqueda de jugadores"""
    query = request.GET.get('q', '')
    players = []
    
    if query:
        players = Player.objects.filter(
            Q(captain_name__icontains=query) | 
            Q(user__username__icontains=query)
        ).order_by('-level')[:20]
    
    if request.is_ajax():
        data = [{
            'id': player.id,
            'captain_name': player.captain_name,
            'level': player.level,
            'reputation': player.get_reputation_display(),
        } for player in players]
        return JsonResponse({'players': data})
    
    context = {
        'players': players,
        'query': query,
    }
    return render(request, 'players/search.html', context)


@login_required
def player_settings(request):
    """Configuraciones del jugador"""
    player = get_object_or_404(Player, user=request.user)
    
    if request.method == 'POST':
        # Actualizar configuraciones
        settings = player.settings
        settings.notifications_enabled = request.POST.get('notifications_enabled') == 'on'
        settings.auto_repair_ships = request.POST.get('auto_repair_ships') == 'on'
        settings.music_enabled = request.POST.get('music_enabled') == 'on'
        settings.sound_effects_enabled = request.POST.get('sound_effects_enabled') == 'on'
        settings.save()
        
        messages.success(request, 'Configuración actualizada correctamente.')
        return redirect('player_settings')
    
    context = {
        'player': player,
    }
    return render(request, 'players/settings.html', context)
