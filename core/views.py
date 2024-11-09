from datetime import datetime, time
from django.db.models import Q
from django.db import IntegrityError
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ValidationError, ObjectDoesNotExist
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
def my_appointments(request):
    return render(request, 'patient/my_appointments.html')


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
            doctor_id=doctor_id, appointment_date=appointment_date, status='CONFIRMED')

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
        speciality_id = request.POST.get('speciality_id')  # Nuevo campo
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')

        # Validaciones manuales de los campos
        if not all([doctor_id, speciality_id, appointment_date, appointment_time, reason]):
            messages.error(
                request, 'Por favor, completa todos los campos antes de enviar.')
            return redirect('schedule_appointment_patient')

        doctor = get_object_or_404(Doctor, id=doctor_id)
        # Obtener la especialidad seleccionada
        speciality = get_object_or_404(Speciality, id=speciality_id)

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
            # Crear la cita con la especialidad incluida
            appointment = Appointment(
                patient=patient,
                doctor=doctor,
                speciality=speciality,  # Asignar la especialidad
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


# Vista para devolver las citas futuras del paciente
@login_required
def future_appointments(request):
    try:
        user = request.user
        # Verificar si el usuario pertenece al grupo 'Paciente'
        if request.user.groups.filter(name='Paciente').exists():
            # Obtener la fecha y hora actuales en la zona horaria local
            current_time = timezone.localtime()

            # Obtener las citas futuras del paciente, excluyendo citas pasadas y canceladas
            appointments = Appointment.objects.filter(
                patient=user,
                status__in=['PENDING', 'CONFIRMED']  # Excluir las canceladas
            ).filter(
                # Citas a partir de mañana
                Q(appointment_date__gt=current_time.date()) |
                # Citas del día de hoy pero con hora futura
                Q(appointment_date=current_time.date(),
                  appointment_time__gt=current_time.time())
            ).select_related('doctor').order_by('appointment_date', 'appointment_time')

        else:
            appointments = []

    except ObjectDoesNotExist as e:
        messages.error(
            request, "Hubo un error al obtener las citas. Intenta de nuevo más tarde.")
        appointments = []

    except Exception as e:
        # Manejar cualquier otro error inesperado
        messages.error(request, f"Error inesperado: {str(e)}")
        appointments = []

    if request.htmx:
        # Si es una solicitud htmx, solo devuelve el fragmento de la tabla
        return render(request, 'patient/appointments_table.html', {'appointments': appointments})

    return render(request, 'patient/future_appointments.html', {'appointments': appointments})


# Vista que devuelve los detalles de la cita
@login_required
def appointment_details(request, appointment_id):
    # Obtener la cita o devolver 404 si no existe
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Verificar si la solicitud incluye un parámetro para diferenciar entre los detalles del historial y las próximas citas
    is_history = request.GET.get('is_history', 'false').lower() == 'true'

    # Seleccionar el template adecuado
    template = 'patient/appointment_history_details.html' if is_history else 'patient/appointment_details.html'

    # Renderizar los detalles en el template correspondiente
    return render(request, template, {'appointment': appointment})


# Vista para cancelar la cita
def cancel_appointment(request, appointment_id):
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if appointment.patient == request.user:
            appointment.status = 'CANCELLED'
            appointment.save()

            # Preparar la respuesta con un mensaje de éxito
            response_data = {
                "message": "La cita ha sido cancelada con éxito.",
                "appointment_id": appointment_id,
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({"message": "No tienes permiso para cancelar esta cita."}, status=403)

    except Exception as e:
        return JsonResponse({"message": f"Ocurrió un error: {str(e)}"}, status=500)


# Vista para devolver el historial de citas del paciente
@login_required
def appointment_history(request):
    if request.method == 'GET':
        try:
            user = request.user

            # Verificar si el usuario pertenece al grupo 'Paciente'
            if request.user.groups.filter(name='Paciente').exists():
                current_datetime = timezone.localtime()

                # Filtrar citas pasadas para status CONFIRMED o ATTENDED
                appointments = Appointment.objects.filter(
                    patient=user
                ).filter(
                    models.Q(status__in=['CANCELLED', 'NO_SHOW']) |
                    models.Q(
                        status__in=['CONFIRMED', 'ATTENDED'],
                        appointment_date__lt=current_datetime.date()
                    ) |
                    models.Q(
                        status__in=['CONFIRMED', 'ATTENDED'],
                        appointment_date=current_datetime.date(),
                        appointment_time__lte=current_datetime.time()
                    )
                ).select_related('doctor')

                # Transformar las citas a JSON
                appointments_data = []
                for appointment in appointments:
                    appointments_data.append({
                        "id": appointment.id,
                        "date": appointment.appointment_date.strftime('%Y-%m-%d'),
                        "time": appointment.appointment_time.strftime('%H:%M'),
                        "doctor": f"{appointment.doctor.first_name} {appointment.doctor.last_name}",
                        "speciality": appointment.speciality.name if appointment.speciality else "Sin especialidad",
                        "status": appointment.get_status_display(),
                    })

                return JsonResponse({"message": "Success", "appointments": appointments_data})
            else:
                return JsonResponse({"message": "No autorizado"}, status=403)

        except Exception as e:
            return JsonResponse({"message": f"Error inesperado: {str(e)}"}, status=500)

    return JsonResponse({"message": "Método no permitido"}, status=405)


# Vista para devolver el historial de los diagnósticos
@login_required
def diagnostics_history(request):
    if request.method == 'GET':
        try:
            user = request.user

            # Verificar si el usuario pertenece al grupo 'Paciente'
            if request.user.groups.filter(name='Paciente').exists():
                diagnostics = MedicalHistory.objects.filter(
                    patient=user).select_related('doctor')

                # Transformar los diagnósticos a JSON
                diagnostics_data = []
                for diagnostic in diagnostics:
                    diagnostics_data.append({
                        "id": diagnostic.id,
                        "created_at": diagnostic.created_at.strftime('%Y-%m-%d'),
                        "diagnosis": diagnostic.diagnosis,
                        "doctor": f"{diagnostic.doctor.first_name} {diagnostic.doctor.last_name}"
                    })

                return JsonResponse({"message": "Success", "diagnostics": diagnostics_data})
            else:
                return JsonResponse({"message": "No autorizado"}, status=403)

        except Exception as e:
            return JsonResponse({"message": f"Error inesperado: {str(e)}"}, status=500)

    return JsonResponse({"message": "Método no permitido"}, status=405)


# Vista para mostrar los detalles de un diagnóstico
@login_required
def diagnostic_details(request, diagnostic_id):
    try:
        diagnostic = MedicalHistory.objects.select_related(
            'doctor').get(id=diagnostic_id)

        context = {
            'medical_history': diagnostic,
            'appointment_id': diagnostic.appointment.id
        }

        return render(request, 'patient/diagnostic_details.html', context)
    except MedicalHistory.DoesNotExist:
        return JsonResponse({"message": "Diagnóstico no encontrado"}, status=404)
