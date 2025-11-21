from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
import os
from .forms import ConcesionForm
from .models import Solicitud, PersonaFisica, PersonaMoral, RepresentanteLegal, Domicilio, Vehiculo, Documento
from catalogo.models import Municipio, MarcaVehiculo, TipoVehiculo, TipoDocumento
from django.views import View
from django.db.models import Q
from .forms import PersonaFisicaForm
from django.forms.models import model_to_dict

# Si tienes 'enviar_email_solicitud_recibida' en accounts/emails.py, mantenlo
# from accounts.emails import enviar_email_solicitud_recibida 


@login_required
def dashboard_view(request):
    """Dashboard principal del usuario"""
    # Mantenemos la importación local para Solicitud por si no está en .models
    from .models import Solicitud
    
    solicitudes = Solicitud.objects.filter(usuario=request.user).order_by('-creado')
    
    context = {
        'solicitudes': solicitudes,
    }
    return render(request, 'vehiculos/dashboard.html', context)

@login_required
def iniciar_proceso_view(request):
    """
    Crea una nueva Solicitud en estado 'borrador' si el usuario no tiene una activa
    y redirige al primer paso del formulario (titulo_view).
    """
    from catalogo.models import Municipio
    
    # Intentar obtener una solicitud existente en borrador
    solicitud_activa = Solicitud.objects.filter(usuario=request.user, estado='borrador').first()

    if not solicitud_activa:
        try:
            # 🟢 CLAVE: Obtener un municipio de referencia (ej. ID=1)
            # Esto es necesario para cumplir con el NOT NULL de la FK antes de que el usuario
            # ingrese los datos reales en titulo_view.
            municipio_por_defecto = Municipio.objects.get(pk=1) 
        except Municipio.DoesNotExist:
            messages.error(request, "Error interno: El municipio por defecto para iniciar la solicitud no existe. Contacte a soporte.")
            return redirect('vehiculos:dashboard')
        
        # Si no existe, crear la nueva solicitud en borrador, INYECTANDO el municipio por defecto
        solicitud_activa = Solicitud.objects.create(
            usuario=request.user,
            estado='borrador',
            municipio_operacion=municipio_por_defecto,
            # La clave_concesion y tipo_persona se actualizarán en titulo_view
        )
        messages.info(request, "Se ha iniciado una nueva solicitud.")

    # Redirigir al primer formulario
    return redirect('vehiculos:titulo')

@login_required
def titulo_view(request):
    """
    Maneja el formulario de datos de concesión (ConcesionForm) y los guarda en la Solicitud.
    """
    
    # 1. Buscar la solicitud en borrador
    solicitud_actual = Solicitud.objects.filter(usuario=request.user, estado='borrador').first()
    
    if not solicitud_actual:
        messages.error(request, 'No se encontró una solicitud activa. Por favor, inicie el proceso.')
        return redirect('vehiculos:dashboard')
    
    # Inicializar datos para el formulario
    initial_data = {}
    
    if request.method == 'POST':
        form = ConcesionForm(request.POST) 
        
        if form.is_valid():
            # 3. Guardar los datos validados directamente en la Solicitud
            solicitud_actual.clave_concesion = form.cleaned_data['concesion']
            solicitud_actual.municipio_operacion = form.cleaned_data['municipio']
            solicitud_actual.tipo_persona = form.cleaned_data['tipo_persona']
            solicitud_actual.save()
            
            # Guardar en sesión para referencia rápida en los siguientes pasos
            request.session['titulo_data'] = {
                'concesion': solicitud_actual.clave_concesion,
                'municipio': str(solicitud_actual.municipio_operacion.pk), 
                'tipo_persona': solicitud_actual.tipo_persona,
            }

            tipo = form.cleaned_data['tipo_persona']
            
            # 4. Redirigir al siguiente paso
            if tipo == 'fisica':
                return redirect('vehiculos:persona_fisica')
            elif tipo == 'moral':
                return redirect('vehiculos:persona_moral')
        
    else: # Petición GET
        # 5. Lógica para precargar datos directamente de solicitud_actual
        if solicitud_actual.clave_concesion: # Si ya tiene datos guardados
            initial_data = {
                'concesion': solicitud_actual.clave_concesion,
                'municipio': solicitud_actual.municipio_operacion.pk, 
                'tipo_persona': solicitud_actual.tipo_persona,
            }
        
        # 6. Instanciar el formulario correcto (ConcesionForm)
        form = ConcesionForm(initial=initial_data)
    
    # 7. Renderizar el template
    context = {
        'form': form,
    }
    return render(request, 'vehiculos/titulo.html', context)


