"""
BuildingService: Lógica de negocio para construcciones y mejoras.
Reutilizable y desacoplada de las vistas.
"""
from apps.buildings.models import BuildingType, PlayerBuilding
from apps.players.models import Player
from apps.exploration.models import Region
from django.utils import timezone

class BuildingService:
    @staticmethod
    def create_building(owner: Player, building_type: BuildingType, region: Region):
        """Crea una nueva construcción para el jugador."""
        building = PlayerBuilding.objects.create(
            owner=owner,
            building_type=building_type,
            region=region,
            status='building',
            construction_started=timezone.now()
        )
        return building

    @staticmethod
    def complete_building(building: PlayerBuilding):
        """Marca la construcción como completada."""
        building.status = 'completed'
        building.completion_time = timezone.now()
        building.save()
        return building

    @staticmethod
    def upgrade_building(building: PlayerBuilding):
        """Mejora el nivel de la construcción."""
        building.level += 1
        building.save()
        return building

    @staticmethod
    def get_player_buildings(player: Player):
        """Obtiene todas las construcciones de un jugador."""
        return PlayerBuilding.objects.filter(owner=player)
