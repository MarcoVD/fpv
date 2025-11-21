from django.contrib import admin
from .models import Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['user', 'telefono_movil', 'cuenta_activada', 'creado']
    list_filter = ['cuenta_activada', 'creado']
    search_fields = ['user__username', 'user__email', 'telefono_movil']
    readonly_fields = ['token_activacion', 'creado', 'actualizado']