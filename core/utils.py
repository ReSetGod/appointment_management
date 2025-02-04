import random
import string
import os
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML

import os
from django.conf import settings

from appointment_management import settings

# Funciones para verificar roles de usuario


def is_patient(user):
    return user.groups.filter(name='Paciente').exists()


def is_admin(user):
    return user.groups.filter(name='Administrador').exists()


def is_doctor(user):
    return user.groups.filter(name='Doctor').exists()


def is_receptionist(user):
    return user.groups.filter(name='Secretaria').exists()


def is_manager(user):
    return user.groups.filter(name='Gerencia').exists()


def is_allowed_to_schedule(user):
    return (
        is_patient(user) or
        is_receptionist(user)
    )


def is_allowed_to_review_histories(user):
    return (
        is_patient(user) or
        is_receptionist(user) or
        is_doctor(user)
    )


def is_allowed_to_create_reports(user):
    return (
        is_admin(user) or
        is_manager(user)
    )


# Función para generar contraseñas aleatorias
def generate_password(length=8):
    characters = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(random.choices(characters, k=length))


# Función para obtener el nombre completo del doctor
def get_doctor_name(doctor):
    return f"{doctor.first_name} {doctor.middle_name or ''} {doctor.last_name} {doctor.maternal_surname or ''}".strip()


# Función para obtener el nombre completo del paciente
def get_patient_name(patient):
    return f"{patient.first_name} {patient.middle_name or ''} {patient.last_name} {patient.maternal_surname or ''}".strip()


# Función para la generación de PDFs
def generate_pdf(template_src, context):
    try:
        # Add STATIC_ROOT to context
        context['STATIC_ROOT'] = os.path.join(
            settings.BASE_DIR, 'core/static').replace('\\', '/')

        # Render template with context
        html = render_to_string(template_src, context)

        # Use absolute file path for base_url
        static_path = os.path.join(settings.BASE_DIR, 'core', 'static')
        base_url = f"file:///{static_path.replace(os.sep, '/')}"

        try:
            pdf = HTML(
                string=html,
                base_url=base_url,
                encoding='utf-8'
            ).write_pdf(
                presentational_hints=True
            )
            return pdf
        except Exception as pdf_error:
            raise
    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")


def get_category_from_score(score):
    if score == 0:
        return ('Normal', 'success')
    elif score == 1:
        return ('Alerta Moderada', 'warning')
    elif score == 3:
        return ('Alerta Severa', 'orange')
    else:
        return ('Crítico', 'danger')


def get_total_category(total_score):
    if 0 <= total_score <= 4:
        return ('No urgente', 'success')
    elif 5 <= total_score <= 9:
        return ('Urgente', 'warning')
    elif 10 <= total_score <= 14:
        return ('Muy urgente', 'orange')
    else:
        return ('Emergencia', 'danger')
