from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import random
from .models import Region, ExplorationEvent, ExplorationMission, RegionResource
from apps.players.models import Player
from apps.ships.models import Ship


@login_required
def exploration_map(request):
    """Mapa de exploración con selección de barcos y regiones."""
    player = get_object_or_404(Player, user=request.user)
    
    # Barcos disponibles (idle)
    available_ships = Ship.objects.filter(owner=player, status='idle')
    
    # Barco seleccionado (desde sesión o None)
    selected_ship_id = request.session.get('selected_ship_id')
    selected_ship = None
    if selected_ship_id:
        try:
            selected_ship = Ship.objects.get(id=selected_ship_id, owner=player, status='idle')
        except Ship.DoesNotExist:
            request.session.pop('selected_ship_id', None)
    
    # Todas las regiones
    regions = Region.objects.all().order_by('required_level', 'name')
    
    # Estadísticas de exploración
    exploration_stats = {
        'successful_missions': ExplorationMission.objects.filter(player=player, status='completed').count(),
        'treasures_found': player.regions_discovered,  # placeholder
        'battles_won': player.total_battles_won,
    }
    
    context = {
        'player': player,
        'available_ships': available_ships,
        'selected_ship': selected_ship,
        'regions': regions,
        'exploration_stats': exploration_stats,
    }
    return render(request, 'exploration/map.html', context)


@login_required
def select_ship(request, ship_id):
    """Seleccionar barco para exploración."""
    player = get_object_or_404(Player, user=request.user)
    ship = get_object_or_404(Ship, id=ship_id, owner=player, status='idle')
    
    request.session['selected_ship_id'] = ship.id
    messages.success(request, f'Barco "{ship.name}" seleccionado para exploración.')
    return redirect('exploration:map')


@login_required
def start_exploration(request):
    """Iniciar una misión de exploración."""
    if request.method != 'POST':
        return redirect('exploration:map')
    
    player = get_object_or_404(Player, user=request.user)
    
    region_id = request.POST.get('region_id')
    ship_id = request.POST.get('ship_id')
    exploration_type = request.POST.get('exploration_type', 'normal')
    
    if not region_id or not ship_id:
        messages.error(request, 'Datos incompletos.')
        return redirect('exploration:map')
    
    region = get_object_or_404(Region, id=region_id)
    ship = get_object_or_404(Ship, id=ship_id, owner=player, status='idle')
    
    # Verificaciones
    if player.level < region.required_level:
        messages.error(request, f'Necesitas nivel {region.required_level} para explorar esta región.')
        return redirect('exploration:map')
    
    if ship.health < ship.ship_type.max_health * 0.3:
        messages.error(request, 'El barco necesita reparación antes de explorar.')
        return redirect('exploration:map')
    
    # Determinar duración según tipo de exploración
    duration_map = {
        'quick': 30,
        'normal': 60,
        'thorough': 120
    }
    duration_minutes = duration_map.get(exploration_type, 60)
    
    # Crear misión de exploración
    mission = ExplorationMission.objects.create(
        player=player,
        ship=ship,
        target_region=region,
        exploration_type=exploration_type,
        status='active',
        started_at=timezone.now(),
        estimated_completion=timezone.now() + timedelta(minutes=duration_minutes)
    )
    
    # Cambiar estado del barco
    ship.status = 'exploring'
    ship.save()
    
    # Limpiar selección de barco
    request.session.pop('selected_ship_id', None)
    
    messages.success(request, f'¡Exploración de "{region.name}" iniciada! Tu barco regresará en {duration_minutes} minutos.')
    return redirect('exploration:missions')


@login_required
def exploration_missions(request):
    """Lista de misiones de exploración."""
    player = get_object_or_404(Player, user=request.user)
    
    # Misiones activas
    active_missions = ExplorationMission.objects.filter(
        player=player, 
        status='active'
    ).select_related('target_region', 'ship').order_by('estimated_completion')
    
    # Misiones completadas recientes
    completed_missions = ExplorationMission.objects.filter(
        player=player, 
        status__in=['completed', 'failed']
    ).select_related('target_region', 'ship').order_by('-completed_at')[:10]
    
    context = {
        'player': player,
        'active_missions': active_missions,
        'completed_missions': completed_missions,
    }
    return render(request, 'exploration/missions.html', context)


