from django.shortcuts import render
from .models import Post, Group, User  # Asegúrate de que este es el nombre correcto del modelo
from .serializer import PostSerializer  # Importa el serializador correcto
from datetime import datetime
from babel.dates import format_datetime

def index(request):
    return render(request, 'index.html')

def error(request, exception=None):
    return render(request, 'error.html', status=404)