from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.players.models import Player
from apps.exploration.models import Region
import random
from datetime import datetime, timedelta


class Resource(models.Model):
    """Recursos comerciables en Age of Voyage"""
    
    RESOURCE_CATEGORIES = [
        ('luxury', 'Artículos de Lujo'),
        ('spices', 'Especias'),
        ('precious', 'Metales Preciosos'),
        ('textiles', 'Textiles'),
        ('weapons', 'Armas'),
        ('food', 'Alimentos'),
        ('raw_materials', 'Materias Primas'),
        ('exotic', 'Productos Exóticos'),
        ('contraband', 'Contrabando'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=RESOURCE_CATEGORIES)
    
    # Características físicas
    weight = models.IntegerField(help_text="Peso por unidad")
    base_price = models.IntegerField(help_text="Precio base por unidad")
    
    # Volatilidad del precio (cuánto puede fluctuar)
    price_volatility = models.FloatField(default=0.2, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Requisitos para comerciar
    required_level = models.IntegerField(default=1)
    is_legal = models.BooleanField(default=True, help_text="¿Es legal comerciar con este recurso?")
    
    class Meta:
        verbose_name = "Recurso"
        verbose_name_plural = "Recursos"
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def get_current_price(self, region=None):
        """Obtener precio actual del recurso, opcionalmente en una región específica"""
        base = self.base_price
        
        # Fluctuación temporal (basada en la hora actual)
        time_factor = random.uniform(0.8, 1.2)
        
        # Factor de región si se especifica
        region_factor = 1.0
        if region:
            # Buscar si hay modificador específico para esta región
            try:
                region_resource = region.resources.get(resource=self)
                region_factor = region_resource.base_price_modifier
            except:
                region_factor = random.uniform(0.7, 1.3)
        
        # Aplicar volatilidad
        volatility_factor = random.uniform(1 - self.price_volatility, 1 + self.price_volatility)
        
        final_price = int(base * time_factor * region_factor * volatility_factor)
        return max(1, final_price)


class TradeRoute(models.Model):
    """Rutas comerciales entre regiones"""
    
    origin = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='trade_routes_origin')
    destination = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='trade_routes_destination')
    
    # Características de la ruta
    distance = models.IntegerField(help_text="Distancia en millas náuticas")
    danger_level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    base_travel_time = models.DurationField(help_text="Tiempo base de viaje")
    
    # Requisitos
    required_ship_speed = models.IntegerField(default=0)
    required_level = models.IntegerField(default=1)
    
    # Estado
    is_active = models.BooleanField(default=True)
    discovery_date = models.DateTimeField(auto_now_add=True)
    discovered_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Ruta Comercial"
        verbose_name_plural = "Rutas Comerciales"
        unique_together = ['origin', 'destination']
    
    def __str__(self):
        return f"{self.origin.name} → {self.destination.name}"
    
    def calculate_travel_time(self, ship_speed):
        """Calcular tiempo de viaje basado en velocidad del barco"""
        speed_factor = max(0.1, ship_speed / 10.0)
        adjusted_time = self.base_travel_time / speed_factor
        return adjusted_time
    
    def calculate_profit_potential(self, resource, quantity):
        """Calcular potencial de ganancia para un recurso"""
        origin_price = resource.get_current_price(self.origin)
        destination_price = resource.get_current_price(self.destination)
        
        profit_per_unit = destination_price - origin_price
        total_profit = profit_per_unit * quantity
        
        # Factor de riesgo basado en el peligro de la ruta
        risk_factor = 1 - (self.danger_level * 0.05)
        expected_profit = total_profit * risk_factor
        
        return {
            'origin_price': origin_price,
            'destination_price': destination_price,
            'profit_per_unit': profit_per_unit,
            'total_profit': total_profit,
            'expected_profit': expected_profit,
            'risk_factor': risk_factor,
        }


