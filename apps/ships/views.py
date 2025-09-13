from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from .models import Ship, ShipType, ShipUpgrade, CrewMember
from apps.players.models import Player


@login_required
def ship_list(request):
    """Lista de barcos del jugador"""
    player = get_object_or_404(Player, user=request.user)
    ships = Ship.objects.filter(owner=player).order_by('-created_at')
    
    # Estadísticas de la flota
    total_crew = sum(ship.crew_members.count() for ship in ships)
    total_combat_power = sum(ship.ship_type.attack_power + ship.ship_type.defense_power for ship in ships)
    total_cargo_capacity = sum(ship.ship_type.cargo_capacity for ship in ships)
    average_speed = ships.aggregate(models.Avg('speed'))['speed__avg'] or 0
    
    context = {
        'ships': ships,
        'player': player,
        'max_ships': 10,  # Límite de barcos
        'total_crew': total_crew,
        'total_combat_power': total_combat_power,
        'total_cargo_capacity': total_cargo_capacity,
        'average_speed': round(average_speed, 1),
    }
    return render(request, 'ships/fleet.html', context)


@login_required
def ship_detail(request, ship_id):
    """Detalle de un barco específico"""
    player = get_object_or_404(Player, user=request.user)
    ship = get_object_or_404(Ship, id=ship_id, owner=player)
    
    cargo_items = ship.cargo_items.all()
    crew_members = ship.crew_members.all()
    
    context = {
        'ship': ship,
        'cargo_items': cargo_items,
        'crew_members': crew_members,
    }
    return render(request, 'ships/ship_detail.html', context)


@login_required
def shipyard(request):
    """Astillero - Comprar nuevos barcos"""
    player = get_object_or_404(Player, user=request.user)
    
    # Barcos disponibles según el nivel del jugador
    ship_types = ShipType.objects.filter(required_level__lte=player.level)
    
    # Barcos que el jugador ya posee
    player_ships_count = Ship.objects.filter(owner=player).count()
    
    context = {
        'ship_types': ship_types,
        'player_ships_count': player_ships_count,
        'player': player,
        'max_ships': 10,  # Límite de barcos por jugador
    }
    return render(request, 'ships/shipyard.html', context)


@login_required
def build_ship(request):
    """Construir un barco nuevo"""
    if request.method != 'POST':
        return redirect('ships:shipyard')
    
    player = get_object_or_404(Player, user=request.user)
    ship_type_id = request.POST.get('ship_type_id')
    ship_name = request.POST.get('ship_name')
    
    if not ship_type_id or not ship_name:
        messages.error(request, 'Datos incompletos.')
        return redirect('ships:shipyard')
    
    ship_type = get_object_or_404(ShipType, id=ship_type_id)
    
    # Verificaciones
    if Ship.objects.filter(owner=player).count() >= 10:
        messages.error(request, 'Has alcanzado el límite máximo de barcos.')
        return redirect('ships:shipyard')
    
    if player.level < ship_type.required_level:
        messages.error(request, f'Necesitas nivel {ship_type.required_level} para construir este barco.')
        return redirect('ships:shipyard')
    
    if player.gold < ship_type.purchase_cost:
        messages.error(request, 'No tienes suficiente oro para construir este barco.')
        return redirect('ships:shipyard')
    
    # Verificar que el nombre no esté en uso
    if Ship.objects.filter(owner=player, name=ship_name).exists():
        messages.error(request, 'Ya tienes un barco con ese nombre.')
        return redirect('ships:shipyard')
    
    # Crear el barco
    ship = Ship.objects.create(
        owner=player,
        ship_type=ship_type,
        name=ship_name,
        speed=ship_type.base_speed,
        cargo_capacity=ship_type.base_cargo_capacity,
        firepower=ship_type.base_firepower,
        defense=ship_type.base_defense,
        crew_capacity=ship_type.base_crew_capacity,
        crew_count=ship_type.base_crew_capacity // 2,  # Empezar con media tripulación
        hull_health=100,
        status='docked'
    )
    # Descontar oro
    player.gold -= ship_type.purchase_cost
    player.save()
    player.gold -= ship_type.cost
    player.save()
    
    messages.success(request, f'¡Barco "{ship_name}" construido exitosamente!')
    return redirect('ships:fleet')
    player.save()
    
    messages.success(request, f'¡Has adquirido el {ship.name} exitosamente!')
    return redirect('ships:ship_detail', ship_id=ship.id)


