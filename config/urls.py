"""
URL configuration for Age of Voyage project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Admin site customization
admin.site.site_header = "Age of Voyage Admin"
admin.site.site_title = "Age of Voyage Admin Portal"
admin.site.index_title = "Welcome to Age of Voyage Administration"

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('accounts/', include('allauth.urls')),
    
    # Frontend routes
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