# vehiculos/views.py (CÓDIGO CORREGIDO)

# vehiculos/views.py (CÓDIGO CORRECTO)

@login_required
def persona_fisica_view(request):
    """Formulario de persona física con validación y CURP"""
    
    # Buscar la solicitud activa
    solicitud_actual = Solicitud.objects.filter(usuario=request.user, estado='borrador', tipo_persona='fisica').first()
    if not solicitud_actual:
        messages.warning(request, 'No se encontró una solicitud activa de tipo física. Inicie el proceso.')
        return redirect('vehiculos:titulo')

    # 🟢 1. Obtener la instancia existente de PersonaFisica (si ya existe)
    persona_fisica_instance = None
    try:
        persona_fisica_instance = PersonaFisica.objects.get(solicitud=solicitud_actual)
    except PersonaFisica.DoesNotExist:
        pass
    
    # 2. Manejo de la petición POST
    if request.method == 'POST':
        # 🟢 CAMBIO A: Pasar la instancia al ModelForm en el POST.
        form = PersonaFisicaForm(request.POST, instance=persona_fisica_instance)
        
        if form.is_valid():
            # Obtenemos los datos limpios
            datos = form.cleaned_data
            
            # Convertimos la fecha a string para JSON (si es un objeto date)
            if 'fecha_nacimiento' in datos and datos['fecha_nacimiento']:
                datos['fecha_nacimiento'] = str(datos['fecha_nacimiento'])
            
            # Guardamos en la sesión
            request.session['persona_fisica_data'] = datos
            request.session.modified = True 
            
            # Redireccionar al siguiente paso
            return redirect('vehiculos:domicilio')
        
    # 3. Manejo de la petición GET
    else:
        # Intentar precargar desde la sesión (datos más recientes escritos por el usuario)
        session_data = request.session.get('persona_fisica_data', {})
        
        # 🟢 CAMBIO B: Usar la instancia y la sesión para precargar.
        form = PersonaFisicaForm(instance=persona_fisica_instance, initial=session_data)

    return render(request, 'vehiculos/persona_fisica.html', {'form': form})

@login_required
def persona_moral_view(request):
    """Formulario de persona moral"""
    solicitud_actual = Solicitud.objects.filter(usuario=request.user, estado='borrador', tipo_persona='moral').first()
    if not solicitud_actual:
        messages.warning(request, 'No se encontró una solicitud activa de tipo moral. Inicie el proceso.')
        return redirect('vehiculos:titulo')
    
    # NOTA: Aquí deberías usar un Form para validación y precarga, igual que en persona_fisica_view.
    # Por simplicidad, mantengo la estructura de sesión que ya tenías.
    if request.method == 'POST':
        request.session['persona_moral_data'] = {
            'razon_social': request.POST.get('razon_social'),
            'rfc': request.POST.get('rfc'),
            'regimen_fiscal': request.POST.get('regimen_fiscal'),
        }
        return redirect('vehiculos:domicilio_moral')
    
    # Si hay datos en sesión, pasarlos al contexto para precargar en el template
    initial_data = request.session.get('persona_moral_data', {})

    return render(request, 'vehiculos/persona_moral.html', {'initial_data': initial_data})


