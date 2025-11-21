from django.shortcuts import render

def index(request):
    """Vista principal - Landing page"""
    return render(request, 'core/index.html')