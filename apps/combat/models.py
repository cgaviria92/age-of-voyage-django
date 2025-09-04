from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.players.models import Player
from apps.ships.models import Ship
import random


class Battle(models.Model):
    """Batalla naval entre jugadores o contra NPCs"""
    
    BATTLE_TYPES = [
        ('pvp', 'Jugador vs Jugador'),
        ('pve', 'Jugador vs NPC'),
        ('raid', 'Asalto'),
        ('defense', 'Defensa'),
    ]
    
    STATUS_CHOICES = [
        ('preparing', 'Preparando'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    
    # Participantes
    attacker = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='battles_as_attacker')
    defender = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='battles_as_defender', null=True, blank=True)
    
    # Barcos participantes
    attacker_ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name='battles_as_attacker')
    defender_ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name='battles_as_defender', null=True, blank=True)
    
    # Datos del NPC (para batallas PvE)
    npc_name = models.CharField(max_length=100, blank=True)
    npc_health = models.IntegerField(default=100)
    npc_max_health = models.IntegerField(default=100)
    npc_attack_power = models.IntegerField(default=20)
    
    # Características de la batalla
    battle_type = models.CharField(max_length=20, choices=BATTLE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='preparing')
    
    # Resultado
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='battles_won')
    
    # Tiempos
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Recompensas y pérdidas
    gold_stakes = models.IntegerField(default=0)
    experience_reward = models.IntegerField(default=0)
    
    # Log de la batalla
    battle_log = models.TextField(blank=True)
    
    @property
    def npc_health_percentage(self):
        """Porcentaje de salud del NPC"""
        if self.npc_max_health <= 0:
            return 0
        return (self.npc_health / self.npc_max_health) * 100
    
    class Meta:
        verbose_name = "Batalla"
        verbose_name_plural = "Batallas"
        ordering = ['-started_at']
    
    def __str__(self):
        if self.defender:
            return f"{self.attacker.captain_name} vs {self.defender.captain_name}"
        return f"{self.attacker.captain_name} vs NPC"
    
    def start_battle(self):
        """Iniciar la batalla"""
        if self.status != 'preparing':
            return False
        
        self.status = 'in_progress'
        
        # Marcar barcos como en combate
        self.attacker_ship.status = 'combat'
        self.attacker_ship.save()
        
        if self.defender_ship:
            self.defender_ship.status = 'combat'
            self.defender_ship.save()
        
        self.save()
        return True
    
    def resolve_battle(self):
        """Resolver el resultado de la batalla"""
        if self.status != 'in_progress':
            return
        
        # Calcular poder de combate de cada lado
        attacker_power = self.calculate_combat_power(self.attacker, self.attacker_ship)
        
        if self.defender and self.defender_ship:
            defender_power = self.calculate_combat_power(self.defender, self.defender_ship)
        else:
            # NPC con poder aleatorio
            defender_power = random.randint(50, 200)
        
        # Determinar ganador
        total_power = attacker_power + defender_power
        attacker_chance = attacker_power / total_power
        
        if random.random() < attacker_chance:
            # Atacante gana
            self.winner = self.attacker
            self.process_victory(self.attacker, self.defender)
        else:
            # Defensor gana
            self.winner = self.defender
            self.process_victory(self.defender, self.attacker)
        
        self.status = 'completed'
        self.completed_at = timezone.now()
        
        # Liberar barcos
        self.attacker_ship.status = 'docked'
        self.attacker_ship.save()
        
        if self.defender_ship:
            self.defender_ship.status = 'docked'
            self.defender_ship.save()
        
        self.save()
    
    def calculate_combat_power(self, player, ship):
        """Calcular poder de combate total"""
        base_power = ship.firepower + ship.defense
        skill_bonus = player.combat_skill * 10
        crew_bonus = ship.crew_count * 2
        health_penalty = (100 - ship.hull_health) * 0.5
        
        total_power = base_power + skill_bonus + crew_bonus - health_penalty
        return max(10, total_power)
    
    def process_victory(self, winner, loser):
        """Procesar victoria y recompensas"""
        # Experiencia base
        base_exp = 100
        level_diff_bonus = 0
        
        if loser:
            level_diff_bonus = max(0, (loser.level - winner.level) * 10)
        
        self.experience_reward = base_exp + level_diff_bonus
        winner.add_experience(self.experience_reward)
        
        # Oro (stakes + bonus)
        gold_reward = self.gold_stakes
        if loser and loser.gold > 0:
            stolen_gold = min(loser.gold, self.gold_stakes // 2)
            loser.gold -= stolen_gold
            gold_reward += stolen_gold
            loser.save()
        
        winner.gold += gold_reward
        
        # Actualizar estadísticas
        winner.total_battles_won += 1
        if loser:
            loser.total_battles_lost += 1
            loser.save()
        
        winner.save()


class CombatTurn(models.Model):
    """Turnos individuales de combate"""
    
    ACTION_TYPES = [
        ('cannon', 'Disparo de Cañón'),
        ('ram', 'Embestida'),
        ('board', 'Abordaje'),
        ('repair', 'Reparación'),
        ('retreat', 'Retirada'),
    ]
    
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name='turns')
    turn_number = models.IntegerField()
    acting_player = models.ForeignKey(Player, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    
    # Resultados del turno
    damage_dealt = models.IntegerField(default=0)
    damage_received = models.IntegerField(default=0)
    description = models.TextField()
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Turno de Combate"
        verbose_name_plural = "Turnos de Combate"
        ordering = ['battle', 'turn_number']
    
    def __str__(self):
        return f"Turno {self.turn_number} - {self.acting_player.captain_name}: {self.get_action_type_display()}"


class PirateFleet(models.Model):
    """Flotas piratas NPC para combate PvE"""
    
    FLEET_TYPES = [
        ('scout', 'Explorador'),
        ('raider', 'Asaltante'),
        ('warship', 'Navío de Guerra'),
        ('flagship', 'Buque Insignia'),
    ]
    
    name = models.CharField(max_length=100)
    fleet_type = models.CharField(max_length=20, choices=FLEET_TYPES)
    
    # Características de combate
    firepower = models.IntegerField()
    defense = models.IntegerField()
    speed = models.IntegerField()
    crew_size = models.IntegerField()
    
    # Nivel y recompensas
    level = models.IntegerField(default=1)
    gold_reward = models.IntegerField()
    experience_reward = models.IntegerField()
    
    # Ubicación
    current_region = models.ForeignKey('exploration.Region', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Estado
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Flota Pirata"
        verbose_name_plural = "Flotas Piratas"
    
    def __str__(self):
        return f"{self.name} ({self.get_fleet_type_display()})"


class CombatEvent(models.Model):
    """Eventos especiales durante el combate"""
    
    EVENT_TYPES = [
        ('critical_hit', 'Golpe Crítico'),
        ('miss', 'Fallo'),
        ('fire', 'Incendio'),
        ('storm', 'Tormenta'),
        ('reinforcements', 'Refuerzos'),
        ('sabotage', 'Sabotaje'),
    ]
    
    name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    
    # Efectos del evento
    damage_modifier = models.FloatField(default=1.0)
    accuracy_modifier = models.FloatField(default=1.0)
    duration_turns = models.IntegerField(default=1)
    
    # Probabilidad de ocurrencia
    probability = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    
    class Meta:
        verbose_name = "Evento de Combate"
        verbose_name_plural = "Eventos de Combate"
    
    def __str__(self):
        return f"{self.name} ({self.get_event_type_display()})"
