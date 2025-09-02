from django.db import models
from apps.players.models import Player


class Notification(models.Model):
    """Sistema de notificaciones para jugadores"""
    
    NOTIFICATION_TYPES = [
        ('mission', 'Misión'),
        ('battle', 'Batalla'),
        ('trade', 'Comercio'),
        ('guild', 'Gremio'),
        ('system', 'Sistema'),
        ('achievement', 'Logro'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    recipient = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    
    # Estado
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    # Enlaces
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.captain_name} - {self.title}"
    
    def mark_as_read(self):
        """Marcar notificación como leída"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
