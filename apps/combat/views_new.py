from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db import models
from apps.players.models import Player
from apps.ships.models import Ship
from .models import Battle, BattleTurn
import random


@login_required
def combat_arena(request):
    """Arena de combate principal."""
    player = get_object_or_404(Player, user=request.user)
    
    # Barcos disponibles para combate
    available_ships = Ship.objects.filter(owner=player, status='idle', health__gt=0)
    
    # Batallas activas
    active_battles = Battle.objects.filter(
        models.Q(attacker=player) | models.Q(defender=player),
        status='in_progress'
    ).select_related('attacker', 'defender', 'attacker_ship', 'defender_ship')[:5]
    
    # Historial reciente
    recent_battles = Battle.objects.filter(
        models.Q(attacker=player) | models.Q(defender=player),
        status='completed'
    ).select_related('attacker', 'defender', 'winner').order_by('-completed_at')[:10]
    
    # Estadísticas de combate
    combat_stats = {
        'total_battles': Battle.objects.filter(
            models.Q(attacker=player) | models.Q(defender=player),
            status='completed'
        ).count(),
        'battles_won': Battle.objects.filter(winner=player).count(),
        'battles_lost': Battle.objects.filter(
            models.Q(attacker=player) | models.Q(defender=player),
            status='completed'
        ).exclude(winner=player).count(),
    }
    
    context = {
        'player': player,
        'available_ships': available_ships,
        'active_battles': active_battles,
        'recent_battles': recent_battles,
        'combat_stats': combat_stats,
    }
    return render(request, 'combat/arena.html', context)


@login_required
def challenge_npc(request):
    """Desafiar a un NPC enemigo."""
    if request.method != 'POST':
        return redirect('combat:arena')
    
    player = get_object_or_404(Player, user=request.user)
    ship_id = request.POST.get('ship_id')
    difficulty = request.POST.get('difficulty', 'easy')
    
    if not ship_id:
        messages.error(request, 'Debes seleccionar un barco.')
        return redirect('combat:arena')
    
    ship = get_object_or_404(Ship, id=ship_id, owner=player, status='idle')
    
    if ship.health <= 0:
        messages.error(request, 'El barco necesita reparación antes del combate.')
        return redirect('combat:arena')
    
    # Crear batalla automática contra NPC
    battle = create_npc_battle(player, ship, difficulty)
    
    messages.success(request, f'¡Batalla iniciada contra {battle.npc_name}!')
    return redirect('combat:battle_detail', battle_id=battle.id)


@login_required
def battle_detail(request, battle_id):
    """Detalle de una batalla específica."""
    battle = get_object_or_404(Battle, id=battle_id)
    player = get_object_or_404(Player, user=request.user)
    
    # Verificar que el jugador participa en la batalla
    if battle.attacker != player and battle.defender != player:
        messages.error(request, 'No tienes acceso a esta batalla.')
        return redirect('combat:arena')
    
    # Turnos de la batalla
    battle_turns = BattleTurn.objects.filter(battle=battle).order_by('turn_number')
    
    # Determinar si es turno del jugador
    is_player_turn = False
    if battle.status == 'in_progress':
        last_turn = battle_turns.last()
        if not last_turn:
            is_player_turn = (battle.attacker == player)
        else:
            is_player_turn = (last_turn.player != player)
    
    context = {
        'battle': battle,
        'player': player,
        'battle_turns': battle_turns,
        'is_player_turn': is_player_turn,
    }
    return render(request, 'combat/battle_detail.html', context)


@login_required
def execute_attack(request, battle_id):
    """Ejecutar un ataque en la batalla."""
    if request.method != 'POST':
        return redirect('combat:battle_detail', battle_id=battle_id)
    
    battle = get_object_or_404(Battle, id=battle_id)
    player = get_object_or_404(Player, user=request.user)
    
    # Verificaciones
    if battle.status != 'in_progress':
        messages.error(request, 'Esta batalla no está activa.')
        return redirect('combat:battle_detail', battle_id=battle_id)
    
    if battle.attacker != player and battle.defender != player:
        messages.error(request, 'No participas en esta batalla.')
        return redirect('combat:arena')
    
    attack_type = request.POST.get('attack_type', 'normal')
    
    with transaction.atomic():
        # Ejecutar ataque
        result = execute_battle_turn(battle, player, attack_type)
        
        # Verificar si la batalla terminó
        if result['battle_ended']:
            battle.status = 'completed'
            battle.completed_at = timezone.now()
            battle.winner = result['winner']
            battle.save()
            
            # Aplicar recompensas y penalizaciones
            apply_battle_rewards(battle, result)
            
            messages.success(request, f'¡Batalla completada! {result["message"]}')
        else:
            messages.info(request, result['message'])
    
    return redirect('combat:battle_detail', battle_id=battle_id)


