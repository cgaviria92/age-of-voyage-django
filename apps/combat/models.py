"""Combat system models for Age of Voyage."""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import json


class CombatAction(models.Model):
    """Available combat actions during battles."""
    
    ACTION_TYPES = [
        ('attack', 'Direct Attack'),
        ('defensive', 'Defensive Maneuver'),
        ('special', 'Special Action'),
        ('flee', 'Attempt to Flee'),
        ('board', 'Boarding Action'),
        ('repair', 'Emergency Repair'),
        ('reload', 'Reload Weapons'),
    ]
    
    name = models.CharField(max_length=100)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    
    # Action effects
    damage_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    defense_bonus = models.IntegerField(default=0)
    speed_bonus = models.IntegerField(default=0)
    accuracy_modifier = models.IntegerField(default=0)
    
    # Requirements
    required_ammunition = models.PositiveIntegerField(default=0)
    required_crew_morale = models.PositiveIntegerField(default=0)
    required_ship_condition = models.PositiveIntegerField(default=0)
    cooldown_turns = models.PositiveIntegerField(default=0)
    
    # Success rates
    base_success_rate = models.PositiveIntegerField(
        default=75,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    class Meta:
        db_table = 'combat_combataction'
        verbose_name = _('Combat Action')
        verbose_name_plural = _('Combat Actions')
    
    def __str__(self):
        return self.name


class AmmunitionType(models.Model):
    """Different types of ammunition for naval combat."""
    
    AMMO_CATEGORIES = [
        ('round_shot', 'Round Shot'),
        ('chain_shot', 'Chain Shot'),
        ('grape_shot', 'Grape Shot'),
        ('incendiary', 'Incendiary Shot'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=AMMO_CATEGORIES)
    description = models.TextField()
    
    # Combat effects
    hull_damage = models.PositiveIntegerField(default=10)
    sail_damage = models.PositiveIntegerField(default=0)
    crew_damage = models.PositiveIntegerField(default=0)
    fire_chance = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    
    # Costs and availability
    gold_cost = models.PositiveIntegerField()
    iron_cost = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'combat_ammunitiontype'
        verbose_name = _('Ammunition Type')
        verbose_name_plural = _('Ammunition Types')
    
    def __str__(self):
        return self.name


class PirateFleet(models.Model):
    """AI-controlled pirate fleets for encounters."""
    
    FLEET_TYPES = [
        ('patrol', 'Patrol Squadron'),
        ('merchant_hunter', 'Merchant Hunter'),
        ('warship', 'Warship'),
        ('flagship', 'Pirate Flagship'),
    ]
    
    DIFFICULTY_LEVELS = [
        (1, 'Novice'),
        (2, 'Experienced'),
        (3, 'Veteran'),
        (4, 'Elite'),
        (5, 'Legendary'),
    ]
    
    name = models.CharField(max_length=100)
    fleet_type = models.CharField(max_length=20, choices=FLEET_TYPES)
    difficulty = models.PositiveIntegerField(choices=DIFFICULTY_LEVELS)
    
    # Fleet composition
    ship_types = models.JSONField(default=list, help_text="List of ship types in the fleet")
    total_ships = models.PositiveIntegerField(default=1)
    
    # Fleet stats
    total_health = models.PositiveIntegerField()
    total_attack = models.PositiveIntegerField()
    total_defense = models.PositiveIntegerField()
    fleet_speed = models.PositiveIntegerField()
    
    # AI behavior
    aggression = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    tactical_intelligence = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Loot
    gold_reward = models.PositiveIntegerField()
    experience_reward = models.PositiveIntegerField()
    special_loot = models.JSONField(default=dict, help_text="Special items and resources")
    
    # Spawn conditions
    spawn_regions = models.ManyToManyField('exploration.WorldRegion', blank=True)
    spawn_chance = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    
    class Meta:
        db_table = 'combat_piratefleet'
        verbose_name = _('Pirate Fleet')
        verbose_name_plural = _('Pirate Fleets')
    
    def __str__(self):
        return f"{self.name} (Level {self.difficulty})"


class Battle(models.Model):
    """Naval battle instances."""
    
    BATTLE_TYPES = [
        ('pirate_encounter', 'Pirate Encounter'),
        ('player_vs_player', 'Player vs Player'),
        ('faction_battle', 'Faction Battle'),
        ('boss_battle', 'Boss Battle'),
    ]
    
    BATTLE_STATUS = [
        ('preparing', 'Preparing'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('fled', 'Player Fled'),
    ]
    
    battle_type = models.CharField(max_length=20, choices=BATTLE_TYPES)
    status = models.CharField(max_length=20, choices=BATTLE_STATUS, default='preparing')
    
    # Participants
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='battles')
    player_ship = models.ForeignKey('ships.Ship', on_delete=models.CASCADE, related_name='battles')
    
    # Enemy (can be pirate fleet or another player)
    enemy_fleet = models.ForeignKey(
        PirateFleet,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='battles'
    )
    enemy_player = models.ForeignKey(
        'players.Player',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='enemy_battles'
    )
    enemy_ship = models.ForeignKey(
        'ships.Ship',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='enemy_battles'
    )
    
    # Battle conditions
    location = models.ForeignKey('exploration.Region', on_delete=models.CASCADE, related_name='battles')
    weather_condition = models.CharField(max_length=50, default='Clear')
    visibility = models.PositiveIntegerField(default=100, validators=[MaxValueValidator(100)])
    
    # Battle state
    current_turn = models.PositiveIntegerField(default=1)
    player_turn = models.BooleanField(default=True)
    
    # Player state
    player_initial_health = models.PositiveIntegerField()
    player_current_health = models.PositiveIntegerField()
    player_ammunition_used = models.PositiveIntegerField(default=0)
    
    # Enemy state
    enemy_initial_health = models.PositiveIntegerField()
    enemy_current_health = models.PositiveIntegerField()
    
    # Results
    winner = models.CharField(max_length=20, blank=True)  # 'player', 'enemy', 'draw'
    experience_gained = models.PositiveIntegerField(default=0)
    loot_gained = models.JSONField(default=dict)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'combat_battle'
        verbose_name = _('Battle')
        verbose_name_plural = _('Battles')
    
    def __str__(self):
        enemy_name = self.enemy_fleet.name if self.enemy_fleet else f"Player {self.enemy_player.captain_name}"
        return f"Battle: {self.player.captain_name} vs {enemy_name}"
    
    def save(self, *args, **kwargs):
        """Initialize health values if new battle."""
        if not self.pk:
            self.player_initial_health = self.player_ship.current_health
            self.player_current_health = self.player_ship.current_health
            
            if self.enemy_fleet:
                self.enemy_initial_health = self.enemy_fleet.total_health
                self.enemy_current_health = self.enemy_fleet.total_health
            elif self.enemy_ship:
                self.enemy_initial_health = self.enemy_ship.current_health
                self.enemy_current_health = self.enemy_ship.current_health
        
        super().save(*args, **kwargs)


class BattleTurn(models.Model):
    """Individual turns within a battle."""
    
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name='turns')
    turn_number = models.PositiveIntegerField()
    is_player_turn = models.BooleanField()
    
    # Action taken
    action = models.ForeignKey(CombatAction, on_delete=models.CASCADE, related_name='battle_turns')
    ammunition_used = models.ForeignKey(
        AmmunitionType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='battle_turns'
    )
    
    # Target (for multi-ship battles)
    target_ship = models.CharField(max_length=100, blank=True)
    
    # Results
    action_successful = models.BooleanField()
    damage_dealt = models.PositiveIntegerField(default=0)
    damage_received = models.PositiveIntegerField(default=0)
    special_effects = models.JSONField(default=dict, help_text="Fire, critical hits, etc.")
    
    # Combat log
    description = models.TextField()
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'combat_battleturn'
        unique_together = ['battle', 'turn_number']
        verbose_name = _('Battle Turn')
        verbose_name_plural = _('Battle Turns')
    
    def __str__(self):
        participant = "Player" if self.is_player_turn else "Enemy"
        return f"Turn {self.turn_number}: {participant} - {self.action.name}"


class CombatEvent(models.Model):
    """Random events that can occur during combat."""
    
    EVENT_TYPES = [
        ('weather', 'Weather Change'),
        ('reinforcement', 'Reinforcements Arrive'),
        ('equipment_failure', 'Equipment Failure'),
        ('crew_event', 'Crew Event'),
        ('environmental', 'Environmental Hazard'),
    ]
    
    name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    
    # Trigger conditions
    trigger_chance = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    min_turn = models.PositiveIntegerField(default=1)
    max_turn = models.PositiveIntegerField(default=20)
    
    # Effects
    effects = models.JSONField(default=dict, help_text="JSON describing the event effects")
    
    class Meta:
        db_table = 'combat_combatevent'
        verbose_name = _('Combat Event')
        verbose_name_plural = _('Combat Events')
    
    def __str__(self):
        return self.name


class BattleEvent(models.Model):
    """Events that occurred during specific battles."""
    
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name='events')
    event = models.ForeignKey(CombatEvent, on_delete=models.CASCADE)
    turn_triggered = models.PositiveIntegerField()
    effects_applied = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'combat_battleevent'
        verbose_name = _('Battle Event')
        verbose_name_plural = _('Battle Events')
    
    def __str__(self):
        return f"{self.battle} - {self.event.name} (Turn {self.turn_triggered})"
