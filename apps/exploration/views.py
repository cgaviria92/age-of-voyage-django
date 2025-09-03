from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Region, ExplorationEvent, ExplorationMission, RegionResource
from apps.players.models import Player
from apps.ships.models import Ship


@login_required
def exploration_dashboard(request):
    """Panel principal de exploración."""
    player = get_object_or_404(Player, user=request.user)
    
    # Misiones de exploración activas
    active_missions = ExplorationMission.objects.filter(
        player=player, 
        status='active'
    ).select_related('target_region')
    
    # Eventos de exploración recientes
    recent_events = ExplorationEvent.objects.filter(
        player=player
    ).select_related('region').order_by('-created_at')[:10]
    
    # Regiones descubiertas
    discovered_regions = Region.objects.filter(is_discovered=True)
    
    context = {
        'player': player,
        'active_missions': active_missions,
        'recent_events': recent_events,
        'discovered_regions': discovered_regions,
    }
    return render(request, 'exploration/dashboard.html', context)


@login_required
def regions_list(request):
    """Lista de regiones disponibles para explorar."""
    player = get_object_or_404(Player, user=request.user)
    
    # Todas las regiones
    regions = Region.objects.all().order_by('name')
    
    context = {
        'player': player,
        'regions': regions,
    }
    return render(request, 'exploration/regions.html', context)


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
