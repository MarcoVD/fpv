from django import forms
from django.core.exceptions import ValidationError
from vehiculos.models import Solicitud, Documento, PersonaFisica
from catalogo.models import Municipio
import re

# Constantes para la validación de CURP y RFC
CURP_REGEX = r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]{2}$'
RFC_REGEX = r'^([A-ZÑ&]{3,4}\d{6}[A-V1-9][A-Z1-9][0-9A])?$'

class DocumentoForm(forms.ModelForm):
    """Formulario para subir documentos"""
    
    class Meta:
        model = Documento
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            })
        }
    
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        
        if archivo:
            # Validar tamaño (máximo 5MB)
            if archivo.size > 5 * 1024 * 1024:
                raise ValidationError('El archivo no debe superar los 5MB')
            
            # Validar tipo de archivo
            tipos_permitidos = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
            if archivo.content_type not in tipos_permitidos:
                raise ValidationError('Solo se permiten archivos PDF, JPG o PNG')
        
        return archivo
    
class ConcesionForm(forms.Form):
    # Campo 1: Clave de la Concesión
    concesion = forms.CharField(
        label="Clave de la concesión:",
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'})
    )

    # Campo 2: Municipio de Operación 
    municipio = forms.ModelChoiceField(
        # Aplicamos el filtro para solo mostrar municipios activos (iestado=1)
        queryset=Municipio.objects.filter(iestado=1, id_estado=15).order_by('municipio'),
        label="Municipio de Operación:",
        empty_label="-- Seleccione una opción --",
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'})
    )

    # Campo 3: Tipo de Persona (ChoiceField)
    TIPO_PERSONA_CHOICES = [
        ('fisica', 'Persona Física'),
        ('moral', 'Persona Moral'),
    ]
    tipo_persona = forms.ChoiceField(
        label="Tipo de Persona:",
        choices=TIPO_PERSONA_CHOICES,
        widget=forms.RadioSelect(attrs={'required': 'required'})
    )

    def clean_concesion(self):
        """
        Valida que la clave de concesión no exista en el modelo Solicitud.
        """
        clave_concesion = self.cleaned_data.get('concesion')

        if Solicitud.objects.filter(clave_concesion=clave_concesion).exists():
            raise forms.ValidationError(
                "No se puede realizar porque ya existe el registro."
            )
        
        return clave_concesion
    
# -----------------------------------------------------------
# CLASE CORREGIDA: PersonaFisicaForm
# -----------------------------------------------------------

# 🟢 CORRECCIÓN CLAVE: Cambiar forms.Form a forms.ModelForm
class PersonaFisicaForm(forms.ModelForm): 

    class Meta: 
        model = PersonaFisica
        fields = [
            'nombre', 'primer_apellido', 'segundo_apellido', 'curp', 
            'rfc', 'regimen_fiscal', 'sexo', 'fecha_nacimiento', 
            'telefono', 'movil'
        ]

    # Campos que ya tenías (se mantienen para aplicar widgets y labels)
    nombre = forms.CharField(max_length=100, label='Nombre(s)')
    primer_apellido = forms.CharField(max_length=100, label='Primer Apellido')
    segundo_apellido = forms.CharField(max_length=100, required=False, label='Segundo Apellido')
    
    curp = forms.CharField(
        max_length=18,
        label='CURP',
        help_text='Clave Única de Registro de Población (18 caracteres).',
        widget=forms.TextInput(attrs={'placeholder': 'Ej. PERE900101HDFRRA09', 'class': 'form-control'})
    )
    
    rfc = forms.CharField(max_length=13, label='RFC', widget=forms.TextInput(attrs={'class': 'form-control'}))
    regimen_fiscal = forms.CharField(max_length=100, label='Régimen Fiscal', widget=forms.TextInput(attrs={'class': 'form-control'}))
    sexo = forms.ChoiceField(
        choices=[('', '-- Seleccione --'), ('M', 'Mujer'), ('H', 'Hombre')],
        label='Sexo',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    telefono = forms.CharField(max_length=15, required=False, label='Teléfono fijo', widget=forms.TextInput(attrs={'class': 'form-control'}))
    movil = forms.CharField(max_length=15, label='Teléfono móvil', widget=forms.TextInput(attrs={'class': 'form-control'}))

    # --- Validaciones Personalizadas (ahora self.instance funcionará) ---

    def clean_curp(self):
        curp = self.cleaned_data.get('curp').upper()
        
        # 1. Validaciones de formato y longitud
        if len(curp) != 18:
            raise forms.ValidationError('La CURP debe tener exactamente 18 caracteres.')
        
        if not re.match(CURP_REGEX, curp):
            raise forms.ValidationError('La CURP no tiene un formato válido (4 letras, 6 números, 8 alfanuméricos).')
            
        # 2. Lógica de validación de UNICIDAD (usando self.instance)
        query = PersonaFisica.objects.filter(curp=curp)
        
        # Excluir la instancia actual si estamos en modo edición (requiere self.instance)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk) 

        # Si la consulta aún tiene resultados, significa que existe otro objeto con ese CURP
        if query.exists():
             raise forms.ValidationError(
                 "❌ **ERROR:** Este CURP ya está registrado en el sistema. No puede continuar con el registro."
              )
        
        return curp 

    def clean_rfc(self):
        rfc = self.cleaned_data.get('rfc').upper()
        
        # 1. Validaciones de formato y longitud
        if len(rfc) not in [12, 13]:
            raise forms.ValidationError('El RFC debe tener 12 o 13 caracteres.')
        
        if not re.match(RFC_REGEX, rfc):
            raise forms.ValidationError('El RFC no tiene un formato válido.')

        # 2. Lógica de validación de UNICIDAD (usando self.instance)
        query = PersonaFisica.objects.filter(rfc=rfc)
        
        # Excluir la instancia actual si estamos en modo edición (requiere self.instance)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk) 

        if query.exists():
             raise forms.ValidationError(
                 "❌ **ERROR:** Este RFC ya está registrado en el sistema. No puede continuar con el registro."
              )

        return rfc