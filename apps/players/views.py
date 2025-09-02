"""Views for players app."""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Player
from .serializers import PlayerSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    """ViewSet for Player model."""
    
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter to current user's player."""
        if self.request.user.is_authenticated:
            return Player.objects.filter(user=self.request.user)
        return Player.objects.none()
    
    @action(detail=True, methods=['post'])
    def add_experience(self, request, pk=None):
        """Add experience to player."""
        player = self.get_object()
        amount = request.data.get('amount', 0)
        
        if amount > 0:
            player.add_experience(amount)
            return Response({
                'message': f'Added {amount} experience',
                'new_level': player.level,
                'new_experience': player.experience
            })
        
        return Response({'error': 'Invalid amount'}, status=400)
    
    @action(detail=True, methods=['get'])
    def resources(self, request, pk=None):
        """Get player resources."""
        player = self.get_object()
        return Response(player.total_resources)
