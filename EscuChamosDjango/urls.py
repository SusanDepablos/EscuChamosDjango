from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import index, error  # Asegúrate de importar tu vista aquí

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('api/', include('core.api_urls.urls')),
    path('', index, name='index'), 
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'core.views.error'