from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib import messages

from core.models import Appointment, Doctor, Speciality, User
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import Group
from core.utils import is_admin, is_allowed_to_schedule, is_patient, is_receptionist


# Renderiza el template que contiene el formulario para agendar un cita
@login_required
@user_passes_test(is_allowed_to_schedule)
def schedule_appointment(request):
    specialties = Speciality.objects.all()
    doctors = Doctor.objects.all()

    # Verificar que el grupo 'Paciente' exista y obtener la lista de pacientes
    try:
        group_patient = Group.objects.get(name='Paciente')
        patients = User.objects.filter(groups=group_patient)
    except Group.DoesNotExist:
        patients = User.objects.none()  # Ningún paciente si el grupo no existe

    return render(request, 'shared/schedule_appointment.html', {
        'specialties': specialties,
        'doctors': doctors,
        'patients': patients,
    })


# Vista para guardar la cita
@login_required
def book_appointment(request):
    if request.method == 'POST':
        user = request.user

        # Validar los roles del usuario
        if is_patient(user):
            patient = user
        elif is_admin(user) or is_receptionist(user):
            patient_id = request.POST.get('patient_id')
            if not patient_id:
                messages.error(request, 'Debes seleccionar un paciente.')
                return redirect('schedule_appointment')
            patient = get_object_or_404(User, id=patient_id)
        else:
            messages.error(request, 'No tienes permisos para agendar citas.')
            return redirect('schedule_appointment')

        # Obtener datos del formulario
        doctor_id = request.POST.get('doctor_id')
        speciality_id = request.POST.get('speciality_id')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')

        # Validar campos requeridos
        if not all([doctor_id, speciality_id, appointment_date, appointment_time, reason]):
            messages.error(
                request, 'Por favor, completa todos los campos antes de enviar.')
            return redirect('schedule_appointment')

        # Obtener doctor y especialidad
        doctor = get_object_or_404(Doctor, id=doctor_id)
        speciality = get_object_or_404(Speciality, id=speciality_id)

        # Validar la regla de negocio (máximo 2 citas por día con diferentes médicos)
        existing_appointments = Appointment.objects.filter(
            patient=patient,
            appointment_date=appointment_date,
            status='CONFIRMED'
        ).values('doctor').distinct()

        if len(existing_appointments) >= 2:
            messages.error(
                request, 'No puedes reservar más de dos citas con diferentes médicos en el mismo día.')
            return redirect('schedule_appointment')

        try:
            # Crear la cita
            appointment = Appointment(
                patient=patient,
                doctor=doctor,
                speciality=speciality,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason=reason,
            )
            appointment.full_clean()  # Validar el modelo
            appointment.save()

            messages.success(request, 'La cita fue agendada exitosamente.')
            return redirect('schedule_appointment')

        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
        except Exception as e:
            messages.error(request, f'Ocurrió un error al crear la cita: {e}')

        return redirect('schedule_appointment')

    return render(request, 'schedule_appointment.html')


# Vista para renderizar el formulario de edición de una cita
@login_required
def edit_appointment_view(request, appointment_id):
    # Obtener la cita seleccionada
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Obtener especialidades y doctores
    specialties = Speciality.objects.all()
    doctors = Doctor.objects.all()

    # Contexto para renderizar el formulario
    context = {
        "appointment": appointment,  # Datos básicos de la cita
        "specialties": specialties,  # Lista de especialidades
        "doctors": doctors,          # Lista de doctores
    }

    return render(request, "shared/edit_appointment.html", context)


# Vista para guardar los datos de la cita editada
@login_required
def edit_appointment(request, appointment_id):
    # Obtener la cita existente
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Verificar permisos de edición
    if not (is_admin(request.user) or is_receptionist(request.user) or
            (is_patient(request.user) and appointment.patient == request.user)):
        messages.error(request, 'No tienes permiso para editar esta cita.')
        return redirect('future_appointments')

    if request.method == 'POST':
        # Obtener datos del formulario
        doctor_id = request.POST.get('doctor_id')
        speciality_id = request.POST.get('speciality_id')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')

        # Validar que todos los campos estén completos
        if not all([doctor_id, speciality_id, appointment_date, appointment_time, reason]):
            messages.error(
                request, 'Por favor, complete todos los campos requeridos.')
            return redirect('edit_appointment_view', appointment_id=appointment_id)

        # Validar disponibilidad del doctor
        if Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='CONFIRMED'
        ).exclude(pk=appointment.id).exists():
            messages.error(
                request, 'El doctor ya tiene una cita en este horario.')
            return redirect('edit_appointment_view', appointment_id=appointment_id)

        # Validar límite de citas por día del paciente
        same_day_appointments = Appointment.objects.filter(
            patient=appointment.patient,
            appointment_date=appointment_date,
            status='CONFIRMED'
        ).exclude(pk=appointment.id).values('doctor').distinct()

        if len(same_day_appointments) >= 2:
            messages.error(
                request, 'No puedes tener más de dos citas con diferentes médicos en el mismo día.')
            return redirect('edit_appointment_view', appointment_id=appointment_id)

        # Actualizar la cita con los datos validados
        appointment.doctor_id = doctor_id
        appointment.speciality_id = speciality_id
        appointment.appointment_date = appointment_date
        appointment.appointment_time = appointment_time
        appointment.reason = reason

        try:
            # Validar y guardar los cambios
            appointment.full_clean()  # Validación a nivel de modelo
            appointment.save()

            messages.success(request, 'La cita se actualizó correctamente.')
            return redirect('next_appointments')

        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)

        except Exception:
            messages.error(
                request, 'Ocurrió un error al editar la cita. Por favor, inténtelo de nuevo.')

    # Manejar solicitudes GET para precargar los datos del formulario
    context = {'appointment': appointment}
    return render(request, 'shared/edit_appointment.html', context)


