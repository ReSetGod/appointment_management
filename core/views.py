from datetime import datetime, time
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import *

# Creando las funciones que verifican el rol del usuario


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


@login_required
def home(request):
    return render(request, 'home.html')


# Vistas del rol paciente

@login_required
@user_passes_test(is_patient)
def search_doctors(request):
    return render(request, 'patient/search_doctors.html')


@login_required
@user_passes_test(is_patient)
def schedule_appointment_patient(request):
    specialties = Speciality.objects.all()
    doctors = Doctor.objects.all()

    return render(request, 'patient/schedule_appointment.html', {
        'specialties': specialties,
        'doctors': doctors,
    })


@login_required
@user_passes_test(is_patient)
def my_appointment(request):
    return render(request, 'patient/my_appointment.html')


@login_required
@user_passes_test(is_patient)
def appointment_history_patient(request):
    return render(request, 'patient/appointment_history.html')


@login_required
@user_passes_test(is_patient)
def medical_history_patient(request):
    return render(request, 'patient/medical_history.html')


# Vistas del rol Administrador

@login_required
@user_passes_test(is_admin)
def specialties_doctors(request):
    return render(request, 'administrator/specialties_doctors.html')


@login_required
@user_passes_test(is_admin)
def schedule_appointment_admin(request):
    return render(request, 'administrator/schedule_appointment.html')


@login_required
@user_passes_test(is_admin)
def appointment_history_admin(request):
    return render(request, 'administrator/appointment_history.html')


@login_required
@user_passes_test(is_admin)
def medical_history_admin(request):
    return render(request, 'administrator/medical_history.html')


# Configuración
@login_required
def configuration(request):
    return render(request, 'configuration.html')


# Vista para obtener los horarios disponibles
@login_required
def get_available_times(request, doctor_id, date):
    try:
        # Convertir la fecha de string a objeto date
        appointment_date = datetime.strptime(date, "%Y-%m-%d").date()

        # Definir los turnos de la mañana y la tarde con intervalos de 30 minutos
        morning_shift = [time(9, 0), time(9, 30), time(10, 0), time(
            10, 30), time(11, 0), time(11, 30), time(12, 0)]
        afternoon_shift = [time(16, 0), time(16, 30), time(
            17, 0), time(17, 30), time(18, 0)]

        # Combinar ambos turnos
        all_shifts = morning_shift + afternoon_shift

        # Obtener la hora actual en la zona horaria local
        current_datetime = timezone.localtime()

        # Validar si la fecha seleccionada es hoy
        if appointment_date == current_datetime.date():
            # Si la fecha es hoy, eliminar horarios que ya han pasado
            current_time = current_datetime.time()

            # Filtrar los turnos que son pasados
            all_shifts = [
                shift for shift in all_shifts if shift > current_time]

        # Obtener las citas del doctor en la fecha seleccionada
        appointments = Appointment.objects.filter(
            doctor_id=doctor_id, appointment_date=appointment_date)

        # Obtener los horarios ocupados
        occupied_times = [
            appointment.appointment_time for appointment in appointments]

        # Filtrar los horarios disponibles
        available_times = [shift.strftime(
            "%H:%M") for shift in all_shifts if shift not in occupied_times]

        # Retornar los horarios disponibles
        if available_times:
            data = {'message': 'Success', 'available_times': available_times}
        else:
            data = {'message': 'No Available Times'}
    except Exception as e:
        data = {'message': f'Error: {str(e)}'}

    return JsonResponse(data)


# Vista para obtener los nombres de las especialidades
@login_required
def get_specialities(request):
    specialities = list(Speciality.objects.values('id', 'name'))

    if (len(specialities) > 0):
        data = {'message': "Success", 'specialities': specialities}
    else:
        data = {'message': "Not Found"}

    return JsonResponse(data)


# Vista para obtener los doctores filtrados por especialidad
@login_required
def get_doctors_by_specialty(request, specialty_id):
    doctors = list(Doctor.objects.filter(
        specialities__id=specialty_id).values('id', 'first_name', 'last_name'))

    if (len(doctors) > 0):
        data = {'message': "Success", 'doctors': doctors}
    else:
        data = {'message': "Not Found"}

    return JsonResponse(data)


# Vista para guardar la cita
@login_required
def book_appointment(request):
    if request.method == 'POST':
        # Verificar el rol del usuario
        user = request.user
        is_paciente = user.groups.filter(name='Paciente').exists()
        is_administrador = user.groups.filter(name='Administrador').exists()
        is_secretaria = user.groups.filter(name='Secretaria').exists()

        doctor_id = request.POST.get('doctor_id')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')

        # Validaciones manuales de los campos
        if not all([doctor_id, appointment_date, appointment_time, reason]):
            messages.error(
                request, 'Por favor, completa todos los campos antes de enviar.')
            return redirect('schedule_appointment_patient')

        doctor = get_object_or_404(Doctor, id=doctor_id)

        # Asignar el paciente basado en el rol
        if is_paciente:
            patient = user
        elif is_administrador or is_secretaria:
            patient_id = request.POST.get('patient_id')
            patient = get_object_or_404(User, id=patient_id)
        else:
            messages.error(request, 'No tiene permisos para agendar citas.')
            return redirect('schedule_appointment_patient')

        try:
            # Crear la cita
            appointment = Appointment(
                patient=patient,
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason=reason,
            )
            # Validar y guardar la cita
            appointment.full_clean()  # Aquí se validan los campos del modelo
            appointment.save()

            messages.success(request, 'La cita fue agendada exitosamente.')
            return redirect('schedule_appointment_patient')

        except ValidationError as e:
            # Mostrar errores específicos de validación
            for error in e.messages:
                messages.error(request, error)
            return redirect('schedule_appointment_patient')

        except Exception as e:
            # Manejo de errores generales
            messages.error(
                request, 'Ocurrió un error al crear la cita. Inténtalo de nuevo.')
            return redirect('schedule_appointment_patient')

    return render(request, 'schedule_appointment.html')
