from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render

from core.models import MedicalHistory, User
from core.utils import is_admin, is_allowed_to_schedule, is_patient, is_receptionist
from django.contrib.auth.models import Group


@login_required
@user_passes_test(is_allowed_to_schedule)
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

            # Caso: Usuario es Administrador o Secretaria
            elif is_admin(user) or is_receptionist(user):
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
