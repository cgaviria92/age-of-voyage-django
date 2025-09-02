from django.db import models
from apps.players.models import Player
from apps.exploration.models import Region


class BuildingType(models.Model):
    """Tipos de construcciones disponibles"""
    
    BUILDING_CATEGORIES = [
        ('economic', 'Económico'),
        ('military', 'Militar'),
        ('infrastructure', 'Infraestructura'),
        ('residential', 'Residencial'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=BUILDING_CATEGORIES)
    
    # Costos y requisitos
    build_cost = models.IntegerField()
    maintenance_cost = models.IntegerField()
    required_level = models.IntegerField(default=1)
    build_time_hours = models.IntegerField(default=1)
    
    # Beneficios
    gold_production = models.IntegerField(default=0)
    defense_bonus = models.IntegerField(default=0)
    storage_capacity = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Tipo de Construcción"
        verbose_name_plural = "Tipos de Construcciones"
    
    def __str__(self):
        return self.name


class PlayerBuilding(models.Model):
    """Construcciones de los jugadores"""
    
    STATUS_CHOICES = [
        ('planning', 'Planificando'),
        ('building', 'Construyendo'),
        ('completed', 'Completada'),
        ('damaged', 'Dañada'),
    ]
    
    owner = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='buildings')
    building_type = models.ForeignKey(BuildingType, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    level = models.IntegerField(default=1)
    
    # Tiempos
    construction_started = models.DateTimeField(auto_now_add=True)
    completion_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Construcción del Jugador"
        verbose_name_plural = "Construcciones de Jugadores"
    
    def __str__(self):
        return f"{self.building_type.name} de {self.owner.captain_name} en {self.region.name}"
