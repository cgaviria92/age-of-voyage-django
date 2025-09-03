from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import TradeRoute, TradePost, TradeTransaction
from apps.players.models import Player
from apps.ships.models import Ship


@login_required
def trade_dashboard(request):
    """Panel principal de comercio."""
    player = get_object_or_404(Player, user=request.user)
    active_routes = TradeRoute.objects.filter(player=player, is_active=True)
    recent_transactions = TradeTransaction.objects.filter(player=player).order_by('-created_at')[:10]
    
    context = {
        'player': player,
        'active_routes': active_routes,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'trade/dashboard.html', context)


@login_required
def trade_posts(request):
    """Lista de puestos comerciales."""
    player = get_object_or_404(Player, user=request.user)
    trade_posts = TradePost.objects.filter(is_active=True)
    
    context = {
        'player': player,
        'trade_posts': trade_posts,
    }
    return render(request, 'trade/trade_posts.html', context)


@login_required
def create_trade_route(request):
    """Crear una nueva ruta comercial."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        ship_id = request.POST.get('ship_id')
        origin_id = request.POST.get('origin_id')
        destination_id = request.POST.get('destination_id')
        cargo_type = request.POST.get('cargo_type')
        cargo_quantity = request.POST.get('cargo_quantity', 0)
        
        try:
            ship = Ship.objects.get(id=ship_id, player=player)
            origin = TradePost.objects.get(id=origin_id)
            destination = TradePost.objects.get(id=destination_id)
            
            if ship.status != 'docked':
                messages.error(request, 'El barco no está disponible.')
                return redirect('trade:dashboard')
            
            # Crear ruta comercial
            trade_route = TradeRoute.objects.create(
                player=player,
                ship=ship,
                origin=origin,
                destination=destination,
                cargo_type=cargo_type,
                cargo_quantity=int(cargo_quantity),
                is_active=True
            )
            
            # Actualizar estado del barco
            ship.status = 'trading'
            ship.save()
            
            messages.success(request, '¡Ruta comercial creada exitosamente!')
            
        except (Ship.DoesNotExist, TradePost.DoesNotExist, ValueError):
            messages.error(request, 'Error al crear la ruta comercial.')
        
        return redirect('trade:dashboard')
    
    # GET request
    player = get_object_or_404(Player, user=request.user)
    available_ships = Ship.objects.filter(player=player, status='docked')
    trade_posts = TradePost.objects.filter(is_active=True)
    
    cargo_types = [
        'Especias', 'Oro', 'Seda', 'Madera', 'Frutas',
        'Armas', 'Joyas', 'Textiles', 'Cerámicas', 'Vinos'
    ]
    
    context = {
        'player': player,
        'available_ships': available_ships,
        'trade_posts': trade_posts,
        'cargo_types': cargo_types,
    }
    return render(request, 'trade/create_route.html', context)


@login_required
def trade_route_detail(request, route_id):
    """Ver detalles de una ruta comercial."""
    player = get_object_or_404(Player, user=request.user)
    trade_route = get_object_or_404(TradeRoute, id=route_id, player=player)
    
    context = {
        'player': player,
        'trade_route': trade_route,
    }
    return render(request, 'trade/route_detail.html', context)


@login_required
def complete_trade(request, route_id):
    """Completar una ruta comercial."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        trade_route = get_object_or_404(TradeRoute, id=route_id, player=player)
        
        if not trade_route.is_active:
            messages.error(request, 'Esta ruta comercial no está activa.')
            return redirect('trade:dashboard')
        
        # Calcular ganancias
        profit = trade_route.cargo_quantity * 10  # Simulado
        
        # Crear transacción
        TradeTransaction.objects.create(
            player=player,
            trade_route=trade_route,
            profit=profit,
            cargo_type=trade_route.cargo_type,
            quantity=trade_route.cargo_quantity
        )
        
        # Completar ruta
        trade_route.is_active = False
        trade_route.save()
        
        # Devolver barco al puerto
        trade_route.ship.status = 'docked'
        trade_route.ship.save()
        
        # Otorgar ganancias
        player.gold += profit
        player.save()
        
        messages.success(request, f'¡Comercio completado! Ganaste {profit} oro.')
        
        return redirect('trade:dashboard')
    
    return redirect('trade:dashboard')


@login_required
def trade_history(request):
    """Historial de transacciones comerciales."""
    player = get_object_or_404(Player, user=request.user)
    transactions = TradeTransaction.objects.filter(player=player).order_by('-created_at')
    
    context = {
        'player': player,
        'transactions': transactions,
    }
    return render(request, 'trade/history.html', context)
