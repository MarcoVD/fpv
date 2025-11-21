# ========== catalogo/urls.py ==========
from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    # APIs para obtener datos de catálogos (opcional, para AJAX)
    # path('api/municipios/', views.municipios_json, name='municipios_json'),
    # path('api/marcas/', views.marcas_json, name='marcas_json'),
]