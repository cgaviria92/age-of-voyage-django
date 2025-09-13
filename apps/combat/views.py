from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from apps.players.models import Player
from apps.ships.models import Ship
from apps.exploration.models import Region
from .models import Battle, PirateFleet, CombatTurn
from .combat_utils import execute_combat_action, execute_npc_turn
import random
import json


@login_required
def combat_dashboard(request):
    """Panel principal de combate."""
    player = get_object_or_404(Player, user=request.user)
    
    # Batallas activas
    active_battles = Battle.objects.filter(
        Q(attacker=player) | Q(defender=player),
        status__in=['preparing', 'in_progress']
    ).select_related('attacker', 'defender', 'attacker_ship', 'defender_ship')
    
    # Batallas completadas recientes
    recent_battles = Battle.objects.filter(
        Q(attacker=player) | Q(defender=player),
        status='completed'
    ).select_related('attacker', 'defender', 'winner').order_by('-completed_at')[:5]
    
    # Barcos disponibles para combate
    available_ships = Ship.objects.filter(
        owner=player, 
        status='idle',
        health__gt=0
    ).select_related('ship_type')
    
    # Estadísticas
    stats = {
        'total_battles': Battle.objects.filter(Q(attacker=player) | Q(defender=player)).count(),
        'battles_won': Battle.objects.filter(winner=player).count(),
        'battles_lost': Battle.objects.filter(
            Q(attacker=player) | Q(defender=player), 
            winner__isnull=False
        ).exclude(winner=player).count(),
    }
    
    context = {
        'player': player,
        'active_battles': active_battles,
        'recent_battles': recent_battles,
        'available_ships': available_ships,
        'stats': stats,
    }
    return render(request, 'combat/dashboard.html', context)


@login_required
def pirate_hunt(request):
    """Caza de piratas - combate PvE."""
    player = get_object_or_404(Player, user=request.user)
    
    # Barcos disponibles
def combat_action(request, battle_id):
    battle = get_object_or_404(Battle, id=battle_id)
    # Lógica básica de acción de combate
    if request.method == 'POST':
        action = request.POST.get('action')
        # Aquí puedes agregar la lógica de ataque, defensa, huida, etc.
        # Por ahora solo redirige al detalle de la batalla
        return redirect('combat:battle_detail', battle_id=battle.id)
    return render(request, 'combat/action.html', {'battle': battle})
        owner=player, 
        status='idle',
        health__gt=0
    ).select_related('ship_type')
    
    # Flotas piratas activas
    pirate_fleets = PirateFleet.objects.filter(
        is_active=True,
        level__lte=player.level + 2  # Solo piratas de nivel similar
    ).select_related('current_region')
    
    context = {
        'player': player,
        'available_ships': available_ships,
        'pirate_fleets': pirate_fleets,
    }
    return render(request, 'combat/pirate_hunt.html', context)


@login_required
def start_pirate_battle(request):
    """Iniciar batalla contra piratas."""
    if request.method != 'POST':
        return redirect('combat:pirate_hunt')
    
    player = get_object_or_404(Player, user=request.user)
    
    ship_id = request.POST.get('ship_id')
    fleet_id = request.POST.get('fleet_id')
    
    if not ship_id or not fleet_id:
        messages.error(request, 'Datos incompletos.')
        return redirect('combat:pirate_hunt')
    
    ship = get_object_or_404(Ship, id=ship_id, owner=player, status='idle')
    pirate_fleet = get_object_or_404(PirateFleet, id=fleet_id, is_active=True)
    
    # Verificaciones
    if ship.health <= 0:
        messages.error(request, 'Tu barco está demasiado dañado para el combate.')
        return redirect('combat:pirate_hunt')
    
    if ship.crew_count < ship.ship_type.crew_capacity * 0.5:
        messages.error(request, 'Necesitas más tripulación para el combate.')
        return redirect('combat:pirate_hunt')
    
    # Crear batalla
    battle = Battle.objects.create(
        attacker=player,
        attacker_ship=ship,
        battle_type='pve',
        npc_name=pirate_fleet.name,
        npc_health=pirate_fleet.defense * 10,
        npc_max_health=pirate_fleet.defense * 10,
        npc_attack_power=pirate_fleet.firepower,
        npc_defense=pirate_fleet.defense,
        npc_type=pirate_fleet.fleet_type,
        gold_stakes=pirate_fleet.gold_reward,
        experience_reward=pirate_fleet.experience_reward
    )
    
    # Iniciar batalla
    battle.start_battle()
    
    messages.success(request, f'¡Batalla contra {pirate_fleet.name} iniciada!')
    return redirect('combat:battle_detail', battle_id=battle.id)


