"""
URL configuration for Age of Voyage project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.players.urls')),
    path('ships/', include('apps.ships.urls')),
    path('exploration/', include('apps.exploration.urls')),
    path('trade/', include('apps.trade.urls')),
    path('combat/', include('apps.combat.urls')),
    path('buildings/', include('apps.buildings.urls')),
    path('guilds/', include('apps.guilds.urls')),
    path('missions/', include('apps.missions.urls')),
    path('notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
