from django.contrib import admin
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','name','username', 'biography', 'email', 'phone_number', 'birthdate', 'country')
    
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id','name','abbreviation', 'dialing_code', 'iso')