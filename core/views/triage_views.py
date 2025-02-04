import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from core.forms import SpecialityForm, TriageForm
from core.models import Appointment, Doctor, Speciality, Triage, User
from core.utils import get_category_from_score, get_total_category, is_admin, is_doctor, is_receptionist


@login_required
@user_passes_test(is_doctor)
def manage_triages(request):
    return render(request, 'doctor/manage_triages.html')


@login_required
@user_passes_test(is_doctor)
def create_or_edit_triage(request, triage_id=None):
    is_editing = triage_id is not None
    triage = None

    if is_editing:
        triage = get_object_or_404(Triage, pk=triage_id)

    if request.method == 'POST':
        form = TriageForm(request.POST, instance=triage)
        if form.is_valid():
            try:
                triage = form.save()
                messages.success(request, 'Triaje guardado exitosamente.')
                return redirect('manage_triages')
            except Exception as e:
                messages.error(
                    request, f'Error al guardar el triaje: {str(e)}')
    else:
        form = TriageForm(instance=triage)

    return render(request, 'doctor/create_or_edit_triage.html', {
        'form': form,
        'is_editing': is_editing
    })


@login_required
@user_passes_test(is_doctor)
def load_triages(request):
    if request.method == 'GET':
        try:
            triages = Triage.objects.select_related('patient').all()
            triages_data = []

            if not triages.exists():
                return JsonResponse({
                    "message": "Success",
                    "triages": []
                })

            for triage in triages:
                triages_data.append({
                    "id": triage.id,
                    "patient_name": f"{triage.patient.get_full_name()} ({triage.patient.identification})",
                    "heart_rate": triage.heart_rate,
                    "respiratory_rate": triage.respiratory_rate,
                    "systolic_blood_pressure": triage.systolic_blood_pressure,
                    "oxygen_saturation": triage.oxygen_saturation,
                    "total_score": triage.total_score,
                    "category": triage.get_category_display(),
                    "created_at": triage.created_at.strftime('%Y-%m-%d %H:%M'),
                })

            return JsonResponse({"message": "Success", "triages": triages_data})
        except Exception as e:
            print(f"Error en load_triages: {str(e)}")  # Debug log
            return JsonResponse({
                "message": "Success",
                "triages": []
            })

    return JsonResponse({"message": "Método no permitido"}, status=405)


@login_required
@user_passes_test(is_doctor)
def triage_details(request, triage_id):
    triage = get_object_or_404(Triage, pk=triage_id)

    vitals_data = [
        {
            'parameter': 'Frecuencia Cardíaca',
            'value': triage.heart_rate,
            'score': triage.heart_rate_score,
            'category': get_category_from_score(triage.heart_rate_score)
        },
        {
            'parameter': 'Frecuencia Respiratoria',
            'value': triage.respiratory_rate,
            'score': triage.respiratory_rate_score,
            'category': get_category_from_score(triage.respiratory_rate_score)
        },
        {
            'parameter': 'Presión Arterial Sistólica',
            'value': triage.systolic_blood_pressure,
            'score': triage.blood_pressure_score,
            'category': get_category_from_score(triage.blood_pressure_score)
        },
        {
            'parameter': 'Saturación de Oxígeno',
            'value': f"{triage.oxygen_saturation}%",
            'score': triage.oxygen_saturation_score,
            'category': get_category_from_score(triage.oxygen_saturation_score)
        },
        {
            'parameter': 'Nivel de Conciencia',
            'value': triage.get_consciousness_level_display(),
            'score': triage.consciousness_score,
            'category': get_category_from_score(triage.consciousness_score)
        }
    ]

    total_category = get_total_category(triage.total_score)

    return render(request, 'doctor/triage_details.html', {
        'triage': triage,
        'vitals_data': vitals_data,
        'total_category': total_category
    })
