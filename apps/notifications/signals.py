from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.combat.models import Battle
from apps.trade.models import TradeMission
from apps.guilds.models import GuildMembership
from .models import Notification

@receiver(post_save, sender=Battle)
def notify_battle(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.attacker,
            title="¡Nueva batalla iniciada!",
            message=f"Has iniciado una batalla contra {instance.npc_name or instance.defender.captain_name}.",
            notification_type="battle",
            priority="high"
        )
        if instance.defender:
            Notification.objects.create(
                recipient=instance.defender,
                title="¡Has sido atacado!",
                message=f"{instance.attacker.captain_name} ha iniciado una batalla contra ti.",
                notification_type="battle",
                priority="high"
            )

@receiver(post_save, sender=TradeMission)
def notify_trade(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.player,
            title="Misión comercial iniciada",
            message=f"Has iniciado una misión comercial en la ruta {instance.trade_route}.",
            notification_type="trade",
            priority="medium"
        )

@receiver(post_save, sender=GuildMembership)
def notify_guild(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.player,
            title="Unión a gremio",
            message=f"Te has unido al gremio {instance.guild.name} como {instance.get_rank_display()}.",
            notification_type="guild",
            priority="medium"
        )
