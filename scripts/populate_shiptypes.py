from apps.ships.models import ShipType

# Barcos básicos
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
]

for data in ships:
    obj, created = ShipType.objects.get_or_create(name=data['name'], defaults=data)
    if created:
        print(f"Creado: {obj.name}")
    else:
        print(f"Ya existe: {obj.name}")
