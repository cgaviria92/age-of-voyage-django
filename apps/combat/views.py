from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from .models import Battle, Fleet, CombatReport
from apps.players.models import Player
from apps.ships.models import Ship


@login_required
def combat_dashboard(request):
    """Panel principal de combate."""
    player = get_object_or_404(Player, user=request.user)
    active_battles = Battle.objects.filter(
        models.Q(attacker=player) | models.Q(defender=player),
        status='active'
    )
    recent_reports = CombatReport.objects.filter(
        models.Q(attacker=player) | models.Q(defender=player)
    ).order_by('-created_at')[:10]
    
    context = {
        'player': player,
        'active_battles': active_battles,
        'recent_reports': recent_reports,
    }
    return render(request, 'combat/dashboard.html', context)


@login_required
def fleet_management(request):
    """Gestión de flotas."""
    player = get_object_or_404(Player, user=request.user)
    fleets = Fleet.objects.filter(player=player)
    available_ships = Ship.objects.filter(player=player, status='docked')
    
    context = {
        'player': player,
        'fleets': fleets,
        'available_ships': available_ships,
    }
    return render(request, 'combat/fleet_management.html', context)


@login_required
def create_fleet(request):
    """Crear una nueva flota."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        fleet_name = request.POST.get('fleet_name')
        ship_ids = request.POST.getlist('ship_ids')
        
        if not fleet_name or not ship_ids:
            messages.error(request, 'Debes proporcionar un nombre y seleccionar barcos.')
            return redirect('combat:fleet_management')
        
        try:
            # Crear flota
            fleet = Fleet.objects.create(
                player=player,
                name=fleet_name,
                is_active=True
            )
            
            # Agregar barcos a la flota
            ships = Ship.objects.filter(id__in=ship_ids, player=player, status='docked')
            fleet.ships.set(ships)
            
            # Actualizar estado de los barcos
            ships.update(status='fleet')
            
            messages.success(request, f'¡Flota "{fleet_name}" creada exitosamente!')
            
        except Exception as e:
            messages.error(request, 'Error al crear la flota.')
        
        return redirect('combat:fleet_management')
    
    return redirect('combat:fleet_management')


@login_required
def attack_player(request):
    """Atacar a otro jugador."""
    if request.method == 'POST':
        attacker = get_object_or_404(Player, user=request.user)
        defender_id = request.POST.get('defender_id')
        fleet_id = request.POST.get('fleet_id')
        
        try:
            defender = Player.objects.get(id=defender_id)
            fleet = Fleet.objects.get(id=fleet_id, player=attacker)
            
            if not fleet.is_active or fleet.ships.count() == 0:
                messages.error(request, 'La flota no está disponible para combate.')
                return redirect('combat:dashboard')
            
            # Crear batalla
            battle = Battle.objects.create(
                attacker=attacker,
                defender=defender,
                attacker_fleet=fleet,
                status='active'
            )
            
            messages.success(request, f'¡Batalla iniciada contra {defender.user.username}!')
            return redirect('combat:battle_detail', battle_id=battle.id)
            
        except (Player.DoesNotExist, Fleet.DoesNotExist):
            messages.error(request, 'Error al iniciar la batalla.')
        
        return redirect('combat:dashboard')
    
    # GET request
    player = get_object_or_404(Player, user=request.user)
    available_fleets = Fleet.objects.filter(player=player, is_active=True)
    potential_targets = Player.objects.exclude(id=player.id)[:20]  # Limitar para rendimiento
    
    context = {
        'player': player,
        'available_fleets': available_fleets,
        'potential_targets': potential_targets,
    }
    return render(request, 'combat/attack_player.html', context)


@login_required
def battle_detail(request, battle_id):
    """Ver detalles de una batalla."""
    player = get_object_or_404(Player, user=request.user)
    battle = get_object_or_404(Battle, id=battle_id)
    
    # Verificar que el jugador participa en la batalla
    if battle.attacker != player and battle.defender != player:
        messages.error(request, 'No tienes acceso a esta batalla.')
        return redirect('combat:dashboard')
    
    context = {
        'player': player,
        'battle': battle,
    }
    return render(request, 'combat/battle_detail.html', context)


@login_required
def resolve_battle(request, battle_id):
    """Resolver una batalla (simulado)."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        battle = get_object_or_404(Battle, id=battle_id)
        
        if battle.status != 'active':
            messages.error(request, 'Esta batalla ya fue resuelta.')
            return redirect('combat:dashboard')
        
        if battle.attacker != player and battle.defender != player:
            messages.error(request, 'No puedes resolver esta batalla.')
            return redirect('combat:dashboard')
        
        # Simulación simple de combate
        import random
        attacker_power = battle.attacker_fleet.ships.count() * 100 if battle.attacker_fleet else 50
        defender_power = random.randint(50, 150)  # Simulado para el defensor
        
        if attacker_power > defender_power:
            winner = battle.attacker
            loser = battle.defender
            result = 'victory'
        else:
            winner = battle.defender
            loser = battle.attacker
            result = 'defeat'
        
        # Crear reporte de combate
        CombatReport.objects.create(
            battle=battle,
            attacker=battle.attacker,
            defender=battle.defender,
            winner=winner,
            attacker_casualties=random.randint(0, 2),
            defender_casualties=random.randint(0, 2),
            loot_gold=random.randint(50, 200) if result == 'victory' else 0
        )
        
        # Finalizar batalla
        battle.status = 'completed'
        battle.save()
        
        # Devolver barcos al puerto
        if battle.attacker_fleet:
            battle.attacker_fleet.ships.update(status='docked')
        
        if result == 'victory':
            messages.success(request, '¡Victoria! Has ganado la batalla.')
        else:
            messages.warning(request, 'Derrota. Mejor suerte la próxima vez.')
        
        return redirect('combat:dashboard')
    
    return redirect('combat:dashboard')


@login_required
def combat_history(request):
    """Historial de combates."""
    player = get_object_or_404(Player, user=request.user)
    
    reports = CombatReport.objects.filter(
        models.Q(attacker=player) | models.Q(defender=player)
    ).order_by('-created_at')
    
    context = {
        'player': player,
        'reports': reports,
    }
    return render(request, 'combat/history.html', context)
