# Generated by Django 5.0.6 on 2024-09-19 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_appointment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicalhistory',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Activo'), ('ARCHIVED', 'Archivado'), ('PENDING', 'Pendiente')], default='ACTIVE', max_length=20),
        ),
    ]
