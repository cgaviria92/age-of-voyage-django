"""
BattleService: Lógica de negocio para batallas navales.
Reutilizable y desacoplada de las vistas.
"""
from apps.combat.models import Battle, CombatTurn, PirateFleet
from apps.players.models import Player
from apps.ships.models import Ship
from django.utils import timezone
import random

class BattleService:
    @staticmethod
    def start_battle(attacker: Player, defender: Player = None, attacker_ship: Ship = None, defender_ship: Ship = None, battle_type: str = 'pve', npc_data=None):
        """Crea e inicia una batalla."""
        battle = Battle.objects.create(
            attacker=attacker,
            defender=defender,
            attacker_ship=attacker_ship,
            defender_ship=defender_ship,
            battle_type=battle_type,
            status='in_progress',
            npc_name=npc_data.get('name', '') if npc_data else '',
            npc_health=npc_data.get('health', 100) if npc_data else 100,
            npc_max_health=npc_data.get('max_health', 100) if npc_data else 100,
            npc_attack_power=npc_data.get('attack_power', 20) if npc_data else 20,
            npc_defense=npc_data.get('defense', 15) if npc_data else 15,
            npc_type=npc_data.get('type', 'pirate') if npc_data else 'pirate',
        )
        battle.start_battle()
        return battle

    @staticmethod
    def resolve_battle(battle: Battle):
        """Resuelve la batalla y asigna recompensas."""
        battle.resolve_battle()
        return battle

    @staticmethod
    def process_turn(battle: Battle, acting_player: Player, action_type: str):
        """Procesa un turno de combate y actualiza el estado."""
        # Aquí iría la lógica de daño, defensa, etc. (puede delegarse a otro servicio)
        turn_number = CombatTurn.objects.filter(battle=battle).count() + 1
        turn = CombatTurn.objects.create(
            battle=battle,
            turn_number=turn_number,
            acting_player=acting_player,
            action_type=action_type,
            damage_dealt=random.randint(10, 50),
            damage_received=random.randint(5, 30),
            description=f"{acting_player.captain_name} realizó {action_type}"
        )
        return turn

    @staticmethod
    def get_battle_log(battle: Battle):
        """Devuelve el log de la batalla en formato estructurado."""
        return list(battle.turns.order_by('turn_number').values('turn_number', 'acting_player__captain_name', 'action_type', 'description', 'damage_dealt', 'damage_received'))

    @staticmethod
    def get_active_pirate_fleets(player: Player):
        """Obtiene flotas piratas activas para el nivel del jugador."""
        return PirateFleet.objects.filter(is_active=True, level__lte=player.level + 2)
