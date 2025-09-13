"""
TradeService: Lógica de negocio para comercio, rutas y misiones comerciales.
Reutilizable y desacoplada de las vistas.
"""
from apps.trade.models import Resource, TradeRoute, TradeMission, TradeMissionCargo, Market
from apps.players.models import Player
from apps.ships.models import Ship
from django.utils import timezone
import random

class TradeService:
    @staticmethod
    def create_trade_mission(player: Player, ship: Ship, route: TradeRoute, cargo_items: list):
        """Crea una misión comercial y asigna la carga."""
        mission = TradeMission.objects.create(
            player=player,
            ship=ship,
            trade_route=route,
            status='loading',
            initial_investment=sum(item['total_cost'] for item in cargo_items)
        )
        for item in cargo_items:
            TradeMissionCargo.objects.create(
                trade_mission=mission,
                resource=item['resource'],
                quantity=item['quantity'],
                purchase_price=item['purchase_price'],
                total_cost=item['total_cost']
            )
        return mission

    @staticmethod
    def start_mission(mission: TradeMission):
        """Inicia el viaje comercial."""
        return mission.start_journey()

    @staticmethod
    def process_arrival(mission: TradeMission):
        """Procesa la llegada y venta de mercancías."""
        return mission.process_arrival()

    @staticmethod
    def get_market(region):
        """Devuelve el mercado de una región."""
        return Market.objects.get(region=region)

    @staticmethod
    def get_resource_price(resource: Resource, region=None):
        """Obtiene el precio actual de un recurso en una región."""
        return resource.get_current_price(region)

    @staticmethod
    def get_trade_routes(origin=None, destination=None):
        """Obtiene rutas comerciales filtradas por origen/destino."""
        qs = TradeRoute.objects.filter(is_active=True)
        if origin:
            qs = qs.filter(origin=origin)
        if destination:
            qs = qs.filter(destination=destination)
        return qs
