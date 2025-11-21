from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
# Importación correcta: Usar get_user_model() es la mejor práctica
from django.contrib.auth import get_user_model 
from django.contrib import messages
from django.utils import timezone
from .models import Perfil # Tu modelo de perfil personalizado
from .forms import RegistrationForm # Tu formulario de registro
from .emails import enviar_email_activacion # Tu módulo de correos
from .emails import enviar_email_bienvenida

User = get_user_model()

# -----------------------------------------------------------------------------------
# Vista de INICIO DE SESIÓN
# (Código mantenido igual)
# -----------------------------------------------------------------------------------
def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('vehiculos:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # 💡 CORRECCIÓN CLAVE: Usamos filter().first() en lugar de get() 
        # para evitar el error MultipleObjectsReturned si el email está duplicado
        user_obj = User.objects.filter(email=email).first()
        
        if user_obj:
            # Intentar autenticar usando el username del objeto encontrado
            user = authenticate(request, username=user_obj.username, password=password)
            
            if user is not None:
                # Verificar si la cuenta está activada (usando el modelo Perfil)
                if user.perfil.cuenta_activada:
                    login(request, user)
                    messages.success(request, f'¡Bienvenido {user.username}!')
                    return redirect('vehiculos:dashboard')
                else:
                    messages.warning(request, 'Debes activar tu cuenta primero. Revisa tu correo.')
                    return redirect('accounts:activar_cuenta') 
            else:
                messages.error(request, 'Correo o contraseña incorrectos')
        else:
            messages.error(request, 'No existe una cuenta con este correo electrónico')
        
    return render(request, 'accounts/login.html')

# -----------------------------------------------------------------------------------
# Vista de CERRAR SESIÓN
# (Código mantenido igual)
# -----------------------------------------------------------------------------------
@login_required
def logout_view(request):
    """Vista de cerrar sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('core:index')

# -----------------------------------------------------------------------------------
# Vista de REGISTRO (FINALIZADA)
# -----------------------------------------------------------------------------------
def registro_view(request):
    """Vista de registro de usuario"""
    if request.user.is_authenticated:
        return redirect('vehiculos:dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            try:
                # --- LÓGICA DE CREACIÓN DE USUARIO ---
                
                # 1. Generar Username único (Mantenemos tu lógica para evitar conflictos)
                username = email.split('@')[0] 
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # 2. Crear usuario y asignarle contraseña
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password 
                )
                
                # 3. Crear o obtener perfil (que genera el token)
                # NOTA: En tu modelo Perfil, asegúrate de que el campo 'token_activacion'
                # se genere automáticamente al crear la instancia.
                perfil, created = Perfil.objects.get_or_create(user=user)
                
                # 4. Enviar email de activación (Usando tu módulo accounts/emails.py)
                if enviar_email_activacion(user, perfil):
                    messages.success(request, '¡Cuenta creada! Revisa tu correo electrónico para el enlace de activación.')
                else:
                    # Mensaje de respaldo si el envío de correo falla
                    messages.warning(
                        request, 
                        'Cuenta creada. **Atención:** No pudimos enviar el correo de activación. Por favor, ingresa tu token manualmente.'
                    )
                
                # 5. Redirigir a la página donde el usuario ingresará el token
                return redirect('accounts:activar_cuenta') 
                
            except Exception as e:
                # Mensaje genérico de error en la creación
                messages.error(request, f'Error al crear la cuenta. Por favor, inténtalo de nuevo. Detalle: {str(e)}')
                
    else: # GET request
        form = RegistrationForm()
        
    context = {
        'form': form
    }
    return render(request, 'accounts/registro.html', context)


# -----------------------------------------------------------------------------------
# Vista de ACTIVAR CUENTA
# (Código mantenido igual, pero debería recibir el token en el POST si no viene en URL)
# -----------------------------------------------------------------------------------
def activar_cuenta_view(request, token=None):
    """Vista para activar cuenta con token"""
    if request.method == 'POST':
        email = request.POST.get('email')
        token_input = request.POST.get('token')
        
        try:
            user = User.objects.get(email=email)
            perfil = user.perfil
            
            if str(perfil.token_activacion) == token_input:
                perfil.cuenta_activada = True
                perfil.fecha_activacion = timezone.now()
                perfil.save()
                
                # Lógica de Bienvenida (Opcional: usar el correo de bienvenida que definiste)
                from .emails import enviar_email_bienvenida 
                enviar_email_bienvenida(user) # Enviar correo de bienvenida

                messages.success(request, '¡Cuenta activada exitosamente! Ya puedes iniciar sesión.')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Token inválido')
        except User.DoesNotExist:
            messages.error(request, 'No existe una cuenta con este correo electrónico')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'accounts/activar_cuenta.html', {'token': token})