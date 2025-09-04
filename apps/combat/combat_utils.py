from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from apps.players.models import Player
from apps.ships.models import Ship
from .models import Battle, CombatTurn
import random


def execute_combat_action(battle, player, action_type):
    """Ejecutar una acción de combate y calcular resultado."""
    ship = battle.attacker_ship
    result = {
        'damage_dealt': 0,
        'damage_received': 0,
        'description': '',
        'battle_ended': False,
        'end_message': ''
    }
    
    if action_type == 'cannon':
        # Disparo de cañón
        base_damage = ship.firepower + random.randint(-10, 10)
        accuracy = 0.8 + (player.combat_skill * 0.02)
        
        if random.random() < accuracy:
            damage = max(1, base_damage - battle.npc_defense // 2)
            battle.npc_health -= damage
            result['damage_dealt'] = damage
            result['description'] = f"¡Disparo certero! Causaste {damage} de daño al enemigo."
        else:
            result['description'] = "¡Tu disparo falló!"
    
    elif action_type == 'ram':
        # Embestida
        damage_to_enemy = ship.firepower // 2 + random.randint(5, 15)
        damage_to_self = random.randint(5, 10)
        
        battle.npc_health -= damage_to_enemy
        ship.health -= damage_to_self
        ship.save()
        
        result['damage_dealt'] = damage_to_enemy
        result['damage_received'] = damage_to_self
        result['description'] = f"¡Embestida! Causaste {damage_to_enemy} de daño pero recibiste {damage_to_self}."
    
    elif action_type == 'repair':
        # Reparación
        repair_amount = random.randint(10, 20)
        ship.health = min(ship.ship_type.max_health, ship.health + repair_amount)
        ship.save()
        
        result['description'] = f"Reparaste tu barco por {repair_amount} puntos de salud."
    
    # Verificar si el NPC fue derrotado
    if battle.npc_health <= 0:
        battle.winner = player
        result['battle_ended'] = True
        result['end_message'] = f"¡Victoria! Derrotaste a {battle.npc_name}."
    
    battle.save()
    return result


def execute_npc_turn(battle):
    """Ejecutar turno del NPC."""
    result = {
        'damage_dealt': 0,
        'description': '',
        'battle_ended': False,
        'end_message': ''
    }
    
    # NPC siempre ataca
    damage = battle.npc_attack_power + random.randint(-5, 5)
    damage = max(1, damage - battle.attacker_ship.defense // 2)
    
    battle.attacker_ship.health -= damage
    battle.attacker_ship.save()
    
    result['damage_dealt'] = damage
    result['description'] = f"{battle.npc_name} te atacó causando {damage} de daño."
    
    # Verificar si el jugador fue derrotado
    if battle.attacker_ship.health <= 0:
        battle.winner = None  # NPC gana
        result['battle_ended'] = True
        result['end_message'] = f"Derrota... {battle.npc_name} destruyó tu barco."
    
    return result