@login_required
def repair_ship(request, ship_id):
    """Reparar un barco"""
    if request.method != 'POST':
        return redirect('ships:ship_detail', ship_id=ship_id)
    
    player = get_object_or_404(Player, user=request.user)
    ship = get_object_or_404(Ship, id=ship_id, owner=player)
    
    if ship.hull_health >= 100:
        messages.info(request, 'El barco ya está en perfecto estado.')
        return redirect('ships:ship_detail', ship_id=ship_id)
    
    damage = 100 - ship.hull_health
    repair_cost = damage * 10
    
    if not player.can_afford(repair_cost):
        messages.error(request, f'Necesitas {repair_cost} oro para reparar completamente el barco.')
        return redirect('ships:ship_detail', ship_id=ship_id)
    
    # Reparar
    ship.repair()
    messages.success(request, f'El {ship.name} ha sido reparado completamente por {repair_cost} oro.')
    
    return redirect('ships:ship_detail', ship_id=ship_id)


@login_required
def upgrade_ship(request, ship_id):
    """Página de mejoras del barco"""
    player = get_object_or_404(Player, user=request.user)
    ship = get_object_or_404(Ship, id=ship_id, owner=player)
    
    available_upgrades = ShipUpgrade.objects.filter(required_level__lte=player.level)
    
    context = {
        'ship': ship,
        'available_upgrades': available_upgrades,
    }
    return render(request, 'ships/upgrade_ship.html', context)


@login_required
def hire_crew(request, ship_id):
    """Contratar tripulación"""
    player = get_object_or_404(Player, user=request.user)
    ship = get_object_or_404(Ship, id=ship_id, owner=player)
    
    if request.method == 'POST':
        crew_type = request.POST.get('crew_type')
        crew_name = request.POST.get('crew_name')
        
        if ship.crew_members.count() >= ship.crew_capacity:
            messages.error(request, 'El barco ya tiene la tripulación completa.')
            return redirect('ships:ship_detail', ship_id=ship_id)
        
        # Costo base según tipo de tripulante
        crew_costs = {
            'sailor': 50,
            'gunner': 75,
            'navigator': 100,
            'carpenter': 80,
            'cook': 60,
            'quartermaster': 120,
        }
        
        cost = crew_costs.get(crew_type, 50)
        
        if not player.can_afford(cost):
            messages.error(request, f'No tienes suficiente oro para contratar este tripulante ({cost} oro).')
            return redirect('ships:ship_detail', ship_id=ship_id)
        
        # Contratar tripulante
        CrewMember.objects.create(
            ship=ship,
            name=crew_name,
            crew_type=crew_type,
            skill_level=1,
            salary_per_day=cost // 10,
        )
        
        ship.crew_count += 1
        ship.save()
        
        player.spend_gold(cost)
        player.save()
        
        messages.success(request, f'Has contratado a {crew_name} como {dict(CrewMember.CREW_TYPES)[crew_type]}.')
        return redirect('ships:ship_detail', ship_id=ship_id)
    
    available_crew_types = CrewMember.CREW_TYPES
    context = {
        'ship': ship,
        'available_crew_types': available_crew_types,
    }
    return render(request, 'ships/hire_crew.html', context)


@login_required
def ship_status_api(request, ship_id):
    """API para obtener estado del barco"""
    player = get_object_or_404(Player, user=request.user)
    ship = get_object_or_404(Ship, id=ship_id, owner=player)
    
    data = {
        'id': ship.id,
        'name': ship.name,
        'status': ship.status,
        'hull_health': ship.hull_health,
        'crew_count': ship.crew_count,
        'cargo_weight': ship.current_cargo_weight,
        'available_cargo': ship.available_cargo_space,
        'is_operational': ship.is_operational,
    }
    
    return JsonResponse(data)
