"""Ship models for Age of Voyage."""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class ShipType(models.Model):
    """Different types of ships available in the game."""
    
    SHIP_CLASSES = [
        ('balandra', 'Balandra'),
        ('bergantin', 'Bergantín'),
        ('fragata', 'Fragata'),
        ('galeon', 'Galeón'),
        ('navio', 'Navío de Línea'),
        ('corsario', 'Corsario'),
    ]
    
    name = models.CharField(max_length=50, choices=SHIP_CLASSES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Base stats
    base_health = models.PositiveIntegerField()
    base_attack = models.PositiveIntegerField()
    base_defense = models.PositiveIntegerField()
    base_speed = models.PositiveIntegerField()
    base_cargo_capacity = models.PositiveIntegerField()
    base_crew_capacity = models.PositiveIntegerField()
    
    # Requirements
    required_level = models.PositiveIntegerField(default=1)
    required_navigation_skill = models.PositiveIntegerField(default=1)
    
    # Costs
    gold_cost = models.PositiveIntegerField()
    wood_cost = models.PositiveIntegerField()
    iron_cost = models.PositiveIntegerField()
    
    # Specialization bonuses
    exploration_bonus = models.PositiveIntegerField(default=0)
    combat_bonus = models.PositiveIntegerField(default=0)
    trade_bonus = models.PositiveIntegerField(default=0)
    speed_bonus = models.PositiveIntegerField(default=0)
    
    # Image
    image = models.ImageField(upload_to='ships/types/', blank=True, null=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    
    class Meta:
        db_table = 'ships_shiptype'
        verbose_name = _('Ship Type')
        verbose_name_plural = _('Ship Types')
    
    def __str__(self):
        return self.display_name


class Ship(models.Model):
    """Individual ship instances owned by players."""
    
    owner = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='ships')
    ship_type = models.ForeignKey(ShipType, on_delete=models.CASCADE)
    
    # Custom naming
    name = models.CharField(max_length=100)
    
    # Current stats (can be modified by upgrades/damage)
    current_health = models.PositiveIntegerField()
    max_health = models.PositiveIntegerField()
    attack = models.PositiveIntegerField()
    defense = models.PositiveIntegerField()
    speed = models.PositiveIntegerField()
    cargo_capacity = models.PositiveIntegerField()
    crew_capacity = models.PositiveIntegerField()
    
    # Current status
    current_crew = models.PositiveIntegerField(default=0)
    crew_morale = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    condition = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Ship condition percentage"
    )
    
    # Location and travel
    current_region = models.ForeignKey(
        'exploration.Region',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ships_present'
    )
    is_traveling = models.BooleanField(default=False)
    travel_destination = models.ForeignKey(
        'exploration.Region',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ships_traveling_to'
    )
    travel_started = models.DateTimeField(null=True, blank=True)
    travel_arrives = models.DateTimeField(null=True, blank=True)
    
    # Cargo
    cargo_gold = models.PositiveIntegerField(default=0)
    cargo_wood = models.PositiveIntegerField(default=0)
    cargo_iron = models.PositiveIntegerField(default=0)
    cargo_food = models.PositiveIntegerField(default=0)
    cargo_ammunition = models.PositiveIntegerField(default=0)
    cargo_spices = models.PositiveIntegerField(default=0)
    cargo_silk = models.PositiveIntegerField(default=0)
    
    # Timestamps
    acquired_at = models.DateTimeField(auto_now_add=True)
    last_maintenance = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ships_ship'
        verbose_name = _('Ship')
        verbose_name_plural = _('Ships')
    
    def __str__(self):
        return f"{self.name} ({self.ship_type.display_name})"
    
    def save(self, *args, **kwargs):
        """Initialize stats from ship type if new ship."""
        if not self.pk:
            self.current_health = self.ship_type.base_health
            self.max_health = self.ship_type.base_health
            self.attack = self.ship_type.base_attack
            self.defense = self.ship_type.base_defense
            self.speed = self.ship_type.base_speed
            self.cargo_capacity = self.ship_type.base_cargo_capacity
            self.crew_capacity = self.ship_type.base_crew_capacity
        super().save(*args, **kwargs)
    
    @property
    def current_cargo_weight(self):
        """Calculate current cargo weight."""
        return (
            self.cargo_gold + self.cargo_wood + self.cargo_iron +
            self.cargo_food + self.cargo_ammunition + self.cargo_spices + self.cargo_silk
        )
    
    @property
    def cargo_space_remaining(self):
        """Calculate remaining cargo space."""
        return max(0, self.cargo_capacity - self.current_cargo_weight)
    
    @property
    def health_percentage(self):
        """Get health as percentage."""
        return (self.current_health / self.max_health) * 100 if self.max_health > 0 else 0
    
    @property
    def is_operational(self):
        """Check if ship is operational."""
        return self.current_health > 0 and self.condition > 0 and self.current_crew > 0
    
    def repair(self, amount=None):
        """Repair the ship."""
        if amount is None:
            amount = self.max_health - self.current_health
        
        self.current_health = min(self.max_health, self.current_health + amount)
        self.condition = min(100, self.condition + (amount * 2))
        self.save()
    
    def take_damage(self, amount):
        """Apply damage to the ship."""
        self.current_health = max(0, self.current_health - amount)
        self.condition = max(0, self.condition - (amount // 2))
        if self.current_health == 0:
            self.crew_morale = max(0, self.crew_morale - 20)
        self.save()
    
    def load_cargo(self, **cargo):
        """Load cargo onto the ship."""
        total_new_cargo = sum(cargo.values())
        if total_new_cargo > self.cargo_space_remaining:
            raise ValueError("Not enough cargo space")
        
        for cargo_type, amount in cargo.items():
            cargo_attr = f"cargo_{cargo_type}"
            if hasattr(self, cargo_attr):
                setattr(self, cargo_attr, getattr(self, cargo_attr) + amount)
        self.save()
    
    def unload_cargo(self, **cargo):
        """Unload cargo from the ship."""
        for cargo_type, amount in cargo.items():
            cargo_attr = f"cargo_{cargo_type}"
            if hasattr(self, cargo_attr):
                current_amount = getattr(self, cargo_attr)
                if current_amount < amount:
                    raise ValueError(f"Not enough {cargo_type} in cargo")
                setattr(self, cargo_attr, current_amount - amount)
        self.save()


class ShipUpgrade(models.Model):
    """Upgrades that can be applied to ships."""
    
    UPGRADE_TYPES = [
        ('hull', 'Hull Reinforcement'),
        ('sails', 'Improved Sails'),
        ('cannons', 'Better Cannons'),
        ('storage', 'Expanded Storage'),
        ('crew_quarters', 'Better Crew Quarters'),
    ]
    
    name = models.CharField(max_length=100)
    upgrade_type = models.CharField(max_length=20, choices=UPGRADE_TYPES)
    description = models.TextField()
    
    # Stat modifiers
    health_bonus = models.IntegerField(default=0)
    attack_bonus = models.IntegerField(default=0)
    defense_bonus = models.IntegerField(default=0)
    speed_bonus = models.IntegerField(default=0)
    cargo_bonus = models.IntegerField(default=0)
    crew_bonus = models.IntegerField(default=0)
    
    # Requirements and costs
    required_level = models.PositiveIntegerField(default=1)
    gold_cost = models.PositiveIntegerField()
    wood_cost = models.PositiveIntegerField(default=0)
    iron_cost = models.PositiveIntegerField(default=0)
    
    # Applicable ship types
    applicable_ship_types = models.ManyToManyField(ShipType, blank=True)
    
    class Meta:
        db_table = 'ships_shipupgrade'
        verbose_name = _('Ship Upgrade')
        verbose_name_plural = _('Ship Upgrades')
    
    def __str__(self):
        return self.name


class ShipUpgradeInstance(models.Model):
    """Applied upgrades on specific ships."""
    
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name='upgrades')
    upgrade = models.ForeignKey(ShipUpgrade, on_delete=models.CASCADE)
    installed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ships_shipupgradeinstance'
        unique_together = ['ship', 'upgrade']
        verbose_name = _('Ship Upgrade Instance')
        verbose_name_plural = _('Ship Upgrade Instances')
    
    def __str__(self):
        return f"{self.ship.name} - {self.upgrade.name}"
