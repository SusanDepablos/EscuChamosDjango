from django.shortcuts import render
from .models import Post, Group, User  # Asegúrate de que este es el nombre correcto del modelo
from .serializer import PostSerializer  # Importa el serializador correcto
from datetime import datetime
from babel.dates import format_datetime

def index(request):
    return render(request, 'index.html')

def verify(request):
    return render(request, 'verify_email.html', {
            'username': 'valentina',
            'verification_code': 555555,
            'user_email': "valentina@gmail.com"
        })
    
def error(request, exception=None):
    return render(request, 'error.html', status=404)