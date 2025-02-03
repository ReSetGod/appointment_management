import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from core.forms import MedicalHistoryForm
from core.models import MedicalHistory, User
from core.utils import is_allowed_to_review_histories, is_doctor, is_patient, is_receptionist
from django.contrib.auth.models import Group


@login_required
@user_passes_test(is_allowed_to_review_histories)
def medical_history(request):
    try:
        group_patient = Group.objects.get(name='Paciente')
        patients = User.objects.filter(groups=group_patient)
    except Group.DoesNotExist:
        patients = User.objects.none()
    return render(request, 'shared/medical_history.html', {'patients': patients})


# Vista para devolver el historial de los diagnósticos
@login_required
def diagnostics_history(request):
    if request.method == 'GET':
        try:
            user = request.user

            # Obtener el ID del paciente si se proporciona en los parámetros de la solicitud
            patient_id = request.GET.get('patient_id')

            # Caso: Usuario es Paciente
            if is_patient(user):
                diagnostics = MedicalHistory.objects.filter(
                    patient=user
                ).select_related('doctor')

            # Caso: Usuario es Administrador, Secretaria o Doctor
            elif is_receptionist(user) or is_doctor(user):
                if not patient_id:
                    return JsonResponse({
                        "message": "Success",
                        "diagnostics": []
                    })

                diagnostics = MedicalHistory.objects.filter(
                    patient_id=patient_id
                ).select_related('doctor')

            else:
                return JsonResponse({"message": "No autorizado"}, status=403)

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

        return render(request, 'shared/diagnostic_details.html', context)
    except MedicalHistory.DoesNotExist:
        return JsonResponse({"message": "Diagnóstico no encontrado"}, status=404)


@login_required
def load_medical_histories(request):
    if request.method == 'GET':
        try:
            user = request.user

            # Verificar que el usuario sea un doctor
            if not user.groups.filter(name='Doctor').exists():
                return JsonResponse({"message": "No autorizado"}, status=403)

            # Obtener los historiales médicos relacionados con el doctor
            medical_histories = MedicalHistory.objects.filter(doctor=user)

            # Formatear los datos en JSON
            histories_data = []
            for history in medical_histories:
                histories_data.append({
                    "id": history.id,
                    "patient": history.patient.get_full_name(),
                    "diagnosis": history.diagnosis,
                    "treatment": history.treatment,
                    "created_at": history.created_at.strftime('%Y-%m-%d %H:%M'),
                    "status": history.get_status_display(),
                })

            return JsonResponse({"message": "Success", "medical_histories": histories_data})

        except Exception as e:
            return JsonResponse({"message": f"Error inesperado: {str(e)}"}, status=500)

    return JsonResponse({"message": "Método no permitido"}, status=405)


@login_required
def create_or_edit_medical_history(request, medical_history_id=None):
    is_editing = medical_history_id is not None
    medical_history = None

    # Si se está editando, obtenemos el historial médico, o lanzamos 404 si no existe.
    if is_editing:
        medical_history = get_object_or_404(
            MedicalHistory, pk=medical_history_id)

    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST, instance=medical_history)
        if form.is_valid():
            try:
                medical_history = form.save(commit=False)
                # Asignar automáticamente el doctor como el usuario actual
                if not is_editing:  # Solo asignar al crear, no al editar
                    medical_history.doctor = request.user

                # Campo para rastrear quién modificó.
                medical_history.modified_by = request.user
                medical_history.save()
                messages.success(
                    request, 'Historial médico guardado con éxito.' if not is_editing else 'Historial médico actualizado con éxito.'
                )
                return redirect('manage_diagnosis')

            except Exception as e:
                messages.error(
                    request, f'Error al guardar el historial médico: {str(e)}')
        else:
            # Manejo detallado de errores
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request, f"{form.fields[field].label}: {error}")

    else:
        form = MedicalHistoryForm(instance=medical_history)

    return render(request, 'doctor/create_or_edit_diagnosis.html', {
        'form': form,
        'is_editing': is_editing
    })


@login_required
def delete_medical_history(request):
    if request.method == 'POST':
        try:
            # Obtenemos el JSON del cuerpo de la solicitud
            body = json.loads(request.body)
            medical_history_id = body.get('medical_history_id')

            if not medical_history_id:
                return JsonResponse({'message': 'ID de historial médico no proporcionado.'}, status=400)

            # Verificamos que el historial médico existe
            medical_history = get_object_or_404(
                MedicalHistory, id=medical_history_id)

            # Eliminamos el historial médico
            medical_history.delete()

            return JsonResponse({'message': 'Diagnóstico eliminado exitosamente.'}, status=200)
        except Exception as e:
            return JsonResponse({'message': f'Error al eliminar el historial médico: {str(e)}'}, status=500)
    else:
        return JsonResponse({'message': 'Método no permitido.'}, status=405)


@login_required
@user_passes_test(is_doctor)
def manage_diagnosis(request):
    return render(request, 'doctor/manage_medical_histories.html')
