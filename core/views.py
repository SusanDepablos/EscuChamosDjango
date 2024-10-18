from django.shortcuts import render

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


