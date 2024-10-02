from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),

    # Rutas para Pacientes
    path('patient/search_doctors/', views.search_doctors,
         name='search_doctors_patient'),
    path('patient/schedule_appointment/', views.schedule_appointment_patient,
         name='schedule_appointment_patient'),
    path('patient/my_appointment/', views.my_appointment,
         name='my_appointment'),
    path('patient/appointment_history/', views.appointment_history_patient,
         name='appointment_history_patient'),
    path('patient/medical_history/', views.medical_history_patient,
         name='medical_history_patient'),

    # Rutas para Administradores
    path('administrator/schedule_appointment/',
         views.schedule_appointment_admin, name='schedule_appointment_admin'),
    path('administrator/appointment_history/',
         views.appointment_history_admin, name='appointment_history_admin'),
    path('administrator/medical_history/',
         views.medical_history_admin, name='medical_history_admin'),
    path('administrator/specialties_doctors/',
         views.specialties_doctors, name='specialties_doctors_admin'),

    # Configuración
    path('configuration/', views.configuration, name='configuration'),

    # Rutas adicionales
    path('doctors/<int:specialty_id>',
         views.get_doctors_by_specialty, name='get_doctors_by_specialty'),
    path('specialities/',
         views.get_specialities, name='get_specialities'),
    path('available_times/<int:doctor_id>/<str:date>/',
         views.get_available_times, name='get_available_times'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
]
