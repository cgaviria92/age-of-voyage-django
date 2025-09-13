from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BuildingType, PlayerBuilding
from apps.exploration.models import Region
from apps.players.models import Player
from .services.building_service import BuildingService

@login_required
def buildings_overview(request):
    player = get_object_or_404(Player, user=request.user)
    buildings = BuildingService.get_player_buildings(player)
    types = BuildingType.objects.all()
    context = {
        'player': player,
        'buildings': buildings,
        'types': types,
    }
    return render(request, 'buildings/overview.html', context)

@login_required
def build_structure(request, region_id):
    player = get_object_or_404(Player, user=request.user)
    region = get_object_or_404(Region, id=region_id)
    types = BuildingType.objects.all()
    if request.method == 'POST':
        type_id = request.POST.get('type_id')
        building_type = get_object_or_404(BuildingType, id=type_id)
        building = BuildingService.create_building(player, building_type, region)
        messages.success(request, 'Construcción iniciada correctamente.')
        return redirect('buildings:overview')
    context = {
        'player': player,
        'region': region,
        'types': types,
    }
    return render(request, 'buildings/build.html', context)

@login_required
def manage_building(request, building_id):
    player = get_object_or_404(Player, user=request.user)
    building = get_object_or_404(PlayerBuilding, id=building_id, owner=player)
    if request.method == 'POST':
        if 'complete' in request.POST:
            BuildingService.complete_building(building)
            messages.success(request, 'Construcción completada.')
        elif 'upgrade' in request.POST:
            BuildingService.upgrade_building(building)
            messages.success(request, 'Construcción mejorada.')
        return redirect('buildings:overview')
    context = {
        'player': player,
        'building': building,
    }
    return render(request, 'buildings/manage.html', context)
