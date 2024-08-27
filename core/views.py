from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def error(request):
    return render(request, 'error.html')