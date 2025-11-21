from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    
    # 1. Ruta base: Para cuando el usuario debe ingresar el token manualmente (sin token en la URL).
    # Esta es la URL que se usará al redirigir desde login_view.
    path('activar/', views.activar_cuenta_view, name='activar_cuenta'),

    # 2. Ruta con argumento: Para cuando el usuario viene desde un enlace de correo o registro.
    path('activar/<str:token>/', views.activar_cuenta_view, name='activar_cuenta'),
]