def create_npc_battle(player, ship, difficulty):
    """Crear una batalla automática contra NPC."""
    # Configuración de dificultad
    difficulty_settings = {
        'easy': {'health_mult': 0.8, 'attack_mult': 0.9, 'xp_reward': 15},
        'medium': {'health_mult': 1.0, 'attack_mult': 1.0, 'xp_reward': 25},
        'hard': {'health_mult': 1.3, 'attack_mult': 1.2, 'xp_reward': 40},
    }
    
    settings = difficulty_settings.get(difficulty, difficulty_settings['easy'])
    
    # Crear batalla
    battle = Battle.objects.create(
        attacker=player,
        attacker_ship=ship,
        battle_type='pve',
        status='in_progress',
        npc_name=f"Pirata {random.choice(['Barbanegra', 'Capitán Rojo', 'El Corsario', 'Barba de Acero'])}",
        npc_health=int(ship.ship_type.max_health * settings['health_mult']),
        npc_max_health=int(ship.ship_type.max_health * settings['health_mult']),
        npc_attack_power=int(ship.ship_type.attack_power * settings['attack_mult']),
        experience_reward=settings['xp_reward'],
        gold_stakes=random.randint(50, 200)
    )
    
    # Cambiar estado del barco
    ship.status = 'in_combat'
    ship.save()
    
    return battle


def execute_battle_turn(battle, player, attack_type):
    """Ejecutar un turno de batalla."""
    # Determinar atacante y defensor
    if battle.battle_type == 'pve':
        if player == battle.attacker:
            # Turno del jugador contra NPC
            attacker_ship = battle.attacker_ship
            attacker_attack = calculate_attack_damage(attacker_ship, attack_type)
            
            # Aplicar daño al NPC
            battle.npc_health = max(0, battle.npc_health - attacker_attack)
            battle.save()
            
            # Crear turno
            turn = BattleTurn.objects.create(
                battle=battle,
                player=player,
                turn_number=BattleTurn.objects.filter(battle=battle).count() + 1,
                action_type=attack_type,
                damage_dealt=attacker_attack,
                description=f"{player.captain_name} ataca con {attack_type} causando {attacker_attack} de daño"
            )
            
            # Verificar si el NPC murió
            if battle.npc_health <= 0:
                return {
                    'battle_ended': True,
                    'winner': player,
                    'message': f'¡Victoria! Has derrotado a {battle.npc_name}'
                }
            
            # Turno del NPC
            npc_attack = random.randint(
                int(battle.npc_attack_power * 0.8),
                int(battle.npc_attack_power * 1.2)
            )
            attacker_ship.health = max(0, attacker_ship.health - npc_attack)
            attacker_ship.save()
            
            # Crear turno del NPC
            BattleTurn.objects.create(
                battle=battle,
                player=None,  # NPC
                turn_number=BattleTurn.objects.filter(battle=battle).count() + 1,
                action_type='normal',
                damage_dealt=npc_attack,
                description=f"{battle.npc_name} contraataca causando {npc_attack} de daño"
            )
            
            # Verificar si el jugador perdió
            if attacker_ship.health <= 0:
                return {
                    'battle_ended': True,
                    'winner': None,
                    'message': f'Derrota... {battle.npc_name} ha hundido tu barco'
                }
            
            return {
                'battle_ended': False,
                'message': f'Atacaste causando {attacker_attack} de daño. {battle.npc_name} contraatacó con {npc_attack}'
            }
    
    return {'battle_ended': False, 'message': 'Turno ejecutado'}


def calculate_attack_damage(ship, attack_type):
    """Calcular daño de ataque basado en el barco y tipo de ataque."""
    base_attack = ship.ship_type.attack_power
    
    multipliers = {
        'normal': 1.0,
        'heavy': 1.5,
        'precise': 1.2,
        'ramming': 1.8,
    }
    
    multiplier = multipliers.get(attack_type, 1.0)
    damage = int(base_attack * multiplier * random.uniform(0.8, 1.2))
    
    return max(1, damage)


def apply_battle_rewards(battle, result):
    """Aplicar recompensas y penalizaciones después de la batalla."""
    if result['winner']:
        winner = result['winner']
        winner.gold += battle.gold_stakes
        winner.experience += battle.experience_reward
        winner.total_battles_won += 1
        winner.save()
        
        # Restaurar estado del barco
        if battle.attacker == winner:
            battle.attacker_ship.status = 'idle'
            battle.attacker_ship.save()
    else:
        # Batalla perdida - penalizaciones menores
        if battle.attacker:
            battle.attacker_ship.status = 'damaged'
            battle.attacker_ship.save()
