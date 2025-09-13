from django.db import migrations

def create_shiptypes(apps, schema_editor):
    ShipType = apps.get_model('ships', 'ShipType')
    ships = [
        {
            'name': 'Goleta',
            'description': 'Barco rápido y ligero, ideal para exploración.',
            'base_speed': 18,
            'base_cargo_capacity': 40,
            'base_firepower': 10,
            'base_defense': 8,
            'base_crew_capacity': 20,
            'purchase_cost': 300,
            'maintenance_cost_per_day': 10,
            'required_level': 1,
        },
        {
            'name': 'Fragata',
            'description': 'Barco equilibrado para combate y comercio.',
            'base_speed': 14,
            'base_cargo_capacity': 80,
            'base_firepower': 25,
            'base_defense': 18,
            'base_crew_capacity': 40,
            'purchase_cost': 800,
            'maintenance_cost_per_day': 20,
            'required_level': 2,
        },
        {
            'name': 'Galeón',
            'description': 'Gran capacidad de carga y defensa, lento pero resistente.',
            'base_speed': 10,
            'base_cargo_capacity': 200,
            'base_firepower': 35,
            'base_defense': 30,
            'base_crew_capacity': 80,
            'purchase_cost': 2000,
            'maintenance_cost_per_day': 40,
            'required_level': 4,
        },
        {
            'name': 'Navío de Línea',
            'description': 'El rey del combate naval, gran poder de fuego y defensa.',
            'base_speed': 8,
            'base_cargo_capacity': 120,
            'base_firepower': 60,
            'base_defense': 50,
            'base_crew_capacity': 120,
            'purchase_cost': 5000,
            'maintenance_cost_per_day': 80,
            'required_level': 7,
        },
        {
            'name': 'Corbeta',
            'description': 'Barco pequeño y veloz, ideal para misiones rápidas.',
            'base_speed': 20,
            'base_cargo_capacity': 30,
            'base_firepower': 8,
            'base_defense': 6,
            'base_crew_capacity': 15,
            'purchase_cost': 200,
            'maintenance_cost_per_day': 8,
            'required_level': 1,
        },
        {
            'name': 'Bergantín',
            'description': 'Versátil y equilibrado, usado por piratas y comerciantes.',
            'base_speed': 16,
            'base_cargo_capacity': 60,
            'base_firepower': 18,
            'base_defense': 12,
            'base_crew_capacity': 30,
            'purchase_cost': 500,
            'maintenance_cost_per_day': 15,
            'required_level': 2,
        },
        {
            'name': 'Barco Mercante',
            'description': 'Especializado en carga, poca defensa y velocidad.',
            'base_speed': 9,
            'base_cargo_capacity': 300,
            'base_firepower': 5,
            'base_defense': 10,
            'base_crew_capacity': 25,
            'purchase_cost': 1200,
            'maintenance_cost_per_day': 25,
            'required_level': 3,
        },
    ]
    for data in ships:
        ShipType.objects.get_or_create(name=data['name'], defaults=data)

    # Asignar barco inicial por defecto a cada usuario
    Player = apps.get_model('players', 'Player')
    Ship = apps.get_model('ships', 'Ship')
    goleta_type = ShipType.objects.get(name='Goleta')
    for player in Player.objects.all():
        if not Ship.objects.filter(owner=player).exists():
            Ship.objects.create(
                owner=player,
                ship_type=goleta_type,
                name=f"{player.captain_name} - Goleta",
                speed=goleta_type.base_speed,
                cargo_capacity=goleta_type.base_cargo_capacity,
                firepower=goleta_type.base_firepower,
                defense=goleta_type.base_defense,
                crew_capacity=goleta_type.base_crew_capacity,
                crew_count=goleta_type.base_crew_capacity // 2,
                hull_health=100,
                status='docked'
            )

class Migration(migrations.Migration):
    dependencies = [
        ('ships', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(create_shiptypes),
    ]