@login_required
def domicilio_view(request):
    """Formulario de domicilio (persona física)"""
    solicitud_actual = Solicitud.objects.filter(usuario=request.user, estado='borrador', tipo_persona='fisica').first()
    if not solicitud_actual or 'persona_fisica_data' not in request.session:
        messages.warning(request, 'Primero debes completar los datos personales')
        return redirect('vehiculos:persona_fisica')
    
    # NOTA: Aquí deberías usar un Form para validación y precarga.
    if request.method == 'POST':
        request.session['domicilio_data'] = {
            'codigo_postal': request.POST.get('codigo_postal'),
            'estado': request.POST.get('estado'),
            'municipio': request.POST.get('municipio'),
            'colonia': request.POST.get('colonia'),
            'calle': request.POST.get('calle'),
        }
        return redirect('vehiculos:vehiculo')
    
    initial_data = request.session.get('domicilio_data', {})
    
    return render(request, 'vehiculos/domicilio.html', {'initial_data': initial_data})


@login_required
def domicilio_moral_view(request):
    """Formulario de domicilio fiscal (persona moral)"""
    solicitud_actual = Solicitud.objects.filter(usuario=request.user, estado='borrador', tipo_persona='moral').first()
    if not solicitud_actual or 'persona_moral_data' not in request.session:
        messages.warning(request, 'Primero debes completar los datos de la empresa')
        return redirect('vehiculos:persona_moral')
    
    # NOTA: Aquí deberías usar un Form para validación y precarga.
    if request.method == 'POST':
        request.session['domicilio_moral_data'] = {
            'codigo_postal': request.POST.get('codigo_postal'),
            'estado': request.POST.get('estado'),
            'municipio': request.POST.get('municipio'),
            'colonia': request.POST.get('colonia'),
            'calle': request.POST.get('calle'),
        }
        return redirect('vehiculos:representante_legal')
    
    initial_data = request.session.get('domicilio_moral_data', {})
    
    return render(request, 'vehiculos/domicilio_persona_moral.html', {'initial_data': initial_data})


@login_required
def representante_legal_view(request):
    """Formulario de representante legal"""
    solicitud_actual = Solicitud.objects.filter(usuario=request.user, estado='borrador', tipo_persona='moral').first()
    if not solicitud_actual or 'domicilio_moral_data' not in request.session:
        messages.warning(request, 'Primero debes completar el domicilio fiscal')
        return redirect('vehiculos:domicilio_moral')
    
    # NOTA: Aquí deberías usar un Form para validación y precarga.
    if request.method == 'POST':
        # Se asume que estos datos son suficientes para la FK a RepresentanteLegal
        request.session['representante_data'] = {
            'nombre': request.POST.get('nombre'),
            'primer_apellido': request.POST.get('primer_apellido'),
            'segundo_apellido': request.POST.get('segundo_apellido'),
            'rfc': request.POST.get('rfc'),
            'regimen_fiscal': request.POST.get('regimen_fiscal'),
            'sexo': request.POST.get('sexo'),
            'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
            'telefono_fijo': request.POST.get('telefono_fijo'),
            'telefono_movil': request.POST.get('telefono_movil'),
        }
        return redirect('vehiculos:vehiculo')
    
    initial_data = request.session.get('representante_data', {})
    
    return render(request, 'vehiculos/representante_legal.html', {'initial_data': initial_data})


@login_required
def vehiculo_view(request):
    """Formulario de datos del vehículo"""
    from catalogo.models import MarcaVehiculo
    
    solicitud_actual = Solicitud.objects.filter(usuario=request.user, estado='borrador').first()
    if not solicitud_actual:
        messages.warning(request, 'Debes completar el proceso desde el inicio')
        return redirect('vehiculos:titulo')
    
    # NOTA: Aquí deberías usar un Form para validación y precarga.
    if request.method == 'POST':
        request.session['vehiculo_data'] = {
            'marca': request.POST.get('marca'),
            'tipo': request.POST.get('tipo'),
        }
        
        # Determinar a dónde redirigir según el tipo de persona guardado en la Solicitud
        tipo_persona = solicitud_actual.tipo_persona
        
        if tipo_persona == 'fisica':
            return redirect('vehiculos:documentos_fisica')
        elif tipo_persona == 'moral':
            return redirect('vehiculos:documentos_moral')
        else:
            messages.error(request, 'Tipo de persona no definido en la solicitud.')
            return redirect('vehiculos:dashboard')

    
    marcas = MarcaVehiculo.objects.filter(
        # USAMOS EL NUEVO CAMPO 'iestado' para filtrar por activo
        iestado=1 
    ).order_by('marca') # USAMOS EL NUEVO CAMPO 'marca' para ordenar
    
    # Precargar si hay datos en sesión
    initial_data = request.session.get('vehiculo_data', {})
    
    context = {
        'marcas': marcas,
        'initial_data': initial_data,
    }
    return render(request, 'vehiculos/vehiculo.html', context)


