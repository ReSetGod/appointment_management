from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render

from core.models import Doctor, Speciality
from core.utils import is_patient, is_receptionist


@login_required
@user_passes_test(is_patient)
def search_doctors(request):
    return render(request, 'patient/search_doctors.html')


@login_required
def speciality_detail(request, speciality_id):
    # Obtener la especialidad específica
    speciality = get_object_or_404(Speciality, id=speciality_id)

    # Filtrar los doctores que tienen esta especialidad
    doctors = Doctor.objects.filter(specialities=speciality)

    return render(request, 'patient/speciality_detail.html', {
        'speciality': speciality,
        'doctors': doctors,
    })


# Vista para rol Secretaria
@login_required
@user_passes_test(is_receptionist)
def register_patients(request):
    return render(request, 'receptionist/register_patients.html')