@login_required
@user_passes_test(is_allowed_to_schedule)
def next_appointments(request):
    try:
        group_patient = Group.objects.get(name='Paciente')
        patients = User.objects.filter(groups=group_patient)
    except Group.DoesNotExist:
        patients = User.objects.none()
    return render(request, 'shared/next_appointments.html', {'patients': patients})


@login_required
@user_passes_test(is_allowed_to_schedule)
def appointment_history(request):
    try:
        group_patient = Group.objects.get(name='Paciente')
        patients = User.objects.filter(groups=group_patient)
    except Group.DoesNotExist:
        patients = User.objects.none()
    return render(request, 'shared/appointment_history.html', {'patients': patients})


# Vista que devuelve los detalles de la cita
@login_required
def appointment_details(request, appointment_id):
    # Obtener la cita o devolver 404 si no existe
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Verificar si la solicitud incluye un parámetro para diferenciar entre los detalles del historial y las próximas citas
    is_history = request.GET.get('is_history', 'false').lower() == 'true'

    # Seleccionar el template adecuado
    template = 'shared/appointment_history_details.html' if is_history else 'shared/appointment_details.html'

    # Renderizar los detalles en el template correspondiente
    return render(request, template, {'appointment': appointment})


# Vista para cancelar la cita
@login_required
def cancel_appointment(request, appointment_id):
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Verificar si el usuario tiene permiso para cancelar la cita
        if (
            appointment.patient == request.user or
            is_admin(request.user) or
            is_receptionist(request.user)
        ):
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
def load_appointment_history(request):
    if request.method == 'GET':
        try:
            user = request.user
            patient_id = request.GET.get('patient_id')

            # Verificar roles y establecer el paciente
            if is_patient(user):
                # Si el usuario es paciente, solo puede ver sus propias citas
                patient = user
            elif is_admin(user) or is_receptionist(user):
                # Si es administrador o secretaria, pueden ver las citas de otros pacientes
                if not patient_id:
                    return JsonResponse({
                        "message": "Success",
                        "appointments": []
                    })
                try:
                    patient = User.objects.get(
                        id=patient_id, groups__name='Paciente')
                except User.DoesNotExist:
                    return JsonResponse({"message": "Paciente no encontrado"}, status=404)
            else:
                return JsonResponse({"message": "No autorizado"}, status=403)

            # Obtener las citas del paciente
            current_datetime = timezone.localtime()
            appointments = Appointment.objects.filter(
                patient=patient
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
            ).select_related('doctor', 'speciality')

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

        except Exception as e:
            return JsonResponse({"message": f"Error inesperado: {str(e)}"}, status=500)

    return JsonResponse({"message": "Método no permitido"}, status=405)


# Vista para devolver las citas futuras del paciente
@login_required
def future_appointments(request):
    try:
        user = request.user
        patient_id = request.GET.get('patient_id')
        current_time = timezone.localtime()

        if is_admin(user) or is_receptionist(user):
            # Administradores o secretarias con un paciente seleccionado
            if patient_id:
                appointments = Appointment.objects.filter(
                    patient_id=patient_id,
                    status__in=['PENDING', 'CONFIRMED']
                ).filter(
                    Q(appointment_date__gt=current_time.date()) |
                    Q(appointment_date=current_time.date(),
                      appointment_time__gt=current_time.time())
                ).select_related('doctor').order_by('appointment_date', 'appointment_time')
            else:
                appointments = []  # No se proporcionó un paciente
        elif is_patient(user):
            # Paciente viendo sus propias citas
            appointments = Appointment.objects.filter(
                patient=user,
                status__in=['PENDING', 'CONFIRMED']
            ).filter(
                Q(appointment_date__gt=current_time.date()) |
                Q(appointment_date=current_time.date(),
                  appointment_time__gt=current_time.time())
            ).select_related('doctor').order_by('appointment_date', 'appointment_time')
        else:
            appointments = []  # Rol no permitido para ver citas

    except ObjectDoesNotExist as e:
        messages.error(
            request, "Hubo un error al obtener las citas. Intenta de nuevo más tarde.")
        appointments = []

    except Exception as e:
        messages.error(request, f"Error inesperado: {str(e)}")
        appointments = []

    if request.htmx:
        return render(request, 'shared/appointments_table.html', {'appointments': appointments})

    return render(request, 'shared/next_appointments.html', {'appointments': appointments})
