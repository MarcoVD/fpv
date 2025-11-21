# forms.py en tu aplicación
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class RegistrationForm(forms.Form):
    # Campo para el correo electrónico
    email = forms.EmailField(
        label='Correo Electrónico',
        max_length=254,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'required': 'required'})
    )

    # Campo para la primera contraseña
    password = forms.CharField(
        label='Contraseña',
        # Importante para preservar el espaciado si el usuario lo pone (aunque se recomienda validarlo)
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'required': 'required'})
    )

    # Campo para confirmar la contraseña
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'required': 'required'})
    )

    # Checkbox para aceptar términos/aviso de privacidad
    # El widget se manejará mejor en la plantilla, pero el campo es necesario para la validación
    acepto_terminos = forms.BooleanField(
        label='He leído y acepto el aviso de privacidad',
        required=True,  # Debe estar marcado para que el formulario sea válido
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_email(self):
        """
        Valida que el correo electrónico no esté ya registrado.
        """
        email = self.cleaned_data.get('email')

        # 1. Asegurarse de que el correo está en minúsculas para una comparación uniforme
        if email:
            email = email.lower()

        # 2. Consultar la base de datos para ver si ya existe un usuario con ese email
        if User.objects.filter(email=email).exists():
            # Si el usuario ya existe, lanza un error de validación
            raise forms.ValidationError(
                "Este correo electrónico ya está registrado.")

        # 3. Retornar el valor "limpiado" y potencialmente modificado (en este caso, a minúsculas)
        return email

    def clean(self):
        """
        Validaciones que dependen de varios campos, como:
        1. Las contraseñas coinciden.
        2. La contraseña cumple con los requisitos del validador de Django.
        """
        super().clean()
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")

        # 1. Validar que las contraseñas coincidan
        if password and password2 and password != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')

        # 2. Validar que la contraseña cumpla con los requisitos
        if password:
            try:
                # Usa el validador de contraseñas de Django
                validate_password(password)
            except ValidationError as e:
                # Añade los errores del validador al campo 'password'
                self.add_error('password', e)

        return self.cleaned_data
