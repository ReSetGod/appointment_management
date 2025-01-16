# utils.py
import random
import string

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
        is_admin(user) or
        is_receptionist(user)
    )


# Función para generar contraseñas aleatorias
def generate_password(length=8):
    characters = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(random.choices(characters, k=length))


# Función para obtener el nombre completo del doctor
def get_doctor_name(doctor):
    return f"{doctor.first_name} {doctor.middle_name or ''} {doctor.last_name} {doctor.maternal_surname or ''}".strip()
