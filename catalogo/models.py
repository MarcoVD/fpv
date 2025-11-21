from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

class Municipio(models.Model):
    # Campos funcionales
    # ----------------------------------------------------------------------
    municipio = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Municipio"
    )
    
    # Asumiendo que es un campo entero simple para el ID de estado
    id_estado = models.IntegerField(
        verbose_name="ID de Estado", 
        db_column='id_estado'
    )
    
    # Estado de activación (usado en ConcesionForm)
    iestado = models.IntegerField(
        default=1,
        verbose_name="Estado (1=Activo, 0=Inactivo)"
    )

    # Campos de Auditoría (Trazabilidad)
    # ----------------------------------------------------------------------
    ialtafecha = models.DateField(
        default=timezone.now, # 🛠️ CORREGIDO
        verbose_name="Fecha de Alta",
        db_column='ialtafecha'
    )
    ialtahora = models.TimeField(
        default=timezone.now, # 🛠️ CORREGIDO
        verbose_name="Hora de Alta",
        db_column='ialtahora'
    )
    imodificadofecha = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Modificación",
        db_column='imodificadofecha'
    )
    imodificadohora = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora de Modificación",
        db_column='imodificadohora'
    )
    
    # El usuario que crea (icapturo)
    icapturo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='municipios_creados',
        verbose_name="Usuario que Capturó",
        db_column='icapturo',
        null=True # Permitir Null si no se asigna al inicio
    )
    
    # El usuario que modifica (imodifico)
    imodifico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='municipios_modificados',
        verbose_name="Usuario que Modificó",
        db_column='imodifico',
        null=True,
        blank=True
    )
    
    def __str__(self):
        return self.municipio
    
class MarcaVehiculo(models.Model):
    """Catálogo de marcas de vehículos con campos de auditoría"""
    marca = models.CharField(max_length=50, verbose_name="Marca")
    
    # Reemplaza 'activo' por 'iestado' para consistencia con la auditoría
    iestado = models.IntegerField(
        default=1,
        verbose_name="Estado (1=Activo, 0=Inactivo)"
    )
    
    # Campos de Auditoría (Los que faltaban y generaban errores E035/E108/E116)
    ialtafecha = models.DateField(auto_now_add=True, null=True, blank=True)
    ialtahora = models.DateTimeField(auto_now_add=True, null=True, blank=True) # Usamos DateTimeField para hora precisa
    imodificadofecha = models.DateField(auto_now=True, null=True, blank=True)
    imodificadohora = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    # Usamos settings.AUTH_USER_MODEL
    icapturo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        related_name='marcas_capturadas',
        verbose_name="Usuario Capturó",
        null=True
    )
    imodifico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='marcas_modificadas',
        verbose_name="Usuario Modificó",
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Marca de Vehículo"
        verbose_name_plural = "Marcas de Vehículos"
        ordering = ['marca']
    
    def __str__(self):
        return self.marca

class TipoVehiculo(models.Model):
    """Catálogo de tipos/modelos de vehículos"""
    marca = models.ForeignKey(MarcaVehiculo, on_delete=models.CASCADE, related_name='tipos')
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Tipo de Vehículo"
        verbose_name_plural = "Tipos de Vehículos"
        # CORRECCIÓN DE ERROR E015: Cambiar 'marca__nombre' por 'marca__marca'
        ordering = ['marca__marca', 'nombre']
    
    def __str__(self):
        # CORRECCIÓN: el campo ahora se llama 'marca'
        return f"{self.marca.marca} - {self.nombre}"

class TipoDocumento(models.Model):
    """Catálogo de tipos de documentos"""
    CATEGORIA_CHOICES = [
        ('personal', 'Personal'),
        ('vehiculo', 'Vehículo'),
        ('empresa', 'Empresa'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    obligatorio = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Tipo de Documento"
        verbose_name_plural = "Tipos de Documentos"
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return self.nombre
    
class Solicitud(models.Model):
    # ... (El resto de tus campos) ...
    
    # Campo usado para la validación de unicidad
    clave_concesion = models.CharField(max_length=50) 
    
    # Campo usado en el formulario
    municipio_operacion = models.ForeignKey(Municipio, on_delete=models.PROTECT) 
    
    # ... (El resto de tus campos) ...