@login_required
def documentos_fisica_view(request):
    """Subir documentos personales y de vehículo para persona física"""
    from catalogo.models import TipoDocumento
    
    solicitud_actual = Solicitud.objects.filter(usuario=request.user, estado='borrador', tipo_persona='fisica').first()
    if not solicitud_actual or 'vehiculo_data' not in request.session:
        messages.warning(request, 'Primero debes completar los datos del vehículo')
        return redirect('vehiculos:vehiculo')
    
    # El flujo de documentos_fisica debe llevar a documentos_vehiculo o finalizar si ya es el último paso.
    # Dado que el flujo anterior redirige a 'documentos_vehiculo', esta vista solo maneja los personales.
    if request.method == 'POST':
        request.session['documentos_fisica_completado'] = True
        messages.success(request, 'Documentos personales guardados temporalmente')
        return redirect('vehiculos:documentos_vehiculo') # Siguiente paso
    
    tipos_documentos = TipoDocumento.objects.filter(
        categoria='personal',
        activo=True
    ).order_by('nombre')
    
    # Obtener documentos temporales ya subidos
    documentos_temp = request.session.get('documentos_temporales', {})
    
    context = {
        'tipos_documentos': tipos_documentos,
        # Se filtran los documentos ya subidos para la categoría 'personal'
        'documentos_subidos': {k: v for k, v in documentos_temp.items() if v['categoria'] == 'personal'},
        'categoria_actual': 'personal', # Para usar en la API de subida
    }
    return render(request, 'vehiculos/documentos_fisica.html', context)

@login_required
def documentos_moral_view(request):
    """Subir documentos de empresa y representante legal para persona moral"""
    from catalogo.models import TipoDocumento
    
    solicitud_actual = Solicitud.objects.filter(usuario=request.user, estado='borrador', tipo_persona='moral').first()
    if not solicitud_actual or 'representante_data' not in request.session:
        messages.warning(request, 'Primero debes completar los datos del representante legal')
        return redirect('vehiculos:representante_legal')
    
    if request.method == 'POST':
        request.session['documentos_moral_completado'] = True
        messages.success(request, 'Documentos de persona moral guardados temporalmente')
        return redirect('vehiculos:documentos_vehiculo') # Siguiente paso
    
    tipos_documentos_empresa = TipoDocumento.objects.filter(
        categoria='moral',
        activo=True
    ).order_by('nombre')
    
    tipos_documentos_representante = TipoDocumento.objects.filter(
        categoria='representante',
        activo=True
    ).order_by('nombre')
    
    documentos_temp = request.session.get('documentos_temporales', {})
    
    context = {
        'tipos_documentos_empresa': tipos_documentos_empresa,
        'tipos_documentos_representante': tipos_documentos_representante,
        'documentos_subidos': documentos_temp, # Muestra todos los subidos
    }
    return render(request, 'vehiculos/documentos_moral.html', context)


