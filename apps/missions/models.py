from django.db import models
from apps.players.models import Player


class Mission(models.Model):
    """Misiones disponibles para los jugadores"""
    
    MISSION_TYPES = [
        ('exploration', 'Exploración'),
        ('trade', 'Comercio'),
        ('combat', 'Combate'),
        ('delivery', 'Entrega'),
        ('escort', 'Escolta'),
        ('rescue', 'Rescate'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Fácil'),
        ('medium', 'Medio'),
        ('hard', 'Difícil'),
        ('extreme', 'Extremo'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    mission_type = models.CharField(max_length=20, choices=MISSION_TYPES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    
    # Requisitos
    required_level = models.IntegerField(default=1)
    required_ship_type = models.CharField(max_length=50, blank=True)
    
    # Recompensas
    gold_reward = models.IntegerField()
    experience_reward = models.IntegerField()
    
    # Disponibilidad
    is_active = models.BooleanField(default=True)
    max_attempts = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Misión"
        verbose_name_plural = "Misiones"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"


class PlayerMission(models.Model):
    """Misiones asignadas a jugadores"""
    
    STATUS_CHOICES = [
        ('assigned', 'Asignada'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('failed', 'Fallida'),
        ('abandoned', 'Abandonada'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='missions')
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    # Progreso
    progress_percentage = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    
    # Tiempos
    assigned_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Misión del Jugador"
        verbose_name_plural = "Misiones de Jugadores"
        unique_together = ['player', 'mission']
    
    def __str__(self):
        return f"{self.player.captain_name} - {self.mission.title}"
