from .auth_views import render_email_page, update_email_view, delete_user
from .patient_views import manage_patients, create_or_edit_patient, delete_patient, load_patients
from .doctor_views import (manage_doctors, create_or_edit_doctor,
                           delete_doctor, load_doctors, get_doctors_by_specialty, search_doctors)
from .speciality_views import (
    manage_specialities, create_or_edit_speciality, delete_speciality, load_specialities, get_specialities, speciality_detail
)
from .appointment_views import (
    schedule_appointment, book_appointment, edit_appointment_view, edit_appointment, cancel_appointment, appointment_details, future_appointments, load_appointment_history, appointment_history, next_appointments
)
from .shared_views import home, configuration, get_available_times, search_patients

from .diagnostics_views import diagnostics_history, diagnostic_details, medical_history
