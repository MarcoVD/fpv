from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from vehiculos.models import Solicitud, Documento, PersonaFisica, RepresentanteLegal, Vehiculo
from catalogo.models import Municipio, MarcaVehiculo, TipoVehiculo
import re

# Constantes para la validación de CURP y RFC
CURP_REGEX = r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]{2}$'
RFC_REGEX = r'^([A-Z&]{3,4}\d{6}[A-V1-9][A-Z1-9][0-9A])?$'

# Palabras inconvenientes prohibidas por el SAT
PALABRAS_INCONVENIENTES_RFC = {
    'BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO', 'CAKA', 'CAKO',
    'COGE', 'COGI', 'COJA', 'COJE', 'COJI', 'COJO', 'COLA', 'CULO',
    'FALO', 'FETO', 'GETA', 'GUEI', 'GUEY', 'JETA', 'JOTO', 'KACA',
    'KACO', 'KAGA', 'KAGO', 'KAKA', 'KAKO', 'KOGE', 'KOGI', 'KOJA',
    'KOJE', 'KOJI', 'KOJO', 'KOLA', 'KULO', 'LILO', 'LOCA', 'LOCO',
    'LOKA', 'LOKO', 'MAME', 'MAMO', 'MEAR', 'MEAS', 'MEON', 'MIAR',
    'MION', 'MOCO', 'MOKO', 'MULA', 'MULO', 'NACA', 'NACO', 'PEDA',
    'PEDO', 'PENE', 'PIPI', 'PITO', 'POPO', 'PUTA', 'PUTO', 'QULO',
    'RATA', 'ROBA', 'ROBE', 'ROBO', 'RUIN', 'SENO', 'TETA', 'VACA',
    'VAGA', 'VAGO', 'VAKA', 'VUEI', 'VUEY', 'WUEI', 'WUEY'
}

# Caracteres válidos para RFC (sin Ñ)
RFC_CARACTERES_VALIDOS = r'^[A-Z0-9]+$'


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
            tipos_permitidos = ['application/pdf',
                                'image/jpeg', 'image/jpg', 'image/png']
            if archivo.content_type not in tipos_permitidos:
                raise ValidationError(
                    'Solo se permiten archivos PDF, JPG o PNG')

        return archivo


