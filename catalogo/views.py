
from django.shortcuts import render
from django.http import JsonResponse

# Vista de ejemplo para catálogos (opcional)
def municipios_json(request):
    """API JSON para obtener municipios"""
    municipios = [
        {'id': 1, 'nombre': 'Chalco'},
        {'id': 2, 'nombre': 'Ixtapaluca'},
        # ... más municipios
    ]
    return JsonResponse({'municipios': municipios})