@login_required
def battle_detail(request, battle_id):
    """Detalle de una batalla específica."""
    player = get_object_or_404(Player, user=request.user)
    battle = get_object_or_404(Battle, id=battle_id)
    
    # Verificar que el jugador participa en la batalla
    if battle.attacker != player and battle.defender != player:
        messages.error(request, 'No tienes acceso a esta batalla.')
        return redirect('combat:dashboard')
    
    # Turnos de la batalla
    turns = CombatTurn.objects.filter(battle=battle).order_by('turn_number')
    
    # Si la batalla está en progreso y es el turno del jugador
    can_act = (
        battle.status == 'in_progress' and 
        battle.attacker == player and
        not turns.filter(turn_number=turns.count() + 1).exists()
    )
    
    context = {
        'player': player,
        'battle': battle,
        'turns': turns,
        'can_act': can_act,
    }
    return render(request, 'combat/battle_detail.html', context)


@login_required
def combat_action(request, battle_id):
    """Ejecutar una acción de combate."""
    if request.method != 'POST':
        return redirect('combat:battle_detail', battle_id=battle_id)
    
    player = get_object_or_404(Player, user=request.user)
    battle = get_object_or_404(Battle, id=battle_id, attacker=player, status='in_progress')
    
    action_type = request.POST.get('action_type')
    
    if not action_type or action_type not in ['cannon', 'ram', 'board', 'repair']:
        messages.error(request, 'Acción no válida.')
        return redirect('combat:battle_detail', battle_id=battle_id)
    
    # Calcular resultado de la acción
    result = execute_combat_action(battle, player, action_type)
    
    # Crear turno
    turn_number = CombatTurn.objects.filter(battle=battle).count() + 1
    CombatTurn.objects.create(
        battle=battle,
        turn_number=turn_number,
        acting_player=player,
        action_type=action_type,
        damage_dealt=result['damage_dealt'],
        damage_received=result['damage_received'],
        description=result['description']
    )
    
    # Verificar si la batalla ha terminado
    if result['battle_ended']:
        battle.resolve_battle()
        messages.success(request, result['end_message'])
    else:
        # Turno del NPC
        npc_result = execute_npc_turn(battle)
        turn_number += 1
        CombatTurn.objects.create(
            battle=battle,
            turn_number=turn_number,
            acting_player=None,  # NPC
            action_type='cannon',
            damage_dealt=npc_result['damage_dealt'],
            damage_received=0,
            description=npc_result['description']
        )
        
        if npc_result['battle_ended']:
            battle.resolve_battle()
            messages.warning(request, npc_result['end_message'])
    
    return redirect('combat:battle_detail', battle_id=battle_id)


@login_required
def battle_history(request):
    """Historial de batallas del jugador."""
    player = get_object_or_404(Player, user=request.user)
    
    battles = Battle.objects.filter(
        Q(attacker=player) | Q(defender=player),
        status='completed'
    ).select_related('attacker', 'defender', 'winner').order_by('-completed_at')
    
    paginator = Paginator(battles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'player': player,
        'page_obj': page_obj,
    }
    return render(request, 'combat/battle_history.html', context)
