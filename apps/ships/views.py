"""Views for ships app."""

from rest_framework import viewsets, permissions
from .models import Ship, ShipType
from .serializers import ShipSerializer, ShipTypeSerializer


class ShipTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ShipType model."""
    
    queryset = ShipType.objects.all()
    serializer_class = ShipTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class ShipViewSet(viewsets.ModelViewSet):
    """ViewSet for Ship model."""
    
    queryset = Ship.objects.all()
    serializer_class = ShipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter to current user's ships."""
        if self.request.user.is_authenticated and hasattr(self.request.user, 'player'):
            return Ship.objects.filter(owner=self.request.user.player)
        return Ship.objects.none()
