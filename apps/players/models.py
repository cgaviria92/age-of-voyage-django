"""Player models for Age of Voyage."""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class Faction(models.Model):
    """Different factions in the game world."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    color = models.CharField(max_length=7, help_text="Hex color code")
    emblem = models.ImageField(upload_to='factions/', blank=True, null=True)
    
    class Meta:
        db_table = 'players_faction'
        verbose_name = _('Faction')
        verbose_name_plural = _('Factions')
    
    def __str__(self):
        return self.name


class Specialization(models.Model):
    """Player specializations/skills."""
    
    SKILL_CHOICES = [
        ('navigation', 'Navigation'),
        ('combat', 'Combat'),
        ('trade', 'Trade'),
        ('exploration', 'Exploration'),
        ('diplomacy', 'Diplomacy'),
    ]
    
    name = models.CharField(max_length=50, choices=SKILL_CHOICES, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    
    class Meta:
        db_table = 'players_specialization'
        verbose_name = _('Specialization')
        verbose_name_plural = _('Specializations')
    
    def __str__(self):
        return self.get_name_display()


class Player(models.Model):
    """Main player/captain model."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='player'
    )
    
    # Captain Identity
    captain_name = models.CharField(max_length=100)
    motto = models.CharField(max_length=200, blank=True)
    flag_design = models.JSONField(default=dict, help_text="Custom flag configuration")
    
    # Progression
    level = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(100)])
    experience = models.PositiveIntegerField(default=0)
    experience_to_next_level = models.PositiveIntegerField(default=100)
    
    # Resources
    gold = models.PositiveIntegerField(default=1000)
    wood = models.PositiveIntegerField(default=100)
    iron = models.PositiveIntegerField(default=50)
    food = models.PositiveIntegerField(default=100)
    ammunition = models.PositiveIntegerField(default=50)
    spices = models.PositiveIntegerField(default=0)
    silk = models.PositiveIntegerField(default=0)
    
    # Location
    current_region = models.ForeignKey(
        'exploration.Region',
        on_delete=models.SET_NULL,
        null=True,
        related_name='current_players'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'players_player'
        verbose_name = _('Player')
        verbose_name_plural = _('Players')
    
    def __str__(self):
        return f"Captain {self.captain_name}"
    
    @property
    def total_resources(self):
        """Calculate total resource value."""
        return {
            'gold': self.gold,
            'wood': self.wood,
            'iron': self.iron,
            'food': self.food,
            'ammunition': self.ammunition,
            'spices': self.spices,
            'silk': self.silk,
        }
    
    def add_experience(self, amount):
        """Add experience and handle level up."""
        self.experience += amount
        while self.experience >= self.experience_to_next_level and self.level < 100:
            self.experience -= self.experience_to_next_level
            self.level += 1
            self.experience_to_next_level = int(self.experience_to_next_level * 1.2)
        self.save()
    
    def can_afford(self, **resources):
        """Check if player can afford the given resources."""
        for resource, amount in resources.items():
            if hasattr(self, resource) and getattr(self, resource) < amount:
                return False
        return True
    
    def spend_resources(self, **resources):
        """Spend resources if affordable."""
        if not self.can_afford(**resources):
            raise ValueError("Insufficient resources")
        
        for resource, amount in resources.items():
            if hasattr(self, resource):
                setattr(self, resource, getattr(self, resource) - amount)
        self.save()


class PlayerSpecialization(models.Model):
    """Player skill levels in different specializations."""
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='specializations')
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    level = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(100)])
    experience = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'players_playerspecialization'
        unique_together = ['player', 'specialization']
        verbose_name = _('Player Specialization')
        verbose_name_plural = _('Player Specializations')
    
    def __str__(self):
        return f"{self.player.captain_name} - {self.specialization.get_name_display()} (Level {self.level})"


class FactionReputation(models.Model):
    """Player reputation with different factions."""
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='faction_reputations')
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    reputation = models.IntegerField(
        default=0,
        validators=[MinValueValidator(-100), MaxValueValidator(100)],
        help_text="Reputation range from -100 (hostile) to +100 (allied)"
    )
    
    class Meta:
        db_table = 'players_factionreputation'
        unique_together = ['player', 'faction']
        verbose_name = _('Faction Reputation')
        verbose_name_plural = _('Faction Reputations')
    
    def __str__(self):
        return f"{self.player.captain_name} - {self.faction.name}: {self.reputation}"
    
    @property
    def reputation_status(self):
        """Get the reputation status as a string."""
        if self.reputation >= 75:
            return "Allied"
        elif self.reputation >= 25:
            return "Friendly"
        elif self.reputation >= -25:
            return "Neutral"
        elif self.reputation >= -75:
            return "Unfriendly"
        else:
            return "Hostile"
