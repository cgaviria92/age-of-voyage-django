from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Guild, GuildMember, GuildInvitation, GuildEvent
from apps.players.models import Player


@login_required
def guild_dashboard(request):
    """Panel principal de gremios."""
    player = get_object_or_404(Player, user=request.user)
    
    try:
        guild_member = GuildMember.objects.get(player=player)
        guild = guild_member.guild
        guild_events = GuildEvent.objects.filter(guild=guild).order_by('-created_at')[:10]
        members = GuildMember.objects.filter(guild=guild).select_related('player__user')
    except GuildMember.DoesNotExist:
        guild = None
        guild_member = None
        guild_events = []
        members = []
    
    # Invitaciones pendientes
    pending_invitations = GuildInvitation.objects.filter(
        invited_player=player, 
        status='pending'
    )
    
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
        current_guild = GuildMember.objects.get(player=player).guild
    except GuildMember.DoesNotExist:
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
        
        # Verificar si ya está en un gremio
        if GuildMember.objects.filter(player=player).exists():
            messages.error(request, 'Ya perteneces a un gremio.')
            return redirect('guilds:dashboard')
        
        guild_name = request.POST.get('guild_name')
        description = request.POST.get('description', '')
        
        if not guild_name:
            messages.error(request, 'Debes proporcionar un nombre para el gremio.')
            return redirect('guilds:create_guild')
        
        # Verificar costo
        creation_cost = 1000
        if player.gold < creation_cost:
            messages.error(request, f'Necesitas {creation_cost} oro para crear un gremio.')
            return redirect('guilds:create_guild')
        
        # Crear gremio
        guild = Guild.objects.create(
            name=guild_name,
            description=description,
            leader=player,
            is_active=True
        )
        
        # Agregar al jugador como miembro fundador
        GuildMember.objects.create(
            guild=guild,
            player=player,
            role='leader',
            joined_at=guild.created_at
        )
        
        # Deducir costo
        player.gold -= creation_cost
        player.save()
        
        messages.success(request, f'¡Gremio "{guild_name}" creado exitosamente!')
        return redirect('guilds:dashboard')
    
    # GET request
    player = get_object_or_404(Player, user=request.user)
    context = {'player': player}
    return render(request, 'guilds/create_guild.html', context)


@login_required
def join_guild(request, guild_id):
    """Solicitar unirse a un gremio."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        guild = get_object_or_404(Guild, id=guild_id, is_active=True)
        
        # Verificar si ya está en un gremio
        if GuildMember.objects.filter(player=player).exists():
            messages.error(request, 'Ya perteneces a un gremio.')
            return redirect('guilds:dashboard')
        
        # Verificar si ya hay una invitación pendiente
        if GuildInvitation.objects.filter(guild=guild, invited_player=player, status='pending').exists():
            messages.error(request, 'Ya tienes una solicitud pendiente para este gremio.')
            return redirect('guilds:guild_list')
        
        # Crear solicitud de unión (como invitación)
        invitation = GuildInvitation.objects.create(
            guild=guild,
            invited_by=guild.leader,  # El líder revisará la solicitud
            invited_player=player,
            status='pending'
        )
        
        messages.success(request, f'Solicitud enviada al gremio "{guild.name}".')
        return redirect('guilds:guild_list')
    
    return redirect('guilds:guild_list')


@login_required
def respond_invitation(request, invitation_id):
    """Responder a una invitación de gremio."""
    if request.method == 'POST':
        player = get_object_or_404(Player, user=request.user)
        invitation = get_object_or_404(GuildInvitation, id=invitation_id, invited_player=player)
        
        response = request.POST.get('response')
        
        if response == 'accept':
            # Verificar si ya está en un gremio
            if GuildMember.objects.filter(player=player).exists():
                messages.error(request, 'Ya perteneces a un gremio.')
                invitation.status = 'declined'
                invitation.save()
                return redirect('guilds:dashboard')
            
            # Unirse al gremio
            GuildMember.objects.create(
                guild=invitation.guild,
                player=player,
                role='member'
            )
            
            invitation.status = 'accepted'
            invitation.save()
            
            # Crear evento
            GuildEvent.objects.create(
                guild=invitation.guild,
                event_type='member_joined',
                description=f'{player.user.username} se unió al gremio'
            )
            
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
        
        try:
            guild_member = GuildMember.objects.get(player=player)
            guild = guild_member.guild
            
            if guild_member.role == 'leader':
                # Si es líder, verificar si hay otros miembros
                other_members = GuildMember.objects.filter(guild=guild).exclude(player=player)
                if other_members.exists():
                    # Transferir liderazgo al primer miembro
                    new_leader = other_members.first()
                    new_leader.role = 'leader'
                    new_leader.save()
                    guild.leader = new_leader.player
                    guild.save()
                else:
                    # Si no hay otros miembros, desactivar el gremio
                    guild.is_active = False
                    guild.save()
            
            # Crear evento
            GuildEvent.objects.create(
                guild=guild,
                event_type='member_left',
                description=f'{player.user.username} abandonó el gremio'
            )
            
            # Eliminar membresía
            guild_member.delete()
            
            messages.success(request, f'Has abandonado el gremio "{guild.name}".')
            
        except GuildMember.DoesNotExist:
            messages.error(request, 'No perteneces a ningún gremio.')
        
        return redirect('guilds:dashboard')
    
    return redirect('guilds:dashboard')


@login_required
def guild_detail(request, guild_id):
    """Ver detalles de un gremio."""
    player = get_object_or_404(Player, user=request.user)
    guild = get_object_or_404(Guild, id=guild_id, is_active=True)
    members = GuildMember.objects.filter(guild=guild).select_related('player__user')
    
    # Verificar si el jugador es miembro
    try:
        guild_member = GuildMember.objects.get(guild=guild, player=player)
        is_member = True
    except GuildMember.DoesNotExist:
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
        guild_member = GuildMember.objects.get(player=player, role='leader')
        guild = guild_member.guild
    except GuildMember.DoesNotExist:
        messages.error(request, 'No tienes permisos para gestionar un gremio.')
        return redirect('guilds:dashboard')
    
    members = GuildMember.objects.filter(guild=guild).select_related('player__user')
    pending_invitations = GuildInvitation.objects.filter(guild=guild, status='pending')
    
    context = {
        'player': player,
        'guild': guild,
        'guild_member': guild_member,
        'members': members,
        'pending_invitations': pending_invitations,
    }
    return render(request, 'guilds/manage_guild.html', context)
