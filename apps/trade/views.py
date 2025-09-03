from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import TradeRoute, Market, TradeMission, Resource, TradeMissionCargo, PriceHistory
from apps.players.models import Player
from apps.ships.models import Ship


@login_required
def trade_dashboard(request):
    player = get_object_or_404(Player, user=request.user)
    active_routes = TradeRoute.objects.filter(player=player, is_active=True)
    recent_missions = TradeMission.objects.filter(player=player).order_by('-started_at')[:10]
    
    context = {
        'player': player,
        'active_routes': active_routes,
        'recent_missions': recent_missions,
    }
    return render(request, 'trade/dashboard.html', context)


@login_required
def trade_posts(request):
    player = get_object_or_404(Player, user=request.user)
    markets = Market.objects.filter(is_active=True)
    
    context = {
        'player': player,
        'markets': markets,
    }
    return render(request, 'trade/trade_posts.html', context)


@login_required
def create_trade_route(request):
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        ship_id = request.POST.get('ship_id')
        origin_id = request.POST.get('origin_id')
        destination_id = request.POST.get('destination_id')
        cargo_type = request.POST.get('cargo_type')
        cargo_quantity = request.POST.get('cargo_quantity', 0)
        
        try:
            ship = Ship.objects.get(id=ship_id, player=player)
            origin = Market.objects.get(id=origin_id)
            destination = Market.objects.get(id=destination_id)
            
            if ship.status != 'docked':
                messages.error(request, 'El barco no está disponible.')
                return redirect('trade:trade_dashboard')
            
            trade_route = TradeRoute.objects.create(
                player=player,
                ship=ship,
                origin_region=origin.region,
                destination_region=destination.region,
                cargo_type=cargo_type,
                cargo_quantity=int(cargo_quantity),
                is_active=True
            )
            
            ship.status = 'trading'
            ship.save()
            
            messages.success(request, 'Ruta comercial creada exitosamente!')
            
        except (Ship.DoesNotExist, Market.DoesNotExist, ValueError):
            messages.error(request, 'Error al crear la ruta comercial.')
        
        return redirect('trade:trade_dashboard')
    
    player = get_object_or_404(Player, user=request.user)
    available_ships = Ship.objects.filter(player=player, status='docked')
    markets = Market.objects.filter(is_active=True)
    
    cargo_types = [
        'Especias', 'Oro', 'Seda', 'Madera', 'Frutas',
        'Armas', 'Joyas', 'Textiles', 'Cerámicas', 'Vinos'
    ]
    
    context = {
        'player': player,
        'available_ships': available_ships,
        'markets': markets,
        'cargo_types': cargo_types,
    }
    return render(request, 'trade/create_route.html', context)


@login_required
def trade_route_detail(request, route_id):
    player = get_object_or_404(Player, user=request.user)
    trade_route = get_object_or_404(TradeRoute, id=route_id, player=player)
    
    context = {
        'player': player,
        'trade_route': trade_route,
    }
    return render(request, 'trade/route_detail.html', context)


@login_required
def complete_trade(request, route_id):
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        trade_route = get_object_or_404(TradeRoute, id=route_id, player=player)
        
        if not trade_route.is_active:
            messages.error(request, 'Esta ruta comercial no está activa.')
            return redirect('trade:trade_dashboard')
        
        profit = trade_route.cargo_quantity * 10
        
        player.gold += profit
        player.save()
        
        trade_route.is_active = False
        trade_route.save()
        
        trade_route.ship.status = 'docked'
        trade_route.ship.save()
        
        messages.success(request, f'Comercio completado! Ganaste {profit} oro.')
        
        return redirect('trade:trade_dashboard')
    
    return redirect('trade:trade_dashboard')


@login_required
def trade_history(request):
    player = get_object_or_404(Player, user=request.user)
    missions = TradeMission.objects.filter(player=player).order_by('-started_at')
    
    context = {
        'player': player,
        'missions': missions,
    }
    return render(request, 'trade/history.html', context)
