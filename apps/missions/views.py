from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Mission, MissionProgress, MissionReward
from apps.players.models import Player


@login_required
def missions_dashboard(request):
    """Panel principal de misiones."""
    player = get_object_or_404(Player, user=request.user)
    
    # Misiones disponibles
    available_missions = Mission.objects.filter(
        is_active=True,
        required_level__lte=player.level
    ).exclude(
        id__in=MissionProgress.objects.filter(player=player).values_list('mission_id', flat=True)
    )
    
    # Misiones en progreso
    active_missions = MissionProgress.objects.filter(
        player=player,
        is_completed=False
    ).select_related('mission')
    
    # Misiones completadas recientemente
    completed_missions = MissionProgress.objects.filter(
        player=player,
        is_completed=True
    ).select_related('mission').order_by('-completed_at')[:10]
    
    context = {
        'player': player,
        'available_missions': available_missions,
        'active_missions': active_missions,
        'completed_missions': completed_missions,
    }
    return render(request, 'missions/dashboard.html', context)


@login_required
def mission_detail(request, mission_id):
    """Ver detalles de una misión."""
    player = get_object_or_404(Player, user=request.user)
    mission = get_object_or_404(Mission, id=mission_id, is_active=True)
    
    # Verificar progreso actual
    try:
        progress = MissionProgress.objects.get(player=player, mission=mission)
    except MissionProgress.DoesNotExist:
        progress = None
    
    # Obtener recompensas
    rewards = MissionReward.objects.filter(mission=mission)
    
    context = {
        'player': player,
        'mission': mission,
        'progress': progress,
        'rewards': rewards,
        'can_start': progress is None and player.level >= mission.required_level,
    }
    return render(request, 'missions/mission_detail.html', context)


@login_required
def start_mission(request, mission_id):
    """Iniciar una misión."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        mission = get_object_or_404(Mission, id=mission_id, is_active=True)
        
        # Verificar requisitos
        if player.level < mission.required_level:
            messages.error(request, f'Necesitas nivel {mission.required_level} para esta misión.')
            return redirect('missions:mission_detail', mission_id=mission_id)
        
        # Verificar si ya está en progreso
        if MissionProgress.objects.filter(player=player, mission=mission).exists():
            messages.error(request, 'Ya tienes esta misión en progreso o completada.')
            return redirect('missions:mission_detail', mission_id=mission_id)
        
        # Iniciar misión
        progress = MissionProgress.objects.create(
            player=player,
            mission=mission,
            current_progress=0,
            is_completed=False
        )
        
        messages.success(request, f'¡Misión "{mission.title}" iniciada!')
        return redirect('missions:mission_progress', progress_id=progress.id)
    
    return redirect('missions:dashboard')


@login_required
def mission_progress(request, progress_id):
    """Ver progreso de una misión."""
    player = get_object_or_404(Player, user=request.user)
    progress = get_object_or_404(MissionProgress, id=progress_id, player=player)
    
    # Calcular porcentaje de progreso
    if progress.mission.target_amount > 0:
        progress_percentage = min(100, (progress.current_progress / progress.mission.target_amount) * 100)
    else:
        progress_percentage = 0
    
    context = {
        'player': player,
        'progress': progress,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'missions/mission_progress.html', context)


@login_required
def update_mission_progress(request, progress_id):
    """Actualizar progreso de misión (simulado)."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        progress = get_object_or_404(MissionProgress, id=progress_id, player=player)
        
        if progress.is_completed:
            messages.error(request, 'Esta misión ya fue completada.')
            return redirect('missions:mission_progress', progress_id=progress_id)
        
        # Simular progreso
        increment = int(request.POST.get('increment', 1))
        progress.current_progress = min(
            progress.mission.target_amount,
            progress.current_progress + increment
        )
        
        # Verificar si se completó
        if progress.current_progress >= progress.mission.target_amount:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            
            # Otorgar recompensas
            rewards = MissionReward.objects.filter(mission=progress.mission)
            total_gold = 0
            total_experience = 0
            
            for reward in rewards:
                if reward.reward_type == 'gold':
                    total_gold += reward.amount
                elif reward.reward_type == 'experience':
                    total_experience += reward.amount
            
            player.gold += total_gold
            player.experience += total_experience
            player.save()
            
            messages.success(request, f'¡Misión completada! Recompensas: {total_gold} oro, {total_experience} XP')
        else:
            messages.info(request, f'Progreso actualizado: {progress.current_progress}/{progress.mission.target_amount}')
        
        progress.save()
        return redirect('missions:mission_progress', progress_id=progress_id)
    
    return redirect('missions:dashboard')


@login_required
def abandon_mission(request, progress_id):
    """Abandonar una misión."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        progress = get_object_or_404(MissionProgress, id=progress_id, player=player)
        
        if progress.is_completed:
            messages.error(request, 'No puedes abandonar una misión completada.')
            return redirect('missions:dashboard')
        
        mission_title = progress.mission.title
        progress.delete()
        
        messages.info(request, f'Misión "{mission_title}" abandonada.')
        return redirect('missions:dashboard')
    
    return redirect('missions:dashboard')


@login_required
def daily_missions(request):
    """Misiones diarias."""
    player = get_object_or_404(Player, user=request.user)
    
    # Obtener misiones diarias
    daily_missions = Mission.objects.filter(
        mission_type='daily',
        is_active=True,
        required_level__lte=player.level
    )
    
    # Verificar progreso de misiones diarias de hoy
    today = timezone.now().date()
    daily_progress = MissionProgress.objects.filter(
        player=player,
        mission__mission_type='daily',
        started_at__date=today
    ).select_related('mission')
    
    context = {
        'player': player,
        'daily_missions': daily_missions,
        'daily_progress': daily_progress,
    }
    return render(request, 'missions/daily_missions.html', context)


@login_required
def mission_categories(request):
    """Ver misiones por categorías."""
    player = get_object_or_404(Player, user=request.user)
    
    categories = {
        'exploration': Mission.objects.filter(category='exploration', is_active=True),
        'combat': Mission.objects.filter(category='combat', is_active=True),
        'trade': Mission.objects.filter(category='trade', is_active=True),
        'building': Mission.objects.filter(category='building', is_active=True),
        'social': Mission.objects.filter(category='social', is_active=True),
    }
    
    context = {
        'player': player,
        'categories': categories,
    }
    return render(request, 'missions/categories.html', context)


@login_required
def claim_reward(request, progress_id):
    """Reclamar recompensa de misión completada."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        progress = get_object_or_404(MissionProgress, id=progress_id, player=player)
        
        if not progress.is_completed:
            messages.error(request, 'Esta misión no está completada.')
            return redirect('missions:mission_progress', progress_id=progress_id)
        
        if progress.rewards_claimed:
            messages.error(request, 'Las recompensas ya fueron reclamadas.')
            return redirect('missions:dashboard')
        
        # Marcar recompensas como reclamadas
        progress.rewards_claimed = True
        progress.save()
        
        messages.success(request, '¡Recompensas reclamadas exitosamente!')
        return redirect('missions:dashboard')
    
    return redirect('missions:dashboard')
