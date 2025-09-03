from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Notification, NotificationTemplate
from apps.players.models import Player


@login_required
def notifications_list(request):
    """Lista de notificaciones del jugador."""
    player = get_object_or_404(Player, user=request.user)
    
    # Obtener notificaciones del jugador
    notifications = Notification.objects.filter(
        recipient=player
    ).order_by('-created_at')
    
    # Marcar como leídas al ver la lista
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True, read_at=timezone.now())
    
    # Filtrar por tipo si se especifica
    notification_type = request.GET.get('type')
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    # Paginación simple
    notifications = notifications[:50]  # Limitar a 50 notificaciones
    
    context = {
        'player': player,
        'notifications': notifications,
        'current_type': notification_type,
        'notification_types': [
            ('system', 'Sistema'),
            ('trade', 'Comercio'),
            ('combat', 'Combate'),
            ('exploration', 'Exploración'),
            ('guild', 'Gremio'),
            ('mission', 'Misiones'),
            ('achievement', 'Logros'),
        ]
    }
    return render(request, 'notifications/list.html', context)


@login_required
def notification_detail(request, notification_id):
    """Ver detalles de una notificación."""
    player = get_object_or_404(Player, user=request.user)
    notification = get_object_or_404(Notification, id=notification_id, recipient=player)
    
    # Marcar como leída
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
    
    context = {
        'player': player,
        'notification': notification,
    }
    return render(request, 'notifications/detail.html', context)


@login_required
def mark_as_read(request, notification_id):
    """Marcar notificación como leída."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        notification = get_object_or_404(Notification, id=notification_id, recipient=player)
        
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        
        return redirect('notifications:list')
    
    return redirect('notifications:list')


@login_required
def mark_all_as_read(request):
    """Marcar todas las notificaciones como leídas."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        
        unread_notifications = Notification.objects.filter(
            recipient=player,
            is_read=False
        )
        
        count = unread_notifications.count()
        unread_notifications.update(is_read=True, read_at=timezone.now())
        
        messages.success(request, f'{count} notificaciones marcadas como leídas.')
        return redirect('notifications:list')
    
    return redirect('notifications:list')


@login_required
def delete_notification(request, notification_id):
    """Eliminar una notificación."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        notification = get_object_or_404(Notification, id=notification_id, recipient=player)
        
        notification.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        
        messages.success(request, 'Notificación eliminada.')
        return redirect('notifications:list')
    
    return redirect('notifications:list')


@login_required
def delete_all_read(request):
    """Eliminar todas las notificaciones leídas."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        
        read_notifications = Notification.objects.filter(
            recipient=player,
            is_read=True
        )
        
        count = read_notifications.count()
        read_notifications.delete()
        
        messages.success(request, f'{count} notificaciones eliminadas.')
        return redirect('notifications:list')
    
    return redirect('notifications:list')


@login_required
def notification_settings(request):
    """Configuración de notificaciones."""
    player = get_object_or_404(Player, user=request.user)
    
    if request.method == 'POST':
        # Aquí podrías manejar las preferencias de notificaciones
        # Por ahora, solo mostramos un mensaje de éxito
        messages.success(request, 'Configuración de notificaciones actualizada.')
        return redirect('notifications:settings')
    
    # Obtener estadísticas de notificaciones
    total_notifications = Notification.objects.filter(recipient=player).count()
    unread_notifications = Notification.objects.filter(recipient=player, is_read=False).count()
    
    # Notificaciones por tipo
    notification_stats = {}
    for type_code, type_name in [
        ('system', 'Sistema'),
        ('trade', 'Comercio'),
        ('combat', 'Combate'),
        ('exploration', 'Exploración'),
        ('guild', 'Gremio'),
        ('mission', 'Misiones'),
        ('achievement', 'Logros'),
    ]:
        count = Notification.objects.filter(
            recipient=player,
            notification_type=type_code
        ).count()
        notification_stats[type_name] = count
    
    context = {
        'player': player,
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'notification_stats': notification_stats,
    }
    return render(request, 'notifications/settings.html', context)


@login_required
def get_unread_count(request):
    """Obtener número de notificaciones no leídas (AJAX)."""
    player = get_object_or_404(Player, user=request.user)
    
    unread_count = Notification.objects.filter(
        recipient=player,
        is_read=False
    ).count()
    
    return JsonResponse({'unread_count': unread_count})


@login_required
def get_recent_notifications(request):
    """Obtener notificaciones recientes (AJAX)."""
    player = get_object_or_404(Player, user=request.user)
    
    recent_notifications = Notification.objects.filter(
        recipient=player
    ).order_by('-created_at')[:10]
    
    notifications_data = []
    for notification in recent_notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'priority': notification.priority,
        })
    
    return JsonResponse({'notifications': notifications_data})


def create_notification(recipient, title, message, notification_type='system', priority='normal', action_url=None):
    """
    Función utilitaria para crear notificaciones.
    Esta función puede ser importada desde otras apps.
    """
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        action_url=action_url
    )


def create_notification_from_template(recipient, template_name, context_data=None):
    """
    Crear notificación basada en una plantilla.
    """
    try:
        template = NotificationTemplate.objects.get(
            name=template_name,
            is_active=True
        )
        
        # Reemplazar variables en la plantilla
        title = template.title
        message = template.message
        
        if context_data:
            for key, value in context_data.items():
                title = title.replace(f'{{{key}}}', str(value))
                message = message.replace(f'{{{key}}}', str(value))
        
        return create_notification(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=template.notification_type,
            priority=template.priority
        )
    
    except NotificationTemplate.DoesNotExist:
        # Si la plantilla no existe, crear notificación genérica
        return create_notification(
            recipient=recipient,
            title='Notificación',
            message='Has recibido una nueva notificación.',
            notification_type='system'
        )
