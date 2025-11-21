from django.contrib import admin
from .models import (
    Solicitud, PersonaFisica, PersonaMoral, 
    RepresentanteLegal, Domicilio, Vehiculo, Documento
)

class DomicilioInline(admin.TabularInline):
    model = Domicilio
    extra = 0

class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0
    readonly_fields = ['subido_en', 'tamano']

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ['folio', 'usuario', 'tipo_persona', 'estado', 'creado']
    list_filter = ['estado', 'tipo_persona', 'creado']
    search_fields = ['folio', 'usuario__username', 'clave_concesion']
    readonly_fields = ['folio', 'creado', 'actualizado']
    inlines = [DomicilioInline, DocumentoInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('folio', 'usuario', 'estado')
        }),
        ('Datos de Concesión', {
            'fields': ('tipo_persona', 'clave_concesion', 'municipio_operacion')
        }),
        ('Fechas', {
            'fields': ('creado', 'actualizado', 'fecha_envio'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PersonaFisica)
class PersonaFisicaAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'rfc', 'telefono_movil', 'solicitud']
    search_fields = ['nombre', 'primer_apellido', 'segundo_apellido', 'rfc']

@admin.register(PersonaMoral)
class PersonaMoralAdmin(admin.ModelAdmin):
    list_display = ['razon_social', 'rfc', 'solicitud']
    search_fields = ['razon_social', 'rfc']

@admin.register(RepresentanteLegal)
class RepresentanteLegalAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'rfc', 'persona_moral']
    search_fields = ['nombre', 'primer_apellido', 'segundo_apellido', 'rfc']

@admin.register(Domicilio)
class DomicilioAdmin(admin.ModelAdmin):
    list_display = ['solicitud', 'tipo', 'calle', 'colonia', 'municipio']
    list_filter = ['tipo', 'estado']
    search_fields = ['calle', 'colonia', 'municipio']

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['solicitud', 'marca', 'tipo', 'placas']
    list_filter = ['marca']
    search_fields = ['placas', 'numero_serie']

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['solicitud', 'tipo_documento', 'nombre_original', 'subido_en']
    list_filter = ['tipo_documento', 'subido_en']
    search_fields = ['solicitud__folio', 'nombre_original']
    readonly_fields = ['subido_en']