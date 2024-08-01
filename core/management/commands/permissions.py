from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group

class Command(BaseCommand):
    help = 'Sembrar permisos a la base de datos'

    def handle(self, *args, **options):  
        self.seed_admin_permissions()
        self.seed_volunteer_permissions()
        self.seed_user_permissions()
        
    def seed_admin_permissions(self):
        admin_group = Group.objects.get(name='Administrador')

        all_permissions = Permission.objects.all()

        admin_group.permissions.add(*all_permissions)

    def seed_volunteer_permissions(self):
        volunteer_group = Group.objects.get(name='Voluntario')

        permissions_codenames = [
            # Añade aquí los codenames de los permisos que deseas asignar al grupo Voluntario
        ]

        permissions = Permission.objects.filter(codename__in=permissions_codenames)

        volunteer_group.permissions.add(*permissions)
    
    def seed_user_permissions(self):
        user_group = Group.objects.get(name='Usuario Normal')

        permissions_codenames = [
            # Añade aquí los codenames de los permisos que deseas asignar al grupo Usuario Normal
        ]

        permissions = Permission.objects.filter(codename__in=permissions_codenames)

        user_group.permissions.add(*permissions)
