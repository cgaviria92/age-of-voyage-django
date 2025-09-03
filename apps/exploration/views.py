from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Expedition, Discovery, ExplorationMap
from apps.players.models import Player
from apps.ships.models import Ship


@login_required
def exploration_dashboard(request):
    """Panel principal de exploración."""
    player = get_object_or_404(Player, user=request.user)
    expeditions = Expedition.objects.filter(player=player).order_by('-created_at')
    discoveries = Discovery.objects.filter(player=player).order_by('-discovered_at')
    
    context = {
        'player': player,
        'expeditions': expeditions,
        'discoveries': discoveries,
    }
    return render(request, 'exploration/dashboard.html', context)


@login_required
def start_expedition(request):
    """Iniciar una nueva expedición."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        ship_id = request.POST.get('ship_id')
        destination = request.POST.get('destination')
        
        if not ship_id or not destination:
            messages.error(request, 'Debes seleccionar un barco y destino.')
            return redirect('exploration:dashboard')
        
        try:
            ship = Ship.objects.get(id=ship_id, player=player)
            
            # Verificar si el barco está disponible
            if ship.status != 'docked':
                messages.error(request, 'El barco no está disponible para explorar.')
                return redirect('exploration:dashboard')
            
            # Crear expedición
            expedition = Expedition.objects.create(
                player=player,
                ship=ship,
                destination=destination,
                status='active'
            )
            
            # Actualizar estado del barco
            ship.status = 'exploring'
            ship.save()
            
            messages.success(request, f'¡Expedición iniciada hacia {destination}!')
            
        except Ship.DoesNotExist:
            messages.error(request, 'Barco no encontrado.')
        
        return redirect('exploration:dashboard')
    
    # GET request - mostrar formulario
    player = get_object_or_404(Player, user=request.user)
    available_ships = Ship.objects.filter(player=player, status='docked')
    
    context = {
        'player': player,
        'available_ships': available_ships,
        'destinations': [
            'Islas del Tesoro',
            'Archipiélago Perdido',
            'Mar de las Tormentas',
            'Costa Dorada',
            'Islas Misteriosas'
        ]
    }
    return render(request, 'exploration/start_expedition.html', context)


@login_required
def expedition_detail(request, expedition_id):
    """Ver detalles de una expedición."""
    player = get_object_or_404(Player, user=request.user)
    expedition = get_object_or_404(Expedition, id=expedition_id, player=player)
    
    context = {
        'player': player,
        'expedition': expedition,
    }
    return render(request, 'exploration/expedition_detail.html', context)


@login_required
def complete_expedition(request, expedition_id):
    """Completar una expedición."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        expedition = get_object_or_404(Expedition, id=expedition_id, player=player)
        
        if expedition.status != 'active':
            messages.error(request, 'Esta expedición no puede ser completada.')
            return redirect('exploration:dashboard')
        
        # Completar expedición
        expedition.status = 'completed'
        expedition.save()
        
        # Devolver barco al puerto
        expedition.ship.status = 'docked'
        expedition.ship.save()
        
        # Otorgar recompensas (simulado)
        gold_reward = 100
        experience_reward = 50
        
        player.gold += gold_reward
        player.experience += experience_reward
        player.save()
        
        messages.success(request, f'¡Expedición completada! Ganaste {gold_reward} oro y {experience_reward} XP.')
        
        return redirect('exploration:dashboard')
    
    return redirect('exploration:dashboard')


@login_required
def map_view(request):
    """Ver el mapa de exploración."""
    player = get_object_or_404(Player, user=request.user)
    
    # Obtener o crear mapa del jugador
    exploration_map, created = ExplorationMap.objects.get_or_create(
        player=player,
        defaults={'explored_areas': []}
    )
    
    context = {
        'player': player,
        'exploration_map': exploration_map,
    }
    return render(request, 'exploration/map.html', context)


@login_required
def discovery_list(request):
    """Lista de descubrimientos del jugador."""
    player = get_object_or_404(Player, user=request.user)
    discoveries = Discovery.objects.filter(player=player).order_by('-discovered_at')
    
    context = {
        'player': player,
        'discoveries': discoveries,
    }
    return render(request, 'exploration/discoveries.html', context)
