from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.players.models import Player
import random


class Region(models.Model):
    """Regiones del mundo de Age of Voyage"""
    
    REGION_TYPES = [
        ('island', 'Isla'),
        ('port', 'Puerto'),
        ('ocean', 'Océano Abierto'),
        ('strait', 'Estrecho'),
        ('bay', 'Bahía'),
        ('archipelago', 'Archipiélago'),
        ('reef', 'Arrecife'),
        ('cave', 'Cueva Marina'),
        ('lagoon', 'Laguna'),
        ('atoll', 'Atolón'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Fácil'),
        ('medium', 'Medio'),
        ('hard', 'Difícil'),
        ('extreme', 'Extremo'),
        ('legendary', 'Legendario'),
    ]
    
    CLIMATES = [
        ('tropical', 'Tropical'),
        ('temperate', 'Templado'),
        ('arctic', 'Ártico'),
        ('desert', 'Desértico'),
        ('stormy', 'Tormentoso'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    region_type = models.CharField(max_length=20, choices=REGION_TYPES)
    climate = models.CharField(max_length=20, choices=CLIMATES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    
    # Coordenadas en el mapa del mundo
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()
    
    # Características de exploración
    exploration_cost = models.IntegerField(default=50)
    danger_level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Recompensas potenciales
    base_gold_reward = models.IntegerField(default=0)
    base_experience_reward = models.IntegerField(default=100)
    
    # Requisitos
    required_level = models.IntegerField(default=1)
    required_ship_speed = models.IntegerField(default=0)
    
    # Estado
    is_discovered = models.BooleanField(default=False)
    discoverer = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='discovered_regions')
    discovery_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Región"
        verbose_name_plural = "Regiones"
        ordering = ['difficulty', 'required_level', 'name']
        unique_together = ['x_coordinate', 'y_coordinate']
    
    def __str__(self):
        return f"{self.name} ({self.get_region_type_display()})"
    
    @property
    def exploration_success_rate(self):
        """Tasa de éxito base para exploración"""
        base_rate = max(10, 90 - (self.danger_level * 8))
        return base_rate
    
    def calculate_rewards(self, player_level, ship_speed):
        """Calcular recompensas basadas en nivel del jugador y barco"""
        level_multiplier = 1 + (player_level * 0.1)
        speed_bonus = 1 + (ship_speed * 0.05)
        difficulty_bonus = {'easy': 1, 'medium': 1.5, 'hard': 2, 'extreme': 3, 'legendary': 5}[self.difficulty]
        
        gold_reward = int(self.base_gold_reward * level_multiplier * difficulty_bonus)
        exp_reward = int(self.base_experience_reward * level_multiplier * difficulty_bonus)
        
        return gold_reward, exp_reward


class ExplorationEvent(models.Model):
    """Eventos que pueden ocurrir durante la exploración"""
    
    EVENT_TYPES = [
        ('treasure', 'Tesoro Encontrado'),
        ('storm', 'Tormenta'),
        ('pirates', 'Ataque Pirata'),
        ('merchant', 'Comerciante Encontrado'),
        ('island', 'Isla Secreta'),
        ('monster', 'Monstruo Marino'),
        ('natives', 'Nativos Amigables'),
        ('shipwreck', 'Naufragio'),
        ('whirlpool', 'Remolino'),
        ('calm', 'Aguas Tranquilas'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    
    # Probabilidad de ocurrencia (1-100)
    probability = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    
    # Efectos del evento
    gold_effect = models.IntegerField(default=0)  # Puede ser negativo
    experience_effect = models.IntegerField(default=0)
    hull_damage = models.IntegerField(default=0)  # Daño al barco
    
    # Condiciones para que ocurra
    required_region_type = models.CharField(max_length=20, choices=Region.REGION_TYPES, blank=True)
    required_climate = models.CharField(max_length=20, choices=Region.CLIMATES, blank=True)
    
    class Meta:
        verbose_name = "Evento de Exploración"
        verbose_name_plural = "Eventos de Exploración"
    
    def __str__(self):
        return f"{self.name} ({self.get_event_type_display()})"


class ExplorationMission(models.Model):
    """Misión de exploración de un jugador"""
    
    STATUS_CHOICES = [
        ('preparing', 'Preparando'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('failed', 'Fallida'),
        ('cancelled', 'Cancelada'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='exploration_missions')
    ship = models.ForeignKey('ships.Ship', on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='preparing')
    
    # Tiempos
    started_at = models.DateTimeField(auto_now_add=True)
    estimated_duration = models.DurationField()  # Tiempo estimado de exploración
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Resultados
    gold_earned = models.IntegerField(default=0)
    experience_earned = models.IntegerField(default=0)
    hull_damage_taken = models.IntegerField(default=0)
    events_encountered = models.ManyToManyField(ExplorationEvent, blank=True)
    
    # Notas del resultado
    result_description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Misión de Exploración"
        verbose_name_plural = "Misiones de Exploración"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.player.captain_name} explorando {self.region.name}"
    
    def calculate_duration(self):
        """Calcular duración basada en distancia y velocidad del barco"""
        base_duration = 3600  # 1 hora base
        distance_factor = self.region.danger_level * 0.5
        speed_factor = max(0.1, 1 / (self.ship.speed * 0.1))
        
        duration_seconds = int(base_duration * distance_factor * speed_factor)
        return duration_seconds
    
    def process_exploration(self):
        """Procesar los resultados de la exploración"""
        if self.status != 'in_progress':
            return
        
        # Calcular éxito basado en habilidades del jugador y características del barco
        success_rate = self.region.exploration_success_rate
        navigation_bonus = self.player.navigation_skill * 2
        ship_speed_bonus = self.ship.speed
        
        final_success_rate = min(95, success_rate + navigation_bonus + ship_speed_bonus)
        
        # Determinar si la exploración fue exitosa
        success_roll = random.randint(1, 100)
        is_successful = success_roll <= final_success_rate
        
        if is_successful:
            # Calcular recompensas
            gold_reward, exp_reward = self.region.calculate_rewards(
                self.player.level, 
                self.ship.speed
            )
            
            self.gold_earned = gold_reward
            self.experience_earned = exp_reward
            self.status = 'completed'
            
            # Agregar recompensas al jugador
            self.player.gold += gold_reward
            level_up = self.player.add_experience(exp_reward)
            
            # Marcar región como descubierta si es la primera vez
            if not self.region.is_discovered:
                self.region.is_discovered = True
                self.region.discoverer = self.player
                self.region.discovery_date = self.completed_at
                self.region.save()
                
                # Bonus por descubrimiento
                discovery_bonus = 500
                self.player.gold += discovery_bonus
                self.gold_earned += discovery_bonus
            
            self.result_description = f"¡Exploración exitosa! Descubriste {self.region.name}."
            
        else:
            # Exploración fallida
            self.status = 'failed'
            hull_damage = random.randint(10, 30)
            self.hull_damage_taken = hull_damage
            self.ship.hull_health = max(0, self.ship.hull_health - hull_damage)
            self.ship.save()
            
            self.result_description = f"La exploración falló. Tu barco sufrió {hull_damage} puntos de daño."
        
        # Procesar eventos aleatorios
        self.process_random_events()
        
        # Guardar cambios
        self.player.save()
        self.save()
    
    def process_random_events(self):
        """Procesar eventos aleatorios durante la exploración"""
        possible_events = ExplorationEvent.objects.all()
        
        # Filtrar eventos por tipo de región y clima
        if self.region.region_type:
            possible_events = possible_events.filter(
                models.Q(required_region_type='') | 
                models.Q(required_region_type=self.region.region_type)
            )
        
        if self.region.climate:
            possible_events = possible_events.filter(
                models.Q(required_climate='') | 
                models.Q(required_climate=self.region.climate)
            )
        
        # Determinar qué eventos ocurren
        for event in possible_events:
            event_roll = random.randint(1, 100)
            if event_roll <= event.probability:
                self.events_encountered.add(event)
                
                # Aplicar efectos del evento
                self.gold_earned += event.gold_effect
                self.experience_earned += event.experience_effect
                
                if event.hull_damage > 0:
                    self.hull_damage_taken += event.hull_damage
                    self.ship.hull_health = max(0, self.ship.hull_health - event.hull_damage)
                    self.ship.save()


class RegionResource(models.Model):
    """Recursos disponibles en cada región"""
    
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='resources')
    resource = models.ForeignKey('trade.Resource', on_delete=models.CASCADE)
    abundance = models.CharField(max_length=20, choices=[
        ('rare', 'Raro'),
        ('uncommon', 'Poco Común'),
        ('common', 'Común'),
        ('abundant', 'Abundante'),
    ])
    base_price_modifier = models.FloatField(default=1.0)  # Modificador del precio base
    
    class Meta:
        verbose_name = "Recurso de Región"
        verbose_name_plural = "Recursos de Regiones"
        unique_together = ['region', 'resource']
    
    def __str__(self):
        return f"{self.resource.name} en {self.region.name} ({self.abundance})"
