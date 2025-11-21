# En D:\Codigo\02_Python\fpv\catalogo\admin.py

from django.contrib import admin
# Importamos los modelos que están en catalogo/models.py
from .models import Municipio, MarcaVehiculo, TipoVehiculo, TipoDocumento, Solicitud 

# --- Admin para Municipio (Corrige E108/E116 si estaban en el código original) ---
class MunicipioAdmin(admin.ModelAdmin):
    # Usamos los nombres de campos reales de tu modelo Municipio
    list_display = (
        'id', 
        'municipio', 
        'id_estado', 
        'iestado',     
        'ialtafecha'    
    )
    list_filter = ('iestado',) 
    search_fields = ('municipio',)

# --- Admin para MarcaVehiculo ---
class MarcaVehiculoAdmin(admin.ModelAdmin):
    # Corregido: list_display usa los nuevos campos
    list_display = (
        'marca', 
        'iestado', 
        'ialtafecha', 
        'icapturo', 
        'imodificadofecha',
        'imodifico'
    )
    
    list_filter = ('iestado',) 
    search_fields = ('marca',) 
    
    # Corregido: readonly_fields usa los nuevos campos de auditoría
    readonly_fields = (
        'ialtafecha', 'ialtahora', 'imodificadofecha', 'imodificadohora', 
        'icapturo', 'imodifico'
    )

# --- Admin para TipoVehiculo ---
class TipoVehiculoAdmin(admin.ModelAdmin):
    list_display = ('marca', 'nombre', 'activo')
    list_filter = ('marca', 'activo')
    search_fields = ('nombre',)

# --- Admin para TipoDocumento ---
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'obligatorio', 'activo')
    list_filter = ('categoria', 'obligatorio', 'activo')
    search_fields = ('nombre',)

# --- REGISTRO DE MODELOS (¡Una sola vez por modelo!) ---
admin.site.register(Municipio, MunicipioAdmin)
admin.site.register(MarcaVehiculo, MarcaVehiculoAdmin)
admin.site.register(TipoVehiculo, TipoVehiculoAdmin)
admin.site.register(TipoDocumento, TipoDocumentoAdmin)

# Nota: Solicitud la dejaremos sin registrar aquí si planeas registrarla en vehiculos/admin.py
# Si quieres que Solicitud se administre aquí:
# admin.site.register(Solicitud)