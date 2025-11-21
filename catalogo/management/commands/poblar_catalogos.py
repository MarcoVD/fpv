# catalogo/management/commands/poblar_catalogos.py
from django.core.management.base import BaseCommand
from catalogo.models import Municipio, MarcaVehiculo, TipoVehiculo, TipoDocumento

class Command(BaseCommand):
    help = 'Poblar catálogos iniciales'

    def handle(self, *args, **kwargs):
        self.stdout.write('Poblando catálogos...')
        
        # Municipios
        municipios = [
            ('Chalco', 'CHA'),
            ('Ixtapaluca', 'IXT'),
            ('Nezahualcóyotl', 'NEZ'),
            ('Ecatepec de Morelos', 'ECA'),
            ('Toluca', 'TOL'),
        ]
        for nombre, clave in municipios:
            Municipio.objects.get_or_create(nombre=nombre, clave=clave)
        
        # Marcas de vehículos
        marcas_data = ['MG', 'JAC', 'BYD', 'NISSAN', 'RENAULT', 'CHANGAN']
        for marca in marcas_data:
            MarcaVehiculo.objects.get_or_create(nombre=marca)
        
        # Tipos de vehículos
        tipos_data = {
            'MG': ['3 HYBRID'],
            'JAC': ['E 10 X', 'E30X'],
            'BYD': ['KING DM 1', 'DOLPHIN MINI'],
            'NISSAN': ['KICKS PLAY E-POWER'],
            'RENAULT': ['KWID E-TECH'],
            'CHANGAN': ['PLUS IDD', 'CS55'],
        }
        
        for marca_nombre, tipos in tipos_data.items():
            marca = MarcaVehiculo.objects.get(nombre=marca_nombre)
            for tipo in tipos:
                TipoVehiculo.objects.get_or_create(marca=marca, nombre=tipo)
        
        # Tipos de documentos
        documentos = [
            ('Identificación oficial', 'personal', True),
            ('CURP', 'personal', True),
            ('RFC', 'personal', True),
            ('Comprobante de domicilio', 'personal', True),
            ('Título de concesión', 'personal', True),
            ('Licencia de conducir', 'personal', True),
            ('Factura y/o endoso', 'vehiculo', True),
            ('Tarjeta de circulación', 'vehiculo', True),
            ('Pago de Tenencias', 'vehiculo', True),
            ('Póliza de seguro', 'vehiculo', True),
        ]
        
        for nombre, categoria, obligatorio in documentos:
            TipoDocumento.objects.get_or_create(
                nombre=nombre,
                defaults={'categoria': categoria, 'obligatorio': obligatorio}
            )
        
        self.stdout.write(self.style.SUCCESS('Catálogos poblados exitosamente'))