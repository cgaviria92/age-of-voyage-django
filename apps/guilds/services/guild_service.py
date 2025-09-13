"""
GuildService: Lógica de negocio para gremios y membresías.
Reutilizable y desacoplada de las vistas.
"""
from apps.guilds.models import Guild, GuildMembership
from apps.players.models import Player
from django.utils import timezone

class GuildService:
    @staticmethod
    def create_guild(leader: Player, name: str, description: str, motto: str = ""):
        """Crea un nuevo gremio y asigna al líder."""
        guild = Guild.objects.create(
            name=name,
            description=description,
            motto=motto,
            leader=leader
        )
        GuildMembership.objects.create(
            guild=guild,
            player=leader,
            rank='leader',
            joined_at=timezone.now()
        )
        return guild

    @staticmethod
    def join_guild(player: Player, guild: Guild):
        """Agrega un jugador a un gremio si hay espacio y cumple requisitos."""
        if guild.memberships.count() >= guild.max_members:
            return None
        if player.level < guild.required_level:
            return None
        return GuildMembership.objects.create(guild=guild, player=player, rank='member', joined_at=timezone.now())

    @staticmethod
    def leave_guild(player: Player):
        """Elimina la membresía del jugador en su gremio."""
        GuildMembership.objects.filter(player=player).delete()

    @staticmethod
    def promote_member(membership: GuildMembership, new_rank: str):
        """Promueve a un miembro a un nuevo rango."""
        membership.rank = new_rank
        membership.save()
        return membership

    @staticmethod
    def get_guild_members(guild: Guild):
        """Obtiene todos los miembros de un gremio."""
        return guild.memberships.select_related('player').all()
