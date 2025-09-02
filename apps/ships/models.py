from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.players.models import Player


class ShipType(models.Model):
    """Tipos de barcos disponibles en Age of Voyage"""
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    
    # Características base
    base_speed = models.IntegerField()
    base_cargo_capacity = models.IntegerField()
    base_firepower = models.IntegerField()
    base_defense = models.IntegerField()
    base_crew_capacity = models.IntegerField()
    
    # Costos
    purchase_cost = models.IntegerField()
    maintenance_cost_per_day = models.IntegerField()
    
    # Requisitos
    required_level = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = "Tipo de Barco"
        verbose_name_plural = "Tipos de Barcos"
        ordering = ['required_level', 'purchase_cost']
    
    def __str__(self):
        return self.name


class Ship(models.Model):
    """Barcos individuales de los jugadores"""
    
    STATUS_CHOICES = [
        ('docked', 'Atracado'),
        ('sailing', 'Navegando'),
        ('exploring', 'Explorando'),
        ('trading', 'Comerciando'),
        ('combat', 'En Combate'),
        ('repairing', 'En Reparación'),
    ]
    
    owner = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='ships')
    ship_type = models.ForeignKey(ShipType, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    # Estado actual
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='docked')
    current_location = models.ForeignKey('exploration.Region', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Características actuales (pueden diferir de las base por mejoras)
    speed = models.IntegerField()
    cargo_capacity = models.IntegerField()
    firepower = models.IntegerField()
    defense = models.IntegerField()
    crew_capacity = models.IntegerField()
    
    # Estado físico
    hull_health = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    crew_count = models.IntegerField(default=0)
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    last_maintenance = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Barco"
        verbose_name_plural = "Barcos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.ship_type.name}) - {self.owner.captain_name}"
    
    @property
    def is_operational(self):
        """Verificar si el barco puede operar"""
        return self.hull_health > 10 and self.crew_count > 0
    
    @property
    def needs_repair(self):
        """Verificar si necesita reparación"""
        return self.hull_health < 80
    
    @property
    def current_cargo_weight(self):
        """Peso actual de la carga"""
        return sum(item.quantity * item.resource.weight for item in self.cargo_items.all())
    
    @property
    def available_cargo_space(self):
        """Espacio de carga disponible"""
        return self.cargo_capacity - self.current_cargo_weight
    
    def repair(self, amount=None):
        """Reparar el barco"""
        if amount is None:
            amount = 100 - self.hull_health
        
        repair_cost = amount * 10  # 10 oro por punto de daño
        
        if self.owner.can_afford(repair_cost):
            self.owner.spend_gold(repair_cost)
            self.hull_health = min(100, self.hull_health + amount)
            self.save()
            self.owner.save()
            return True
        return False
    
    def can_sail_to(self, destination):
        """Verificar si puede navegar a un destino"""
        if not self.is_operational:
            return False, "El barco no está operativo"
        
        if self.status != 'docked':
            return False, "El barco no está atracado"
        
        # Aquí se podría agregar lógica de distancia, etc.
        return True, "Puede navegar"


class ShipUpgrade(models.Model):
    """Mejoras aplicables a los barcos"""
    
    UPGRADE_TYPES = [
        ('speed', 'Velocidad'),
        ('cargo', 'Capacidad de Carga'),
        ('firepower', 'Poder de Fuego'),
        ('defense', 'Defensa'),
        ('crew', 'Capacidad de Tripulación'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    upgrade_type = models.CharField(max_length=20, choices=UPGRADE_TYPES)
    bonus_amount = models.IntegerField()
    cost = models.IntegerField()
    required_level = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = "Mejora de Barco"
        verbose_name_plural = "Mejoras de Barcos"
    
    def __str__(self):
        return f"{self.name} (+{self.bonus_amount} {self.get_upgrade_type_display()})"


class ShipCargo(models.Model):
    """Carga de los barcos"""
    
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name='cargo_items')
    resource = models.ForeignKey('trade.Resource', on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    
    class Meta:
        verbose_name = "Carga de Barco"
        verbose_name_plural = "Cargas de Barcos"
        unique_together = ['ship', 'resource']
    
    def __str__(self):
        return f"{self.ship.name} - {self.quantity} {self.resource.name}"


class CrewMember(models.Model):
    """Miembros de la tripulación"""
    
    CREW_TYPES = [
        ('sailor', 'Marinero'),
        ('gunner', 'Artillero'),
        ('navigator', 'Navegante'),
        ('carpenter', 'Carpintero'),
        ('cook', 'Cocinero'),
        ('quartermaster', 'Contramaestre'),
    ]
    
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name='crew_members')
    name = models.CharField(max_length=100)
    crew_type = models.CharField(max_length=20, choices=CREW_TYPES)
    skill_level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    salary_per_day = models.IntegerField()
    hired_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tripulante"
        verbose_name_plural = "Tripulantes"
    
    def __str__(self):
        return f"{self.name} ({self.get_crew_type_display()}) - {self.ship.name}"