class ConcesionForm(forms.Form):
    # Campo 1: Clave de la Concesión
    concesion = forms.CharField(
        label="Clave de la concesión:",
        max_length=50,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'required': 'required'})
    )

    # Campo 2: Municipio de Operación
    municipio = forms.ModelChoiceField(
        # Aplicamos el filtro para solo mostrar municipios activos (iestado=1)
        queryset=Municipio.objects.filter(
            iestado=1, id_estado=15).order_by('municipio'),
        label="Municipio de Operación:",
        empty_label="-- Seleccione una opción --",
        widget=forms.Select(
            attrs={'class': 'form-select', 'required': 'required'})
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

#  CORRECCIÓN CLAVE: Cambiar forms.Form a forms.ModelForm


class PersonaFisicaForm(forms.ModelForm):

    class Meta:
        model = PersonaFisica
        fields = [
            'nombre', 'primer_apellido', 'segundo_apellido', 'curp',
            'rfc', 'regimen_fiscal', 'sexo', 'fecha_nacimiento',
            'telefono_fijo', 'telefono_movil'
        ]

    # Campos que ya tenías (se mantienen para aplicar widgets y labels)
    nombre = forms.CharField(max_length=100, label='Nombre(s)')
    primer_apellido = forms.CharField(max_length=100, label='Primer Apellido')
    segundo_apellido = forms.CharField(
        max_length=100, required=False, label='Segundo Apellido')

    curp = forms.CharField(
        max_length=18,
        label='CURP',
        help_text='Clave Única de Registro de Población (18 caracteres).',
        widget=forms.TextInput(
            attrs={'placeholder': 'Ej. PERE900101HDFRRA09', 'class': 'form-control'})
    )

    rfc = forms.CharField(max_length=13, label='RFC',
                          widget=forms.TextInput(attrs={
                              'class': 'form-control',
                              'style': 'text-transform: uppercase;',
                          }))
    regimen_fiscal = forms.CharField(
        max_length=100, label='Régimen Fiscal', widget=forms.TextInput(attrs={'class': 'form-control'}))
    sexo = forms.ChoiceField(
        choices=[('', '-- Seleccione --'), ('M', 'Mujer'), ('H', 'Hombre')],
        label='Sexo',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    # Validador para teléfonos
    telefono_validator = RegexValidator(
        regex=r'^\d{10}$',
        message='El teléfono debe contener exactamente 10 dígitos numéricos.'
    )

    telefono_fijo = forms.CharField(
        max_length=10,
        required=False,
        label='Teléfono fijo',
        validators=[telefono_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'tel',
            'pattern': '[0-9]{10}',
            'placeholder': 'Ej. 5512345678'
        })
    )
    telefono_movil = forms.CharField(
        max_length=10,
        label='Teléfono móvil',
        validators=[telefono_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'tel',
            'pattern': '[0-9]{10}',
            'placeholder': 'Ej. 5512345678'
        })
    )

    # --- Validaciones Personalizadas (ahora self.instance funcionará) ---

    def clean_curp(self):
        curp = self.cleaned_data.get('curp').upper()

        # 1. Validaciones de formato y longitud
        if len(curp) != 18:
            raise forms.ValidationError(
                'La CURP debe tener exactamente 18 caracteres.')

        if not re.match(CURP_REGEX, curp):
            raise forms.ValidationError(
                'La CURP no tiene un formato válido (4 letras, 6 números, 8 alfanuméricos).')

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
        rfc_original = self.cleaned_data.get('rfc', '')

        # Limpiar caracteres no válidos (sin Ñ)
        rfc_limpio = re.sub(r'[^A-Z0-9]', '', rfc_original.upper())

        # Validar que no contenga caracteres especiales prohibidos
        if not re.match(RFC_CARACTERES_VALIDOS, rfc_limpio):
            raise forms.ValidationError(
                'El RFC contiene caracteres no válidos. Solo se permiten letras, números.'
            )

        # 1. Validaciones de formato y longitud
        if len(rfc_limpio) not in [12, 13]:
            raise forms.ValidationError(
                'El RFC debe tener 12 o 13 caracteres válidos.'
            )

        # 2. Validar formato con regex
        if not re.match(RFC_REGEX, rfc_limpio):
            raise forms.ValidationError('El RFC no tiene un formato válido.')

        # 3. Verificar palabras inconvenientes
        primeras_letras = rfc_limpio[:4] if len(
            rfc_limpio) == 13 else rfc_limpio[:3]
        if primeras_letras in PALABRAS_INCONVENIENTES_RFC:
            raise forms.ValidationError(
                f'El RFC "{primeras_letras}" no es válido según las reglas del SAT.'
            )

        # 4. Lógica de validación de UNICIDAD (usando self.instance)
        query = PersonaFisica.objects.filter(rfc=rfc_limpio)

        # Excluir la instancia actual si estamos en modo edición
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)

        if query.exists():
            raise forms.ValidationError(
                "❌ **ERROR:** Este RFC ya está registrado en el sistema. No puede continuar con el registro."
            )

        return rfc_limpio


class PersonaMoralForm(forms.Form):
    # Campos para Persona Moral
    razon_social = forms.CharField(
        max_length=200,
        label='Razón Social',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'text-transform: uppercase;'
        })
    )
    rfc = forms.CharField(
        max_length=12,
        label='RFC',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'text-transform: uppercase;'
        })
    )
    regimen_fiscal = forms.CharField(
        max_length=100,
        label='Régimen Fiscal',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Validador para teléfonos
    telefono_validator = RegexValidator(
        regex=r'^\d{10}$',
        message='El teléfono debe contener exactamente 10 dígitos numéricos.'
    )

    telefono = forms.CharField(
        max_length=10,
        required=False,
        label='Teléfono fijo',
        validators=[telefono_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'tel',
            'pattern': '[0-9]{10}',
            'placeholder': 'Ej. 5512345678'
        })
    )
    movil = forms.CharField(
        max_length=10,
        required=False,
        label='Teléfono móvil',
        validators=[telefono_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'tel',
            'pattern': '[0-9]{10}',
            'placeholder': 'Ej. 5512345678'
        })
    )

    def clean_rfc(self):
        rfc = self.cleaned_data.get('rfc').upper()

        # 1. Validaciones de formato y longitud
        if len(rfc) not in [12, 13]:
            raise forms.ValidationError(
                'El RFC debe tener 12 o 13 caracteres.')

        if not re.match(RFC_REGEX, rfc):
            raise forms.ValidationError('El RFC no tiene un formato válido.')

        return rfc


