# vehiculos\models.py

from django.db import models
from django.contrib.auth.models import User
# Importamos todos los modelos de catálogo necesarios desde la aplicación 'catalogo'
from catalogo.models import Municipio, MarcaVehiculo, TipoVehiculo, TipoDocumento
import uuid


class Solicitud(models.Model):
    """Solicitud de renovación vehicular"""
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('enviada', 'Enviada'),
        ('revision', 'En Revisión'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    
    TIPO_PERSONA_CHOICES = [
        ('fisica', 'Persona Física'),
        ('moral', 'Persona Moral'),
    ]
    
    # Relaciones
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes')
    
    # Datos de la solicitud
    folio = models.CharField(max_length=50, unique=True, editable=False)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    tipo_persona = models.CharField(max_length=10, choices=TIPO_PERSONA_CHOICES)
    
    # Datos de concesión
    clave_concesion = models.CharField(max_length=50)
    # CORRECCIÓN DE E304: Se añade related_name único
    municipio_operacion = models.ForeignKey(
        Municipio, 
        on_delete=models.SET_NULL, # O models.CASCADE
        null=True,  # Permitir que el campo esté nulo inicialmente
        blank=True,
        verbose_name="Municipio de Operación",
        related_name="solicitudes_operacion"
    )
    
    # Timestamps
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Solicitud"
        verbose_name_plural = "Solicitudes"
        ordering = ['-creado']
    
    def __str__(self):
        return f"{self.folio} - {self.usuario.username}"
    
    def save(self, *args, **kwargs):
        if not self.folio:
            # Generar folio único
            ultimo_id = Solicitud.objects.count() + 1
            self.folio = f"SEMOV-EDOMEX-25-{ultimo_id:05d}"
        super().save(*args, **kwargs)


class PersonaFisica(models.Model):
    """Datos de persona física"""
    SEXO_CHOICES = [
        ('M', 'Mujer'),
        ('H', 'Hombre'),
    ]
    
    solicitud = models.OneToOneField(Solicitud, on_delete=models.CASCADE, related_name='persona_fisica')
    
    # Datos personales
    nombre = models.CharField(max_length=100)
    primer_apellido = models.CharField(max_length=100)
    segundo_apellido = models.CharField(max_length=100, blank=True)
    curp = models.CharField(
        max_length=18, 
        unique=True,
        null=True,   # <- NECESARIO para que la migración pase con datos existentes
        blank=True,  # <- NECESARIO para que el formulario no lo requiera si es nulo
        verbose_name="CURP"
    )
    rfc = models.CharField(
        max_length=13,
        unique=True, # <- ¡CLAVE!
        verbose_name="RFC"
    )
    regimen_fiscal = models.CharField(max_length=100)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    fecha_nacimiento = models.DateField()
    
    # Contacto
    telefono_fijo = models.CharField(max_length=15, blank=True)
    telefono_movil = models.CharField(max_length=15)
    
    class Meta:
        verbose_name = "Persona Física"
        verbose_name_plural = "Personas Físicas"
    
    def __str__(self):
        return f"{self.nombre} {self.primer_apellido} {self.segundo_apellido}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.primer_apellido} {self.segundo_apellido}".strip()


class PersonaMoral(models.Model):
    """Datos de persona moral"""
    solicitud = models.OneToOneField(Solicitud, on_delete=models.CASCADE, related_name='persona_moral')
    
    # Datos de la empresa
    razon_social = models.CharField(max_length=200)
    rfc = models.CharField(
        max_length=13,
        unique=True # <- ¡CLAVE!
    )
    regimen_fiscal = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Persona Moral"
        verbose_name_plural = "Personas Morales"
    
    def __str__(self):
        return self.razon_social


class RepresentanteLegal(models.Model):
    """Representante legal de persona moral"""
    SEXO_CHOICES = [
        ('M', 'Mujer'),
        ('H', 'Hombre'),
    ]
    
    persona_moral = models.OneToOneField(PersonaMoral, on_delete=models.CASCADE, related_name='representante')
    
    # Datos personales
    nombre = models.CharField(max_length=100)
    primer_apellido = models.CharField(max_length=100)
    segundo_apellido = models.CharField(max_length=100, blank=True)
    rfc = models.CharField(max_length=13)
    regimen_fiscal = models.CharField(max_length=100)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    fecha_nacimiento = models.DateField()
    
    # Contacto
    telefono_fijo = models.CharField(max_length=15, blank=True)
    telefono_movil = models.CharField(max_length=15)
    
    class Meta:
        verbose_name = "Representante Legal"
        verbose_name_plural = "Representantes Legales"
    
    def __str__(self):
        return f"{self.nombre} {self.primer_apellido} {self.segundo_apellido}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.primer_apellido} {self.segundo_apellido}".strip()


class Domicilio(models.Model):
    """Domicilio del titular o fiscal"""
    TIPO_CHOICES = [
        ('titular', 'Domicilio del Titular'),
        ('fiscal', 'Domicilio Fiscal'),
    ]
    
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='domicilios')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    
    # Dirección
    codigo_postal = models.CharField(max_length=5)
    estado = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    colonia = models.CharField(max_length=100)
    calle = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = "Domicilio"
        verbose_name_plural = "Domicilios"
    
    def __str__(self):
        return f"{self.calle}, {self.colonia}, {self.municipio}"


class Vehiculo(models.Model):
    """Datos del vehículo a solicitar"""
    solicitud = models.OneToOneField(Solicitud, on_delete=models.CASCADE, related_name='vehiculo')
    
    # Datos del vehículo
    marca = models.ForeignKey(MarcaVehiculo, on_delete=models.PROTECT)
    tipo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT)
    
    # Datos adicionales que se pueden agregar después
    placas = models.CharField(max_length=20, blank=True)
    numero_serie = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
    
    def __str__(self):
        return f"{self.marca} {self.tipo}"


class Documento(models.Model):
    """Documentos subidos por el usuario"""
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT)
    
    # Archivo
    archivo = models.FileField(upload_to='documentos/%Y/%m/')
    nombre_original = models.CharField(max_length=255)
    tamano = models.IntegerField(help_text="Tamaño en bytes")
    
    # Metadatos
    subido_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-subido_en']
    
    def __str__(self):
        return f"{self.tipo_documento.nombre} - {self.solicitud.folio}"