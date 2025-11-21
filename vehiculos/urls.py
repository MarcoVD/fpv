from django.urls import path
from . import views

app_name = 'vehiculos'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('iniciar/', views.iniciar_proceso_view, name='iniciar_proceso'),
    path('titulo/', views.titulo_view, name='titulo'),
    path('persona-fisica/', views.persona_fisica_view, name='persona_fisica'),
    path('persona-moral/', views.persona_moral_view, name='persona_moral'),
    path('domicilio/', views.domicilio_view, name='domicilio'),
    path('domicilio-moral/', views.domicilio_moral_view, name='domicilio_moral'),
    path('representante-legal/', views.representante_legal_view, name='representante_legal'),
    path('vehiculo/', views.vehiculo_view, name='vehiculo'),
    path('documentos-fisica/', views.documentos_fisica_view, name='documentos_fisica'),
    path('documentos-moral/', views.documentos_moral_view, name='documentos_moral'),
    path('documentos-vehiculo/', views.documentos_vehiculo_view, name='documentos_vehiculo'),
    path('finalizar/', views.finalizar_view, name='finalizar'),
    
    # API
    path('api/tipos-vehiculo/', views.obtener_tipos_vehiculo, name='obtener_tipos_vehiculo'),
    path('api/subir-documento/', views.subir_documento, name='subir_documento'),  # NUEVA
]