class RepresentanteLegalForm(forms.ModelForm):

    class Meta:
        model = RepresentanteLegal
        fields = [
            'nombre', 'primer_apellido', 'segundo_apellido', 'rfc',
            'regimen_fiscal', 'sexo', 'fecha_nacimiento',
            'telefono_fijo', 'telefono_movil'
        ]

    nombre = forms.CharField(
        max_length=200,
        label='Nombre(s)',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Ej. Juan'})
    )
    primer_apellido = forms.CharField(
        max_length=100,
        label='Primer Apellido',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Ej. Pérez'})
    )
    segundo_apellido = forms.CharField(
        max_length=100,
        required=False,
        label='Segundo Apellido',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Ej. López'})
    )
    rfc = forms.CharField(
        max_length=13,
        label='RFC',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'text-transform: uppercase;',
            'maxlength': '13'
        })
    )
    regimen_fiscal = forms.CharField(
        max_length=100,
        label='Régimen Fiscal',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    sexo = forms.ChoiceField(
        choices=[('', '-- Seleccione --'), ('M', 'Mujer'), ('H', 'Hombre')],
        label='Sexo',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    # Validador para teléfonos
    telefono_validator = RegexValidator(
        regex=r'^\d{10}$',
        message='El teléfono debe contener exactamente 10 dígitos numéricos.'
    )

    telefono_fijo = forms.CharField(
        max_length=10,
        required=False,
        label='Teléfono fijo',
        validators=[telefono_validator],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'tel',
                'pattern': '[0-9]{10}',
                'placeholder': 'Ej. 5512345678'
            })
    )
    telefono_movil = forms.CharField(
        max_length=10,
        label='Teléfono móvil',
        validators=[telefono_validator],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'tel',
                'pattern': '[0-9]{10}',
                'placeholder': 'Ej. 5512345678'
            })
    )


class VehiculoForm(forms.ModelForm):
    """
    Formulario para registrar datos del vehículo.

    NOTA IMPORTANTE sobre ForeignKey en ModelForm:
    - Los campos 'marca' y 'tipo' son ForeignKey en el modelo
    - Django automáticamente los convierte en ModelChoiceField
    - NO necesitas redefinirlos aquí, solo personalizarlos si quieres
    """

    class Meta:
        model = Vehiculo
        # Excluimos 'solicitud' porque se asigna en la vista
        fields = ['marca', 'tipo', 'placas', 'numero_serie']

        # Personalizar widgets y labels
        widgets = {
            'marca': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'placas': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. ABC-123-D',
                'style': 'text-transform: uppercase;',
                'maxlength': '20'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. 3VWFE21C04M000001',
                'style': 'text-transform: uppercase;',
                'maxlength': '50'
            }),
        }

        labels = {
            'marca': 'Marca del Vehículo',
            'tipo': 'Tipo de Vehículo',
            'placas': 'Placas',
            'numero_serie': 'Número de Serie (VIN)',
        }

        help_texts = {
            'numero_serie': 'Número de Identificación Vehicular (17 caracteres alfanuméricos)',
        }

    # Validación personalizada para número de serie (VIN)
    def clean_numero_serie(self):
        numero_serie = self.cleaned_data.get(
            'numero_serie', '').strip().upper()

        if numero_serie:
            # Eliminar espacios y guiones
            numero_serie_limpio = numero_serie.replace(
                ' ', '').replace('-', '')

            # Validar que solo contenga caracteres alfanuméricos
            if not numero_serie_limpio.isalnum():
                raise forms.ValidationError(
                    'El número de serie solo debe contener letras y números.'
                )

            # Opcionalmente validar longitud estándar VIN (17 caracteres)
            # Comentado porque algunos vehículos pueden tener formatos diferentes
            # if len(numero_serie_limpio) != 17:
            #     raise forms.ValidationError(
            #         'El número de serie (VIN) debe tener exactamente 17 caracteres.'
            #     )

        return numero_serie_limpio if numero_serie else ''

    def clean_placas(self):
        placas = self.cleaned_data.get('placas', '').strip().upper()
        return placas