@login_required
def documentos_vehiculo_view(request):
    """Subir documentos del vehículo"""
    from catalogo.models import TipoDocumento
    
    solicitud_actual = Solicitud.objects.filter(usuario=request.user, estado='borrador').first()
    if not solicitud_actual:
        messages.warning(request, 'No se encontró una solicitud activa. Inicie el proceso.')
        return redirect('vehiculos:titulo')
        
    if request.method == 'POST':
        request.session['documentos_vehiculo_completado'] = True
        messages.success(request, 'Documentos del vehículo guardados temporalmente')
        return redirect('vehiculos:finalizar')
    
    tipos_documentos = TipoDocumento.objects.filter(
        categoria='vehiculo',
        activo=True
    ).order_by('nombre')
    
    # Obtener documentos temporales ya subidos
    documentos_temp = request.session.get('documentos_temporales', {})
    
    context = {
        'tipos_documentos': tipos_documentos,
        # Se filtran los documentos ya subidos para la categoría 'vehiculo'
        'documentos_subidos': {k: v for k, v in documentos_temp.items() if v['categoria'] == 'vehiculo'},
        'categoria_actual': 'vehiculo', # Para usar en la API de subida
    }
    return render(request, 'vehiculos/documentos_vehiculo.html', context)


@login_required
def finalizar_view(request):
    """
    Vista de finalización que guarda todos los datos de sesión en la base de datos
    y actualiza la solicitud de 'borrador' a 'enviada'.
    """
    from django.utils import timezone
    from django.db import transaction
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    
    # 1. Buscar la solicitud existente en borrador
    solicitud_actual = Solicitud.objects.filter(usuario=request.user, estado='borrador').first()
    
    if not solicitud_actual:
        messages.error(request, 'No se encontró una solicitud en proceso. Por favor, inicie el proceso nuevamente.')
        return redirect('vehiculos:dashboard')
    
    if solicitud_actual.estado != 'borrador':
         # Evitar el doble envío
        messages.warning(request, f'La solicitud {solicitud_actual.folio} ya fue enviada.')
        context = {
            'folio': solicitud_actual.folio,
            'fecha': solicitud_actual.fecha_envio if solicitud_actual.fecha_envio else solicitud_actual.creado,
        }
        return render(request, 'vehiculos/final.html', context)
    
    # 2. Iniciar transacción atómica
    try:
        with transaction.atomic():
            
            # --- Actualizar Solicitud a 'enviada' ---
            solicitud_actual.estado = 'enviada'
            solicitud_actual.fecha_envio = timezone.now()
            solicitud_actual.save() # Guarda el cambio de estado
            
            solicitud = solicitud_actual # Alias para claridad
            tipo_persona = solicitud.tipo_persona
            
            # --- 3. Crear objetos relacionados ---
            
            # A. Persona Física / Moral
            if tipo_persona == 'fisica':
                # Intentar obtener o crear PersonaFisica
                persona_data = request.session.get('persona_fisica_data', {})
                PersonaFisica.objects.update_or_create(
                    solicitud=solicitud,
                    defaults={
                        'nombre': persona_data.get('nombre', ''),
                        'primer_apellido': persona_data.get('primer_apellido', ''),
                        'segundo_apellido': persona_data.get('segundo_apellido', ''),
                        'rfc': persona_data.get('rfc', ''),
                        'regimen_fiscal': persona_data.get('regimen_fiscal', ''),
                        'sexo': persona_data.get('sexo', 'H'),
                        'fecha_nacimiento': persona_data.get('fecha_nacimiento'),
                        'telefono_fijo': persona_data.get('telefono_fijo', ''),
                        'telefono_movil': persona_data.get('telefono_movil', ''),
                    }
                )
                
                # Intentar obtener o crear Domicilio titular
                domicilio_data = request.session.get('domicilio_data', {})
                Domicilio.objects.update_or_create(
                    solicitud=solicitud,
                    tipo='titular', # Clave para identificar el domicilio
                    defaults={
                        'codigo_postal': domicilio_data.get('codigo_postal', ''),
                        'estado': domicilio_data.get('estado', ''), 
                        'municipio': domicilio_data.get('municipio', ''),
                        'colonia': domicilio_data.get('colonia', ''),
                        'calle': domicilio_data.get('calle', ''),
                    }
                )
                
            elif tipo_persona == 'moral':
                # Intentar obtener o crear PersonaMoral
                moral_data = request.session.get('persona_moral_data', {})
                persona_moral, created_moral = PersonaMoral.objects.update_or_create(
                    solicitud=solicitud,
                    defaults={
                        'razon_social': moral_data.get('razon_social', ''),
                        'rfc': moral_data.get('rfc', ''),
                        'regimen_fiscal': moral_data.get('regimen_fiscal', ''),
                    }
                )
                
                # Intentar obtener o crear Domicilio fiscal
                domicilio_data = request.session.get('domicilio_moral_data', {})
                Domicilio.objects.update_or_create(
                    solicitud=solicitud,
                    tipo='fiscal', # Clave para identificar el domicilio
                    defaults={
                        'codigo_postal': domicilio_data.get('codigo_postal', ''),
                        'estado': domicilio_data.get('estado', ''),
                        'municipio': domicilio_data.get('municipio', ''),
                        'colonia': domicilio_data.get('colonia', ''),
                        'calle': domicilio_data.get('calle', ''),
                    }
                )
                
                # Intentar obtener o crear RepresentanteLegal
                representante_data = request.session.get('representante_data', {})
                RepresentanteLegal.objects.update_or_create(
                    persona_moral=persona_moral,
                    defaults={
                        'nombre': representante_data.get('nombre', ''),
                        'primer_apellido': representante_data.get('primer_apellido', ''),
                        'segundo_apellido': representante_data.get('segundo_apellido', ''),
                        'rfc': representante_data.get('rfc', ''),
                        'regimen_fiscal': representante_data.get('regimen_fiscal', ''),
                        'sexo': representante_data.get('sexo', 'H'),
                        'fecha_nacimiento': representante_data.get('fecha_nacimiento'),
                        'telefono_fijo': representante_data.get('telefono_fijo', ''),
                        'telefono_movil': representante_data.get('telefono_movil', ''),
                    }
                )
            
            # B. Vehiculo
            vehiculo_data = request.session.get('vehiculo_data', {})
            if vehiculo_data:
                marca = MarcaVehiculo.objects.get(id=vehiculo_data.get('marca'))
                tipo_vehiculo = TipoVehiculo.objects.get(id=vehiculo_data.get('tipo'))
                
                Vehiculo.objects.update_or_create(
                    solicitud=solicitud,
                    defaults={
                        'marca': marca,
                        'tipo': tipo_vehiculo,
                    }
                )
            
            # C. Documentos
            documentos_temp = request.session.get('documentos_temporales', {})
            if documentos_temp:
                # 1. Eliminar documentos viejos asociados a la solicitud antes de guardar los nuevos
                Documento.objects.filter(solicitud=solicitud).delete()
                
                for doc_key, doc_data in documentos_temp.items():
                    try:
                        tipo_doc = TipoDocumento.objects.get(id=doc_data['tipo_documento_id'])
                        
                        temp_path = doc_data.get('path')
                        if temp_path and default_storage.exists(temp_path):
                            with default_storage.open(temp_path, 'rb') as f:
                                contenido = f.read()
                            
                            # Nuevo path permanente usando el folio de la Solicitud
                            nuevo_path = f'documentos/{solicitud.folio}/{doc_data["nombre_unico"]}'
                            final_path = default_storage.save(nuevo_path, ContentFile(contenido))
                            
                            Documento.objects.create(
                                solicitud=solicitud,
                                tipo_documento=tipo_doc,
                                archivo=final_path,
                                nombre_original=doc_data['nombre_archivo'],
                                tamano=doc_data['tamanio']
                            )
                            
                            # Eliminar archivo temporal después de moverlo
                            default_storage.delete(temp_path)
                            
                    except Exception as e:
                        # Loggear el error de un solo documento y continuar
                        print(f"Error al guardar documento {doc_key}: {e}")
            
            # Enviar email (Descomenta y ajusta si la función existe)
            # try:
            #     from accounts.emails import enviar_email_solicitud_recibida
            #     enviar_email_solicitud_recibida(request.user, solicitud)
            # except Exception as email_error:
            #     print(f"Error al enviar email: {email_error}")
            
            # --- Limpiar sesión ---
            keys_to_delete = [
                'titulo_data', 'persona_fisica_data', 'persona_moral_data',
                'domicilio_data', 'domicilio_moral_data', 'representante_data',
                'vehiculo_data', 'documentos_fisica_completado',
                'documentos_vehiculo_completado', 'documentos_temporales',
                'documentos_moral_completado' # Añadida para moral
            ]
            for key in keys_to_delete:
                if key in request.session:
                    del request.session[key]
            
            messages.success(request, f'¡Solicitud registrada exitosamente! Tu folio es: {solicitud.folio}')
            
            context = {
                'folio': solicitud.folio,
                'fecha': solicitud.fecha_envio,
            }
            return render(request, 'vehiculos/final.html', context)
            
    except Exception as e:
        # Manejo de error si falla la transacción
        print(f"FATAL ERROR en finalizar_view: {e}")
        messages.error(request, f'Error al guardar la solicitud. Por favor, reintente: {str(e)}')
        return redirect('vehiculos:dashboard')


