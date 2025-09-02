"""
Comando personalizado para poblar la base de datos con datos iniciales del juego
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.players.models import Player
from apps.ships.models import ShipType
from apps.exploration.models import Region, ExplorationEvent
from apps.trade.models import Resource
from apps.combat.models import PirateFleet
from apps.missions.models import Mission


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos iniciales de Age of Voyage'

    def handle(self, *args, **options):
        self.stdout.write('🚢 Iniciando población de Age of Voyage...')
        
        # Crear tipos de barcos
        self.create_ship_types()
        
        # Crear regiones del mundo
        self.create_regions()
        
        # Crear recursos comerciales
        self.create_resources()
        
        # Crear eventos de exploración
        self.create_exploration_events()
        
        # Crear flotas piratas
        self.create_pirate_fleets()
        
        # Crear misiones
        self.create_missions()
        
        # Crear jugador administrador
        self.create_admin_player()
        
        self.stdout.write(
            self.style.SUCCESS('🎉 ¡Age of Voyage poblado exitosamente!')
        )

    def create_ship_types(self):
        ship_types = [
            {
                'name': 'Balandra',
                'description': 'Embarcación rápida y ágil, perfecta para exploración.',
                'base_speed': 12,
                'base_cargo_capacity': 50,
                'base_firepower': 20,
                'base_defense': 15,
                'base_crew_capacity': 15,
                'purchase_cost': 800,
                'maintenance_cost_per_day': 5,
                'required_level': 1,
            },
            {
                'name': 'Corsario',
                'description': 'Barco de guerra ligero, especializado en ataques rápidos.',
                'base_speed': 10,
                'base_cargo_capacity': 40,
                'base_firepower': 35,
                'base_defense': 25,
                'base_crew_capacity': 20,
                'purchase_cost': 1500,
                'maintenance_cost_per_day': 8,
                'required_level': 5,
            },
            {
                'name': 'Fragata',
                'description': 'Embarcación versátil para combate y comercio.',
                'base_speed': 8,
                'base_cargo_capacity': 80,
                'base_firepower': 45,
                'base_defense': 40,
                'base_crew_capacity': 35,
                'purchase_cost': 3000,
                'maintenance_cost_per_day': 15,
                'required_level': 10,
            },
            {
                'name': 'Galeón',
                'description': 'Imponente nave de carga con gran capacidad.',
                'base_speed': 6,
                'base_cargo_capacity': 200,
                'base_firepower': 30,
                'base_defense': 50,
                'base_crew_capacity': 50,
                'purchase_cost': 5000,
                'maintenance_cost_per_day': 25,
                'required_level': 15,
            },
            {
                'name': 'Bergantín',
                'description': 'Equilibrio perfecto entre velocidad y capacidad.',
                'base_speed': 9,
                'base_cargo_capacity': 120,
                'base_firepower': 40,
                'base_defense': 35,
                'base_crew_capacity': 40,
                'purchase_cost': 4000,
                'maintenance_cost_per_day': 20,
                'required_level': 12,
            },
            {
                'name': 'Navío de Línea',
                'description': 'El barco de guerra más poderoso de los mares.',
                'base_speed': 5,
                'base_cargo_capacity': 100,
                'base_firepower': 80,
                'base_defense': 70,
                'base_crew_capacity': 80,
                'purchase_cost': 10000,
                'maintenance_cost_per_day': 50,
                'required_level': 25,
            },
        ]
        
        for ship_data in ship_types:
            ship_type, created = ShipType.objects.get_or_create(
                name=ship_data['name'],
                defaults=ship_data
            )
            if created:
                self.stdout.write(f'⚓ Creado tipo de barco: {ship_type.name}')

    def create_regions(self):
        regions = [
            # Caribe (30 regiones)
            {'name': 'Puerto Real, Jamaica', 'region_type': 'port', 'climate': 'tropical', 'difficulty': 'easy', 'x': 100, 'y': 200, 'required_level': 1},
            {'name': 'Tortuga', 'region_type': 'island', 'climate': 'tropical', 'difficulty': 'medium', 'x': 120, 'y': 180, 'required_level': 3},
            {'name': 'La Habana, Cuba', 'region_type': 'port', 'climate': 'tropical', 'difficulty': 'easy', 'x': 80, 'y': 160, 'required_level': 1},
            {'name': 'Cartagena', 'region_type': 'port', 'climate': 'tropical', 'difficulty': 'medium', 'x': 70, 'y': 220, 'required_level': 5},
            {'name': 'Nassau, Bahamas', 'region_type': 'port', 'climate': 'tropical', 'difficulty': 'easy', 'x': 110, 'y': 140, 'required_level': 2},
            {'name': 'Barbados', 'region_type': 'island', 'climate': 'tropical', 'difficulty': 'medium', 'x': 160, 'y': 200, 'required_level': 4},
            {'name': 'Martinica', 'region_type': 'island', 'climate': 'tropical', 'difficulty': 'medium', 'x': 150, 'y': 190, 'required_level': 6},
            {'name': 'Puerto Príncipe', 'region_type': 'port', 'climate': 'tropical', 'difficulty': 'hard', 'x': 130, 'y': 170, 'required_level': 8},
            {'name': 'Vera Cruz', 'region_type': 'port', 'climate': 'tropical', 'difficulty': 'medium', 'x': 40, 'y': 180, 'required_level': 7},
            {'name': 'Isla del Coco', 'region_type': 'island', 'climate': 'tropical', 'difficulty': 'hard', 'x': 20, 'y': 240, 'required_level': 10},
            
            # Atlántico (25 regiones)
            {'name': 'Lisboa', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'easy', 'x': 300, 'y': 100, 'required_level': 1},
            {'name': 'Sevilla', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'easy', 'x': 280, 'y': 120, 'required_level': 2},
            {'name': 'Cádiz', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'easy', 'x': 270, 'y': 130, 'required_level': 1},
            {'name': 'Plymouth', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'medium', 'x': 320, 'y': 60, 'required_level': 5},
            {'name': 'Amsterdam', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'medium', 'x': 340, 'y': 70, 'required_level': 6},
            {'name': 'Azores', 'region_type': 'archipelago', 'climate': 'temperate', 'difficulty': 'medium', 'x': 260, 'y': 110, 'required_level': 4},
            {'name': 'Canarias', 'region_type': 'archipelago', 'climate': 'temperate', 'difficulty': 'easy', 'x': 250, 'y': 140, 'required_level': 3},
            {'name': 'Cabo Verde', 'region_type': 'archipelago', 'climate': 'tropical', 'difficulty': 'medium', 'x': 240, 'y': 180, 'required_level': 7},
            {'name': 'Costa de Oro', 'region_type': 'port', 'climate': 'tropical', 'difficulty': 'hard', 'x': 290, 'y': 200, 'required_level': 12},
            {'name': 'Estrecho de Gibraltar', 'region_type': 'strait', 'climate': 'temperate', 'difficulty': 'medium', 'x': 275, 'y': 125, 'required_level': 8},
            
            # Mediterráneo (20 regiones)
            {'name': 'Barcelona', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'easy', 'x': 380, 'y': 120, 'required_level': 3},
            {'name': 'Génova', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'medium', 'x': 390, 'y': 110, 'required_level': 5},
            {'name': 'Venecia', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'medium', 'x': 410, 'y': 105, 'required_level': 6},
            {'name': 'Nápoles', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'medium', 'x': 400, 'y': 130, 'required_level': 7},
            {'name': 'Palermo', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'medium', 'x': 395, 'y': 140, 'required_level': 6},
            {'name': 'Malta', 'region_type': 'island', 'climate': 'temperate', 'difficulty': 'hard', 'x': 405, 'y': 145, 'required_level': 10},
            {'name': 'Creta', 'region_type': 'island', 'climate': 'temperate', 'difficulty': 'hard', 'x': 450, 'y': 140, 'required_level': 12},
            {'name': 'Chipre', 'region_type': 'island', 'climate': 'temperate', 'difficulty': 'medium', 'x': 460, 'y': 135, 'required_level': 8},
            {'name': 'Constantinopla', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'hard', 'x': 470, 'y': 120, 'required_level': 15},
            {'name': 'Alejandría', 'region_type': 'port', 'climate': 'desert', 'difficulty': 'hard', 'x': 480, 'y': 150, 'required_level': 13},
            
            # Pacífico (25 regiones) 
            {'name': 'Acapulco', 'region_type': 'port', 'climate': 'tropical', 'difficulty': 'medium', 'x': 50, 'y': 170, 'required_level': 8},
            {'name': 'Callao, Perú', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'medium', 'x': 60, 'y': 280, 'required_level': 10},
            {'name': 'Valparaíso', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'hard', 'x': 70, 'y': 320, 'required_level': 12},
            {'name': 'Islas Galápagos', 'region_type': 'archipelago', 'climate': 'tropical', 'difficulty': 'hard', 'x': 30, 'y': 260, 'required_level': 15},
            {'name': 'Tahití', 'region_type': 'island', 'climate': 'tropical', 'difficulty': 'extreme', 'x': 150, 'y': 300, 'required_level': 20},
            {'name': 'Isla de Pascua', 'region_type': 'island', 'climate': 'temperate', 'difficulty': 'extreme', 'x': 100, 'y': 330, 'required_level': 22},
            {'name': 'Hawái', 'region_type': 'archipelago', 'climate': 'tropical', 'difficulty': 'extreme', 'x': 200, 'y': 160, 'required_level': 18},
            {'name': 'Islas Filipinas', 'region_type': 'archipelago', 'climate': 'tropical', 'difficulty': 'extreme', 'x': 500, 'y': 200, 'required_level': 25},
            {'name': 'Macao', 'region_type': 'port', 'climate': 'tropical', 'difficulty': 'hard', 'x': 520, 'y': 180, 'required_level': 20},
            {'name': 'Nagasaki', 'region_type': 'port', 'climate': 'temperate', 'difficulty': 'extreme', 'x': 550, 'y': 140, 'required_level': 30},
            
            # Ártico (15 regiones)
            {'name': 'Groenlandia', 'region_type': 'island', 'climate': 'arctic', 'difficulty': 'extreme', 'x': 200, 'y': 20, 'required_level': 25},
            {'name': 'Islandia', 'region_type': 'island', 'climate': 'arctic', 'difficulty': 'hard', 'x': 300, 'y': 30, 'required_level': 18},
            {'name': 'Spitsbergen', 'region_type': 'archipelago', 'climate': 'arctic', 'difficulty': 'extreme', 'x': 350, 'y': 10, 'required_level': 30},
            {'name': 'Paso del Noroeste', 'region_type': 'strait', 'climate': 'arctic', 'difficulty': 'legendary', 'x': 150, 'y': 10, 'required_level': 35},
            {'name': 'Tierra de Baffin', 'region_type': 'island', 'climate': 'arctic', 'difficulty': 'extreme', 'x': 180, 'y': 25, 'required_level': 28},
            
            # Refugios Piratas (5 regiones secretas)
            {'name': 'Isla Tortuga Secreta', 'region_type': 'cave', 'climate': 'tropical', 'difficulty': 'legendary', 'x': 125, 'y': 185, 'required_level': 40},
            {'name': 'Refugio de Barbanegra', 'region_type': 'lagoon', 'climate': 'tropical', 'difficulty': 'legendary', 'x': 115, 'y': 145, 'required_level': 35},
            {'name': 'Cueva del Tesoro Maldito', 'region_type': 'cave', 'climate': 'tropical', 'difficulty': 'legendary', 'x': 45, 'y': 245, 'required_level': 45},
            {'name': 'Atolón Fantasma', 'region_type': 'atoll', 'climate': 'tropical', 'difficulty': 'legendary', 'x': 175, 'y': 275, 'required_level': 50},
            {'name': 'Puerto de los Condenados', 'region_type': 'port', 'climate': 'stormy', 'difficulty': 'legendary', 'x': 500, 'y': 300, 'required_level': 60},
        ]
        
        for region_data in regions:
            region, created = Region.objects.get_or_create(
                name=region_data['name'],
                defaults=region_data
            )
            if created:
                self.stdout.write(f'🗺️ Creada región: {region.name}')

    def create_resources(self):
        resources = [
            # Artículos de Lujo
            {'name': 'Perlas', 'category': 'luxury', 'weight': 1, 'base_price': 200, 'price_volatility': 0.3},
            {'name': 'Seda', 'category': 'luxury', 'weight': 2, 'base_price': 150, 'price_volatility': 0.25},
            {'name': 'Joyas', 'category': 'luxury', 'weight': 1, 'base_price': 500, 'price_volatility': 0.4},
            {'name': 'Perfumes', 'category': 'luxury', 'weight': 1, 'base_price': 100, 'price_volatility': 0.2},
            
            # Especias
            {'name': 'Pimienta Negra', 'category': 'spices', 'weight': 1, 'base_price': 50, 'price_volatility': 0.3},
            {'name': 'Canela', 'category': 'spices', 'weight': 1, 'base_price': 75, 'price_volatility': 0.35},
            {'name': 'Clavo de Olor', 'category': 'spices', 'weight': 1, 'base_price': 80, 'price_volatility': 0.4},
            {'name': 'Nuez Moscada', 'category': 'spices', 'weight': 1, 'base_price': 90, 'price_volatility': 0.45},
            
            # Metales Preciosos
            {'name': 'Oro', 'category': 'precious', 'weight': 5, 'base_price': 1000, 'price_volatility': 0.15},
            {'name': 'Plata', 'category': 'precious', 'weight': 3, 'base_price': 300, 'price_volatility': 0.2},
            {'name': 'Cobre', 'category': 'precious', 'weight': 8, 'base_price': 50, 'price_volatility': 0.25},
            
            # Textiles
            {'name': 'Algodón', 'category': 'textiles', 'weight': 3, 'base_price': 30, 'price_volatility': 0.2},
            {'name': 'Lana', 'category': 'textiles', 'weight': 4, 'base_price': 40, 'price_volatility': 0.15},
            {'name': 'Lino', 'category': 'textiles', 'weight': 2, 'base_price': 60, 'price_volatility': 0.25},
            
            # Armas
            {'name': 'Mosquetes', 'category': 'weapons', 'weight': 10, 'base_price': 200, 'price_volatility': 0.3},
            {'name': 'Cañones', 'category': 'weapons', 'weight': 50, 'base_price': 1500, 'price_volatility': 0.2},
            {'name': 'Pólvora', 'category': 'weapons', 'weight': 5, 'base_price': 100, 'price_volatility': 0.4},
            {'name': 'Espadas', 'category': 'weapons', 'weight': 3, 'base_price': 80, 'price_volatility': 0.25},
            
            # Alimentos
            {'name': 'Azúcar', 'category': 'food', 'weight': 2, 'base_price': 25, 'price_volatility': 0.3},
            {'name': 'Café', 'category': 'food', 'weight': 1, 'base_price': 35, 'price_volatility': 0.35},
            {'name': 'Cacao', 'category': 'food', 'weight': 2, 'base_price': 45, 'price_volatility': 0.4},
            {'name': 'Tabaco', 'category': 'food', 'weight': 1, 'base_price': 60, 'price_volatility': 0.3},
            
            # Materias Primas
            {'name': 'Madera', 'category': 'raw_materials', 'weight': 20, 'base_price': 15, 'price_volatility': 0.2},
            {'name': 'Hierro', 'category': 'raw_materials', 'weight': 15, 'base_price': 40, 'price_volatility': 0.25},
            {'name': 'Alquitrán', 'category': 'raw_materials', 'weight': 8, 'base_price': 20, 'price_volatility': 0.3},
            
            # Productos Exóticos
            {'name': 'Marfil', 'category': 'exotic', 'weight': 10, 'base_price': 400, 'price_volatility': 0.5},
            {'name': 'Ámbar', 'category': 'exotic', 'weight': 1, 'base_price': 250, 'price_volatility': 0.6},
            {'name': 'Plumas Exóticas', 'category': 'exotic', 'weight': 1, 'base_price': 120, 'price_volatility': 0.4},
            
            # Contrabando
            {'name': 'Opio', 'category': 'contraband', 'weight': 2, 'base_price': 300, 'price_volatility': 0.8, 'is_legal': False},
            {'name': 'Esclavos', 'category': 'contraband', 'weight': 0, 'base_price': 500, 'price_volatility': 0.7, 'is_legal': False, 'required_level': 10},
        ]
        
        for resource_data in resources:
            resource, created = Resource.objects.get_or_create(
                name=resource_data['name'],
                defaults=resource_data
            )
            if created:
                self.stdout.write(f'💰 Creado recurso: {resource.name}')

    def create_exploration_events(self):
        events = [
            # Eventos positivos
            {'name': 'Cofre del Tesoro Encontrado', 'event_type': 'treasure', 'probability': 15, 'gold_effect': 500, 'experience_effect': 100, 'hull_damage': 0},
            {'name': 'Comerciante Amigable', 'event_type': 'merchant', 'probability': 20, 'gold_effect': 200, 'experience_effect': 50, 'hull_damage': 0},
            {'name': 'Nativos Hospitalarios', 'event_type': 'natives', 'probability': 25, 'gold_effect': 100, 'experience_effect': 75, 'hull_damage': 0},
            {'name': 'Isla Secreta Descubierta', 'event_type': 'island', 'probability': 10, 'gold_effect': 1000, 'experience_effect': 200, 'hull_damage': 0},
            {'name': 'Naufragio con Tesoro', 'event_type': 'shipwreck', 'probability': 12, 'gold_effect': 300, 'experience_effect': 80, 'hull_damage': 0},
            {'name': 'Aguas Tranquilas', 'event_type': 'calm', 'probability': 30, 'gold_effect': 0, 'experience_effect': 25, 'hull_damage': 0},
            
            # Eventos negativos
            {'name': 'Tormenta Tropical', 'event_type': 'storm', 'probability': 25, 'gold_effect': -100, 'experience_effect': 30, 'hull_damage': 15},
            {'name': 'Ataque de Piratas', 'event_type': 'pirates', 'probability': 18, 'gold_effect': -300, 'experience_effect': 50, 'hull_damage': 25},
            {'name': 'Monstruo Marino', 'event_type': 'monster', 'probability': 8, 'gold_effect': -200, 'experience_effect': 100, 'hull_damage': 30},
            {'name': 'Remolino Peligroso', 'event_type': 'whirlpool', 'probability': 12, 'gold_effect': -150, 'experience_effect': 40, 'hull_damage': 20},
        ]
        
        for event_data in events:
            event, created = ExplorationEvent.objects.get_or_create(
                name=event_data['name'],
                defaults=event_data
            )
            if created:
                self.stdout.write(f'⚡ Creado evento: {event.name}')

    def create_pirate_fleets(self):
        fleets = [
            {'name': 'Escuadrón de Saqueadores', 'fleet_type': 'scout', 'firepower': 25, 'defense': 20, 'speed': 12, 'crew_size': 15, 'level': 3, 'gold_reward': 200, 'experience_reward': 150},
            {'name': 'Banda de Corsarios', 'fleet_type': 'raider', 'firepower': 40, 'defense': 30, 'speed': 10, 'crew_size': 25, 'level': 8, 'gold_reward': 500, 'experience_reward': 300},
            {'name': 'Flota de Guerra Pirata', 'fleet_type': 'warship', 'firepower': 60, 'defense': 50, 'speed': 8, 'crew_size': 40, 'level': 15, 'gold_reward': 1000, 'experience_reward': 600},
            {'name': 'El Venganza Negra', 'fleet_type': 'flagship', 'firepower': 90, 'defense': 80, 'speed': 7, 'crew_size': 60, 'level': 25, 'gold_reward': 2500, 'experience_reward': 1200},
            {'name': 'Horda de Barbanegra', 'fleet_type': 'flagship', 'firepower': 110, 'defense': 100, 'speed': 6, 'crew_size': 80, 'level': 35, 'gold_reward': 5000, 'experience_reward': 2000},
        ]
        
        for fleet_data in fleets:
            fleet, created = PirateFleet.objects.get_or_create(
                name=fleet_data['name'],
                defaults=fleet_data
            )
            if created:
                self.stdout.write(f'🏴‍☠️ Creada flota pirata: {fleet.name}')

    def create_missions(self):
        missions = [
            # Misiones de exploración
            {'title': 'Descubre las Islas Perdidas', 'description': 'Explora tres islas desconocidas en el Caribe.', 'mission_type': 'exploration', 'difficulty': 'easy', 'required_level': 5, 'gold_reward': 500, 'experience_reward': 200},
            {'title': 'Expedición al Ártico', 'description': 'Navega hacia las peligrosas aguas árticas.', 'mission_type': 'exploration', 'difficulty': 'extreme', 'required_level': 30, 'gold_reward': 3000, 'experience_reward': 1500},
            
            # Misiones de comercio
            {'title': 'Ruta de las Especias', 'description': 'Establece una ruta comercial rentable de especias.', 'mission_type': 'trade', 'difficulty': 'medium', 'required_level': 10, 'gold_reward': 800, 'experience_reward': 300},
            {'title': 'Contrabando de Lujo', 'description': 'Transporta mercancías de lujo de forma discreta.', 'mission_type': 'trade', 'difficulty': 'hard', 'required_level': 15, 'gold_reward': 1500, 'experience_reward': 600},
            
            # Misiones de combate
            {'title': 'Caza de Piratas', 'description': 'Elimina a los piratas que acechan las rutas comerciales.', 'mission_type': 'combat', 'difficulty': 'medium', 'required_level': 8, 'gold_reward': 600, 'experience_reward': 400},
            {'title': 'Duelo Naval', 'description': 'Derrota al famoso capitán pirata en combate singular.', 'mission_type': 'combat', 'difficulty': 'extreme', 'required_level': 25, 'gold_reward': 2000, 'experience_reward': 1000},
            
            # Misiones de entrega
            {'title': 'Mensaje Urgente', 'description': 'Entrega un mensaje importante entre puertos.', 'mission_type': 'delivery', 'difficulty': 'easy', 'required_level': 3, 'gold_reward': 200, 'experience_reward': 100},
            {'title': 'Rescate de Náufragos', 'description': 'Rescata a los supervivientes de un naufragio.', 'mission_type': 'rescue', 'difficulty': 'medium', 'required_level': 12, 'gold_reward': 700, 'experience_reward': 350},
        ]
        
        for mission_data in missions:
            mission, created = Mission.objects.get_or_create(
                title=mission_data['title'],
                defaults=mission_data
            )
            if created:
                self.stdout.write(f'🎯 Creada misión: {mission.title}')

    def create_admin_player(self):
        # Crear usuario administrador si no existe
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ageofvoyage.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            
            # Crear perfil de jugador
            admin_player = Player.objects.create(
                user=admin_user,
                captain_name='Almirante Admin',
                level=50,
                experience=50000,
                gold=100000,
                reputation='marine',
                navigation_skill=20,
                combat_skill=20,
                trade_skill=20,
                leadership_skill=20,
                diplomacy_skill=20,
            )
            
            self.stdout.write(f'👑 Creado jugador administrador: {admin_player.captain_name}')
            self.stdout.write('🔑 Usuario: admin, Contraseña: admin123')
