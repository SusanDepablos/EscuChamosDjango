from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=Reaction)
def hacer_algo_despues_de_guardar(sender, instance, created, **kwargs):
    if created:
        print(f"Instancia creada: {instance}")
        for field in instance._meta.fields:
            field_name = field.name
            field_value = getattr(instance, field_name)
            print(f"{field_name}: {field_value}")
