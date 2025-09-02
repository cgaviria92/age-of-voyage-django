from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Player(models.Model):
    """Perfil de jugador extendido para Age of Voyage"""
    
    REPUTATION_CHOICES = [
        ('marine', 'Marina Real'),
        ('merchant', 'Comerciante'),
        ('privateer', 'Corsario'),
        ('pirate', 'Pirata'),
        ('explorer', 'Explorador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    captain_name = models.CharField(max_length=100, unique=True)
    level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(100)])
    experience = models.IntegerField(default=0)
    gold = models.IntegerField(default=1000)
    reputation = models.CharField(max_length=20, choices=REPUTATION_CHOICES, default='merchant')
    
    # Estadísticas del jugador
    total_battles_won = models.IntegerField(default=0)
    total_battles_lost = models.IntegerField(default=0)
    total_trade_profit = models.IntegerField(default=0)
    regions_discovered = models.IntegerField(default=0)
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    
    # Habilidades especializadas
    navigation_skill = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(20)])
    combat_skill = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(20)])
    trade_skill = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(20)])
    leadership_skill = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(20)])
    diplomacy_skill = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(20)])
    
    class Meta:
        verbose_name = "Jugador"
        verbose_name_plural = "Jugadores"
        ordering = ['-level', '-experience']
    
    def __str__(self):
        return f"Capitán {self.captain_name} (Nivel {self.level})"
    
    @property
    def total_battles(self):
        return self.total_battles_won + self.total_battles_lost
    
    @property
    def win_rate(self):
        if self.total_battles == 0:
            return 0
        return round((self.total_battles_won / self.total_battles) * 100, 2)
    
    def add_experience(self, amount):
        """Agregar experiencia y subir de nivel si es necesario"""
        self.experience += amount
        
        # Calcular nuevo nivel (experiencia requerida: nivel * 1000)
        new_level = min(100, self.experience // 1000 + 1)
        if new_level > self.level:
            self.level = new_level
            return True  # Subió de nivel
        return False
    
    def can_afford(self, cost):
        """Verificar si el jugador puede pagar cierto costo"""
        return self.gold >= cost
    
    def spend_gold(self, amount):
        """Gastar oro si es posible"""
        if self.can_afford(amount):
            self.gold -= amount
            return True
        return False


class PlayerAchievement(models.Model):
    """Logros del jugador"""
    
    ACHIEVEMENT_TYPES = [
        ('combat', 'Combate'),
        ('trade', 'Comercio'),
        ('exploration', 'Exploración'),
        ('social', 'Social'),
        ('milestone', 'Hito'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='achievements')
    name = models.CharField(max_length=100)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    earned_at = models.DateTimeField(auto_now_add=True)
    gold_reward = models.IntegerField(default=0)
    experience_reward = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Logro"
        verbose_name_plural = "Logros"
        unique_together = ['player', 'name']
    
    def __str__(self):
        return f"{self.player.captain_name} - {self.name}"


class PlayerSettings(models.Model):
    """Configuraciones del jugador"""
    
    player = models.OneToOneField(Player, on_delete=models.CASCADE, related_name='settings')
    notifications_enabled = models.BooleanField(default=True)
    auto_repair_ships = models.BooleanField(default=False)
    preferred_language = models.CharField(max_length=10, default='es')
    music_enabled = models.BooleanField(default=True)
    sound_effects_enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Configuración de Jugador"
        verbose_name_plural = "Configuraciones de Jugadores"
    
    def __str__(self):
        return f"Configuración de {self.player.captain_name}"