@login_required
def start_exploration_mission(request):
    """Iniciar una nueva misión de exploración."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        ship_id = request.POST.get('ship_id')
        region_id = request.POST.get('region_id')
        
        if not ship_id or not region_id:
            messages.error(request, 'Debes seleccionar un barco y una región.')
            return redirect('exploration:dashboard')
        
        try:
            ship = Ship.objects.get(id=ship_id, player=player)
            region = Region.objects.get(id=region_id)
            
            # Verificar si el barco está disponible
            if ship.status != 'available':
                messages.error(request, 'El barco no está disponible para explorar.')
                return redirect('exploration:dashboard')
            
            # Crear misión de exploración
            mission = ExplorationMission.objects.create(
                player=player,
                ship=ship,
                target_region=region,
                status='active'
            )
            
            # Actualizar estado del barco
            ship.status = 'exploring'
            ship.save()
            
            messages.success(request, f'¡Misión de exploración iniciada hacia {region.name}!')
            
        except (Ship.DoesNotExist, Region.DoesNotExist):
            messages.error(request, 'Barco o región no encontrada.')
        
        return redirect('exploration:dashboard')
    
    # GET request - mostrar formulario
    player = get_object_or_404(Player, user=request.user)
    available_ships = Ship.objects.filter(player=player, status='available')
    available_regions = Region.objects.all()
    
    context = {
        'player': player,
        'available_ships': available_ships,
        'available_regions': available_regions,
    }
    return render(request, 'exploration/start_mission.html', context)


@login_required
def mission_detail(request, mission_id):
    """Ver detalles de una misión de exploración."""
    player = get_object_or_404(Player, user=request.user)
    mission = get_object_or_404(ExplorationMission, id=mission_id, player=player)
    
    context = {
        'player': player,
        'mission': mission,
    }
    return render(request, 'exploration/mission_detail.html', context)


@login_required
def complete_mission(request, mission_id):
    """Completar una misión de exploración."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        mission = get_object_or_404(ExplorationMission, id=mission_id, player=player)
        
        if mission.status != 'active':
            messages.error(request, 'Esta misión no puede ser completada.')
            return redirect('exploration:dashboard')
        
        # Completar misión
        mission.status = 'completed'
        mission.save()
        
        # Devolver barco
        mission.ship.status = 'available'
        mission.ship.save()
        
        # Crear evento de exploración
        ExplorationEvent.objects.create(
            player=player,
            region=mission.target_region,
            event_type='mission_completed',
            description=f'Misión de exploración completada en {mission.target_region.name}'
        )
        
        # Otorgar recompensas (simulado)
        experience_reward = 100
        player.experience += experience_reward
        player.save()
        
        messages.success(request, f'¡Misión completada! Ganaste {experience_reward} XP.')
        
        return redirect('exploration:dashboard')
    
    return redirect('exploration:dashboard')


@login_required
def region_detail(request, region_id):
    """Ver detalles de una región."""
    player = get_object_or_404(Player, user=request.user)
    region = get_object_or_404(Region, id=region_id)
    
    # Recursos de la región
    resources = RegionResource.objects.filter(region=region)
    
    # Eventos en esta región
    events = ExplorationEvent.objects.filter(
        region=region, 
        player=player
    ).order_by('-created_at')
    
    context = {
        'player': player,
        'region': region,
        'resources': resources,
        'events': events,
    }
    return render(request, 'exploration/region_detail.html', context)


@login_required
def exploration_events(request):
    """Lista de eventos de exploración del jugador."""
    player = get_object_or_404(Player, user=request.user)
    events = ExplorationEvent.objects.filter(player=player).order_by('-created_at')
    
    context = {
        'player': player,
        'events': events,
    }
    return render(request, 'exploration/events.html', context)
