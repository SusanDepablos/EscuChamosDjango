# Generated by Django 5.0.7 on 2024-08-07 22:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Borrado')),
                ('body', models.TextField(blank=True, null=True, verbose_name='Cuerpo')),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reposts', to='core.post', verbose_name='Publicación Padre')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='post', to='core.status', verbose_name='Estado')),
                ('type_post', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='posts', to='core.typepost', verbose_name='Tipo de Publicación')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Publicación',
                'verbose_name_plural': 'Publicaciones',
                'db_table': 'posts',
            },
        ),
    ]