class TradeMission(models.Model):
    """Misión comercial de un jugador"""
    
    STATUS_CHOICES = [
        ('planning', 'Planificando'),
        ('loading', 'Cargando'),
        ('traveling', 'Viajando'),
        ('selling', 'Vendiendo'),
        ('returning', 'Regresando'),
        ('completed', 'Completada'),
        ('failed', 'Fallida'),
        ('cancelled', 'Cancelada'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='trade_missions')
    ship = models.ForeignKey('ships.Ship', on_delete=models.CASCADE)
    trade_route = models.ForeignKey(TradeRoute, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    
    # Tiempos
    started_at = models.DateTimeField(auto_now_add=True)
    departure_time = models.DateTimeField(null=True, blank=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Finanzas
    initial_investment = models.IntegerField(default=0)
    final_profit = models.IntegerField(default=0)
    total_expenses = models.IntegerField(default=0)
    
    # Eventos durante el viaje
    events_log = models.TextField(blank=True)
    hull_damage_taken = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Misión Comercial"
        verbose_name_plural = "Misiones Comerciales"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.player.captain_name} - {self.trade_route} ({self.get_status_display()})"
    
    def calculate_estimated_profit(self):
        """Calcular ganancia estimada basada en la carga actual"""
        total_estimated = 0
        
        for cargo_item in self.cargo_items.all():
            route_profit = self.trade_route.calculate_profit_potential(
                cargo_item.resource, 
                cargo_item.quantity
            )
            total_estimated += route_profit['expected_profit']
        
        return total_estimated
    
    def start_journey(self):
        """Iniciar el viaje comercial"""
        if self.status != 'loading':
            return False
        
        # Verificar que el barco tiene carga
        if not self.cargo_items.exists():
            return False
        
        self.status = 'traveling'
        self.departure_time = datetime.now()
        
        # Calcular tiempo estimado de llegada
        travel_time = self.trade_route.calculate_travel_time(self.ship.speed)
        self.estimated_arrival = self.departure_time + travel_time
        
        # Marcar barco como ocupado
        self.ship.status = 'trading'
        self.ship.save()
        
        self.save()
        return True
    
    def process_arrival(self):
        """Procesar llegada al destino y venta de mercancías"""
        if self.status != 'traveling':
            return
        
        if datetime.now() < self.estimated_arrival:
            return  # Aún no ha llegado
        
        self.status = 'selling'
        
        # Procesar venta de cada item de carga
        total_revenue = 0
        
        for cargo_item in self.cargo_items.all():
            current_price = cargo_item.resource.get_current_price(self.trade_route.destination)
            revenue = current_price * cargo_item.quantity
            total_revenue += revenue
            
            # Registrar la venta
            cargo_item.selling_price = current_price
            cargo_item.total_revenue = revenue
            cargo_item.save()
        
        # Calcular ganancia neta
        self.final_profit = total_revenue - self.initial_investment - self.total_expenses
        
        # Agregar ganancia al jugador
        self.player.gold += total_revenue
        
        # Experiencia por comercio exitoso
        base_exp = 50
        distance_bonus = self.trade_route.distance // 10
        danger_bonus = self.trade_route.danger_level * 10
        profit_bonus = max(0, self.final_profit // 100)
        
        total_exp = base_exp + distance_bonus + danger_bonus + profit_bonus
        self.player.add_experience(total_exp)
        
        # Actualizar estadísticas del jugador
        self.player.total_trade_profit += max(0, self.final_profit)
        
        # Marcar como completada
        self.status = 'completed'
        self.completed_at = datetime.now()
        
        # Liberar el barco
        self.ship.status = 'docked'
        self.ship.save()
        
        self.player.save()
        self.save()


class TradeMissionCargo(models.Model):
    """Carga específica de una misión comercial"""
    
    trade_mission = models.ForeignKey(TradeMission, on_delete=models.CASCADE, related_name='cargo_items')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Precios de compra y venta
    purchase_price = models.IntegerField()
    selling_price = models.IntegerField(null=True, blank=True)
    total_cost = models.IntegerField()
    total_revenue = models.IntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Carga de Misión Comercial"
        verbose_name_plural = "Cargas de Misiones Comerciales"
        unique_together = ['trade_mission', 'resource']
    
    def __str__(self):
        return f"{self.quantity} {self.resource.name} - {self.trade_mission}"
    
    @property
    def profit_per_unit(self):
        if self.selling_price:
            return self.selling_price - self.purchase_price
        return 0
    
    @property
    def total_profit(self):
        if self.total_revenue:
            return self.total_revenue - self.total_cost
        return 0


class Market(models.Model):
    """Mercado de una región específica"""
    
    region = models.OneToOneField(Region, on_delete=models.CASCADE, related_name='market')
    
    # Características del mercado
    size = models.CharField(max_length=20, choices=[
        ('small', 'Pequeño'),
        ('medium', 'Mediano'),
        ('large', 'Grande'),
        ('metropolis', 'Metrópolis'),
    ], default='medium')
    
    # Especialización del mercado
    specialization = models.CharField(max_length=20, choices=Resource.RESOURCE_CATEGORIES, blank=True)
    
    # Estado del mercado
    prosperity_level = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Mercado"
        verbose_name_plural = "Mercados"
    
    def __str__(self):
        return f"Mercado de {self.region.name}"
    
    def get_demand_modifier(self, resource):
        """Obtener modificador de demanda para un recurso específico"""
        base_modifier = 1.0
        
        # Bonus si el mercado se especializa en esta categoría
        if self.specialization == resource.category:
            base_modifier += 0.3
        
        # Factor de prosperidad
        prosperity_factor = self.prosperity_level / 100.0
        base_modifier *= (0.5 + prosperity_factor)
        
        return base_modifier
    
    def update_prosperity(self, trade_volume):
        """Actualizar nivel de prosperidad basado en volumen de comercio"""
        # El comercio aumenta la prosperidad
        prosperity_increase = min(5, trade_volume // 1000)
        self.prosperity_level = min(100, self.prosperity_level + prosperity_increase)
        self.save()


class PriceHistory(models.Model):
    """Historial de precios de recursos"""
    
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='price_history')
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    price = models.IntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Historial de Precios"
        verbose_name_plural = "Historiales de Precios"
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.resource.name} en {self.region.name}: {self.price} oro"
