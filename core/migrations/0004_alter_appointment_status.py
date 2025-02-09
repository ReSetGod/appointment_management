# Generated by Django 5.0.6 on 2024-09-19 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_doctor_options_alter_speciality_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pendiente'), ('CONFIRMED', 'Confirmada'), ('CANCELLED', 'Cancelada')], default='CONFIRMED', max_length=20),
        ),
    ]