# API para subir documentos
@login_required
@require_POST
def subir_documento(request):
    """Vista para subir documentos vía AJAX (sin cambios)"""
    try:
        tipo_documento_id = request.POST.get('tipo_documento_id')
        categoria = request.POST.get('categoria', 'personal')
        archivo = request.FILES.get('archivo')
        
        if not archivo or not tipo_documento_id:
            return JsonResponse({
                'success': False,
                'error': 'Faltan datos requeridos'
            }, status=400)
        
        # Validaciones
        if archivo.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'El archivo no debe superar los 5MB'
            }, status=400)
        
        tipos_permitidos = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
        if archivo.content_type not in tipos_permitidos:
            return JsonResponse({
                'success': False,
                'error': 'Solo se permiten archivos PDF, JPG o PNG'
            }, status=400)
        
        # Re-importar para asegurar que está disponible
        from catalogo.models import TipoDocumento
        tipo_documento = TipoDocumento.objects.get(id=tipo_documento_id)
        
        # Guardar temporalmente
        documentos_temp = request.session.get('documentos_temporales', {})
        
        # Usar la clave compuesta para asegurar unicidad por tipo
        doc_key = f"{categoria}_{tipo_documento_id}"
        
        ext = os.path.splitext(archivo.name)[1]
        nombre_unico = f"{tipo_documento_id}_{request.user.id}_{timezone.now().timestamp():.0f}{ext}"
        
        
        documentos_temp[doc_key] = {
            'tipo_documento_id': tipo_documento_id,
            'tipo_documento_nombre': tipo_documento.nombre,
            'nombre_archivo': archivo.name,
            'nombre_unico': nombre_unico,
            'tamanio': archivo.size,
            'content_type': archivo.content_type,
            'categoria': categoria,
            # El path temporal se añadirá después
        }
        
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        path = default_storage.save(
            f'temp_documentos/{request.user.id}/{nombre_unico}',
            ContentFile(archivo.read())
        )
        
        documentos_temp[doc_key]['path'] = path
        request.session['documentos_temporales'] = documentos_temp
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Documento "{tipo_documento.nombre}" guardado correctamente',
            'documento': {
                'nombre': archivo.name,
                'tamanio': archivo.size,
                'tipo': tipo_documento.nombre
            }
        })
        
    except TipoDocumento.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Tipo de documento no encontrado.'
        }, status=404)
        
    except Exception as e:
        print(f"Error al subir documento: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error al subir el archivo: {str(e)}'
        }, status=500)


# API para tipos de vehículo
def obtener_tipos_vehiculo(request):
    """API para obtener tipos de vehículo según la marca (sin cambios)"""
    from catalogo.models import TipoVehiculo
    
    marca_id = request.GET.get('marca_id')
    
    if not marca_id:
        return JsonResponse({'error': 'Falta el parámetro marca_id'}, status=400)
    
    try:
        tipos = TipoVehiculo.objects.filter(
            marca_id=marca_id,
            activo=True
        ).values('id', 'nombre').order_by('nombre')
        
        return JsonResponse({
            'success': True,
            'tipos': list(tipos)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)