"""Exploration and world models for Age of Voyage."""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class WorldRegion(models.Model):
    """Major world regions like Caribbean, Atlantic, etc."""
    
    REGION_TYPES = [
        ('caribbean', 'Caribbean'),
        ('atlantic', 'Atlantic'),
        ('mediterranean', 'Mediterranean'),
        ('pacific', 'Pacific'),
        ('arctic', 'Arctic'),
        ('hideout', 'Pirate Hideout'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    region_type = models.CharField(max_length=20, choices=REGION_TYPES)
    description = models.TextField()
    climate = models.CharField(max_length=50)
    danger_level = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    class Meta:
        db_table = 'exploration_worldregion'
        verbose_name = _('World Region')
        verbose_name_plural = _('World Regions')
    
    def __str__(self):
        return self.name


class Region(models.Model):
    """Specific explorable regions/locations."""
    
    LOCATION_TYPES = [
        ('port', 'Port City'),
        ('island', 'Island'),
        ('ocean', 'Open Ocean'),
        ('strait', 'Strait'),
        ('bay', 'Bay'),
        ('reef', 'Reef'),
        ('hideout', 'Pirate Hideout'),
    ]
    
    name = models.CharField(max_length=100)
    world_region = models.ForeignKey(WorldRegion, on_delete=models.CASCADE, related_name='regions')
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES)
    description = models.TextField()
    
    # Geographical data
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    
    # Exploration data
    is_discovered = models.BooleanField(default=False, help_text="Whether this region is known by default")
    discovery_difficulty = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    # Economic data
    has_market = models.BooleanField(default=False)
    has_shipyard = models.BooleanField(default=False)
    has_tavern = models.BooleanField(default=False)
    
    # Safety
    pirate_activity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    weather_risk = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    # Resources available
    available_resources = models.JSONField(default=list, help_text="List of resource types available")
    
    # Image
    image = models.ImageField(upload_to='regions/', blank=True, null=True)
    
    class Meta:
        db_table = 'exploration_region'
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')
        unique_together = ['name', 'world_region']
    
    def __str__(self):
        return f"{self.name} ({self.world_region.name})"
    
    @property
    def coordinates(self):
        """Return coordinates as a tuple."""
        return (float(self.latitude), float(self.longitude))
    
    @property
    def danger_rating(self):
        """Calculate overall danger rating."""
        return (self.pirate_activity + self.weather_risk + self.world_region.danger_level) / 3


class PlayerDiscovery(models.Model):
    """Track which regions each player has discovered."""
    
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='discoveries')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='discovered_by')
    discovered_at = models.DateTimeField(auto_now_add=True)
    exploration_experience_gained = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'exploration_playerdiscovery'
        unique_together = ['player', 'region']
        verbose_name = _('Player Discovery')
        verbose_name_plural = _('Player Discoveries')
    
    def __str__(self):
        return f"{self.player.captain_name} discovered {self.region.name}"


class TravelRoute(models.Model):
    """Defined travel routes between regions."""
    
    from_region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='routes_from')
    to_region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='routes_to')
    distance = models.PositiveIntegerField(help_text="Distance in nautical miles")
    travel_time = models.PositiveIntegerField(help_text="Base travel time in hours")
    difficulty = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    # Route conditions
    requires_navigation_skill = models.PositiveIntegerField(default=1)
    weather_affected = models.BooleanField(default=True)
    pirate_encounters = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'exploration_travelroute'
        unique_together = ['from_region', 'to_region']
        verbose_name = _('Travel Route')
        verbose_name_plural = _('Travel Routes')
    
    def __str__(self):
        return f"{self.from_region.name} → {self.to_region.name}"


class Exploration(models.Model):
    """Player exploration activities."""
    
    EXPLORATION_TYPES = [
        ('survey', 'Survey Area'),
        ('treasure_hunt', 'Treasure Hunt'),
        ('mapping', 'Cartography'),
        ('resource_search', 'Resource Search'),
    ]
    
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='explorations')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='explorations')
    exploration_type = models.CharField(max_length=20, choices=EXPLORATION_TYPES)
    
    # Progress
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Results
    success = models.BooleanField(default=False)
    experience_gained = models.PositiveIntegerField(default=0)
    resources_found = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'exploration_exploration'
        verbose_name = _('Exploration')
        verbose_name_plural = _('Explorations')
    
    def __str__(self):
        return f"{self.player.captain_name} exploring {self.region.name}"
