from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def error(request, exception):
    return render(request, 'error.html', status=404)