from django.db import models
from apps.players.models import Player


class Guild(models.Model):
    """Gremios de jugadores"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    motto = models.CharField(max_length=200, blank=True)
    
    # Liderazgo
    leader = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='led_guild')
    
    # Configuración
    max_members = models.IntegerField(default=50)
    is_open = models.BooleanField(default=True)
    required_level = models.IntegerField(default=1)
    
    # Recursos del gremio
    guild_gold = models.IntegerField(default=0)
    guild_experience = models.IntegerField(default=0)
    guild_level = models.IntegerField(default=1)
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Gremio"
        verbose_name_plural = "Gremios"
        ordering = ['-guild_level', '-guild_experience']
    
    def __str__(self):
        return self.name


class GuildMembership(models.Model):
    """Membresía de jugadores en gremios"""
    
    RANK_CHOICES = [
        ('member', 'Miembro'),
        ('officer', 'Oficial'),
        ('lieutenant', 'Teniente'),
        ('captain', 'Capitán'),
        ('admiral', 'Almirante'),
        ('leader', 'Líder'),
    ]
    
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='memberships')
    player = models.OneToOneField(Player, on_delete=models.CASCADE, related_name='guild_membership')
    rank = models.CharField(max_length=20, choices=RANK_CHOICES, default='member')
    
    # Contribuciones
    gold_contributed = models.IntegerField(default=0)
    experience_contributed = models.IntegerField(default=0)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Membresía de Gremio"
        verbose_name_plural = "Membresías de Gremios"
    
    def __str__(self):
        return f"{self.player.captain_name} en {self.guild.name} ({self.get_rank_display()})"
