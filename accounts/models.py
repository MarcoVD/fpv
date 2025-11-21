from django.db import models
from django.contrib.auth.models import User
import uuid
from django.conf import settings



class Perfil(models.Model):
    """Perfil extendido del usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=15, blank=True)
    telefono_movil = models.CharField(max_length=15, blank=True)
    
    # Token para activación de cuenta
    token_activacion = models.UUIDField(default=uuid.uuid4, editable=False)
    cuenta_activada = models.BooleanField(default=False)
    fecha_activacion = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    
    
