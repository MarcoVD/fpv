from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.conf import settings

def enviar_email_activacion(user, perfil):
    """Enviar email de activación de cuenta"""
    
    subject = 'Activa tu cuenta - Renovación Vehicular'
    
    # URL de activación
    url_activacion = f"{settings.SITE_URL}/accounts/activar/{perfil.token_activacion}/"
    
    # Contexto para el template
    context = {
        'user': user,
        'token': perfil.token_activacion,
        'url_activacion': url_activacion,
        'site_url': settings.SITE_URL,
    }
    
    # Renderizar template HTML
    html_message = render_to_string('accounts/emails/activacion.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False


def enviar_email_bienvenida(user):
    """Enviar email de bienvenida después de activar cuenta"""
    
    subject = '¡Bienvenido! - Renovación Vehicular'
    
    context = {
        'user': user,
        'site_url': settings.SITE_URL,
    }
    
    html_message = render_to_string('accounts/emails/bienvenida.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False


def enviar_email_solicitud_recibida(user, solicitud):
    """Enviar email de confirmación de solicitud recibida"""
    
    subject = f'Solicitud Recibida - Folio {solicitud.folio}'
    
    context = {
        'user': user,
        'solicitud': solicitud,
        'site_url': settings.SITE_URL,
    }
    
    html_message = render_to_string('vehiculos/emails/solicitud_recibida.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False


def enviar_email_cambio_estado(user, solicitud):
    """Enviar email cuando cambia el estado de la solicitud"""
    
    estados_texto = {
        'borrador': 'en borrador',
        'enviada': 'enviada y en proceso de revisión',
        'revision': 'en revisión',
        'aprobada': '¡APROBADA!',
        'rechazada': 'rechazada',
    }
    
    estado_texto = estados_texto.get(solicitud.estado, solicitud.estado)
    subject = f'Actualización de Solicitud - Folio {solicitud.folio}'
    
    context = {
        'user': user,
        'solicitud': solicitud,
        'estado_texto': estado_texto,
        'site_url': settings.SITE_URL,
    }
    
    html_message = render_to_string('vehiculos/emails/cambio_estado.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False