"""
URL configuration for conf project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Apps URLs
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('vehiculos/', include('vehiculos.urls')),
    path('catalogo/', include('catalogo.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalizar admin
admin.site.site_header = "Renovación Vehicular - Administración"
admin.site.site_title = "Renovación Vehicular"
admin.site.index_title = "Panel de Administración"