from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Guild, GuildMembership
from apps.players.models import Player
from .services.guild_service import GuildService


@login_required
def guild_dashboard(request):
    """Panel principal de gremios."""
    player = get_object_or_404(Player, user=request.user)
    
    try:
        guild_member = GuildMembership.objects.get(player=player)
        guild = guild_member.guild
        # guild_events = GuildEvent.objects.filter(guild=guild).order_by('-created_at')[:10]
        guild_events = []  # Placeholder until GuildEvent model is created
        members = GuildMembership.objects.filter(guild=guild).select_related('player__user')
    except GuildMembership.DoesNotExist:
        guild = None
        guild_member = None
        guild_events = []
        members = []
    
    # Invitaciones pendientes
    # pending_invitations = GuildInvitation.objects.filter(
    #     invited_player=player, 
    #     status='pending'
    # )
    pending_invitations = []  # Placeholder until GuildInvitation model is created
    
    context = {
        'player': player,
        'guild': guild,
        'guild_member': guild_member,
        'guild_events': guild_events,
        'members': members,
        'pending_invitations': pending_invitations,
    }
    return render(request, 'guilds/dashboard.html', context)


@login_required
def guild_list(request):
    """Lista de gremios disponibles."""
    player = get_object_or_404(Player, user=request.user)
    guilds = Guild.objects.filter(is_active=True).order_by('-created_at')
    
    # Verificar si el jugador ya está en un gremio
    try:
        current_guild = GuildMembership.objects.get(player=player).guild
    except GuildMembership.DoesNotExist:
        current_guild = None
    
    context = {
        'player': player,
        'guilds': guilds,
        'current_guild': current_guild,
    }
    return render(request, 'guilds/guild_list.html', context)


@login_required
def create_guild(request):
    """Crear un nuevo gremio."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        if GuildMembership.objects.filter(player=player).exists():
            messages.error(request, 'Ya perteneces a un gremio.')
            return redirect('guilds:dashboard')
        guild_name = request.POST.get('guild_name')
        description = request.POST.get('description', '')
        if not guild_name:
            messages.error(request, 'Debes proporcionar un nombre para el gremio.')
            return redirect('guilds:create_guild')
        creation_cost = 1000
        if player.gold < creation_cost:
            messages.error(request, f'Necesitas {creation_cost} oro para crear un gremio.')
            return redirect('guilds:create_guild')
        guild = GuildService.create_guild(player, guild_name, description)
        player.gold -= creation_cost
        player.save()
        messages.success(request, f'¡Gremio "{guild_name}" creado exitosamente!')
        return redirect('guilds:dashboard')
    player = get_object_or_404(Player, user=request.user)
    context = {'player': player}
    return render(request, 'guilds/create_guild.html', context)


@login_required
def join_guild(request, guild_id):
    """Solicitar unirse a un gremio."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        guild = get_object_or_404(Guild, id=guild_id, is_active=True)
        if GuildMembership.objects.filter(player=player).exists():
            messages.error(request, 'Ya perteneces a un gremio.')
            return redirect('guilds:dashboard')
        membership = GuildService.join_guild(player, guild)
        if membership:
            messages.success(request, f'Te has unido al gremio {guild.name}.')
        else:
            messages.error(request, 'No puedes unirte al gremio.')
        return redirect('guilds:guild_list')
    return redirect('guilds:guild_list')


@login_required
def respond_invitation(request, invitation_id):
    """Responder a una invitación de gremio."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
#         invitation = get_object_or_404(GuildInvitation, id=invitation_id, invited_player=player)
        
        response = request.POST.get('response')
        
        if response == 'accept':
            # Verificar si ya está en un gremio
            if GuildMembership.objects.filter(player=player).exists():
                messages.error(request, 'Ya perteneces a un gremio.')
                invitation.status = 'declined'
                invitation.save()
                return redirect('guilds:dashboard')
            
            # Unirse al gremio
            GuildMembership.objects.create(
                guild=invitation.guild,
                player=player,
                role='member'
            )
            
            invitation.status = 'accepted'
            invitation.save()
            
            # Crear evento
            # GuildEvent.objects.create(
            #     guild=invitation.guild,
            #     event_type='member_joined',
            #     description=f'{player.user.username} se unió al gremio'
            # )
            
            messages.success(request, f'¡Te has unido al gremio "{invitation.guild.name}"!')
            
        elif response == 'decline':
            invitation.status = 'declined'
            invitation.save()
            messages.info(request, 'Invitación rechazada.')
        
        return redirect('guilds:dashboard')
    
    return redirect('guilds:dashboard')


@login_required
def leave_guild(request):
    """Abandonar el gremio actual."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        GuildService.leave_guild(player)
        messages.success(request, 'Has abandonado el gremio.')
        return redirect('guilds:dashboard')
    return redirect('guilds:dashboard')


@login_required
def guild_detail(request, guild_id):
    """Ver detalles de un gremio."""
    player = get_object_or_404(Player, user=request.user)
    guild = get_object_or_404(Guild, id=guild_id, is_active=True)
    members = GuildMembership.objects.filter(guild=guild).select_related('player__user')
    
    # Verificar si el jugador es miembro
    try:
        guild_member = GuildMembership.objects.get(guild=guild, player=player)
        is_member = True
    except GuildMembership.DoesNotExist:
        guild_member = None
        is_member = False
    
    context = {
        'player': player,
        'guild': guild,
        'members': members,
        'guild_member': guild_member,
        'is_member': is_member,
    }
    return render(request, 'guilds/guild_detail.html', context)


@login_required
def manage_guild(request):
    """Gestionar gremio (solo para líderes)."""
    player = get_object_or_404(Player, user=request.user)
    
    try:
        guild_member = GuildMembership.objects.get(player=player, role='leader')
        guild = guild_member.guild
    except GuildMembership.DoesNotExist:
        messages.error(request, 'No tienes permisos para gestionar un gremio.')
        return redirect('guilds:dashboard')
    
    members = GuildMembership.objects.filter(guild=guild).select_related('player__user')
#     pending_invitations = GuildInvitation.objects.filter(guild=guild, status='pending')
    
    context = {
        'player': player,
        'guild': guild,
        'guild_member': guild_member,
        'members': members,
        'pending_invitations': pending_invitations,
    }
    return render(request, 'guilds/manage_guild.html', context)
