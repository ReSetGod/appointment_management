from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),

    # Rutas para Pacientes
    path('patient/search_doctors/', views.search_doctors,
         name='search_doctors_patient'),

    # Rutas compartidas para todos los roles
    path('schedule_appointment/', views.schedule_appointment,
         name='schedule_appointment'),
    path('next_appointments', views.next_appointments,
         name='next_appointments'),
    path('appointment_history/', views.appointment_history,
         name='appointment_history'),
    path('medical_history/', views.medical_history,
         name='medical_history'),

    # Rutas para Administradores
    path('administrator/manage_doctors/',
         views.manage_doctors, name='manage_doctors'),
    path('administrator/manage_specialities/',
         views.manage_specialities, name='manage_specialities'),

    # Rutas para Secretatias
    path('receptionist/register_patients/',
         views.register_patients, name='register_patients'),

    # Configuración
    path('shared/configuration/', views.configuration, name='configuration'),

    # Rutas adicionales
    path('doctors/<int:specialty_id>',
         views.get_doctors_by_specialty, name='get_doctors_by_specialty'),
    path('specialities/',
         views.get_specialities, name='get_specialities'),
    path('available_times/<int:doctor_id>/<str:date>/',
         views.get_available_times, name='get_available_times'),
    path('book_appointment/', views.book_appointment, name='book_appointment'),
    path('future_appointments/', views.future_appointments,
         name='future_appointments'),
    path('appointment/<int:appointment_id>/details/',
         views.appointment_details, name='appointment_details'),
    path('appointment/<int:appointment_id>/cancel/',
         views.cancel_appointment, name='cancel_appointment'),
    path('load_appointment_history/', views.load_appointment_history,
         name='load_appointment_history'),
    path('diagnostics-history/', views.diagnostics_history,
         name='diagnostics_history'),
    path('diagnostic/<int:diagnostic_id>/details/',
         views.diagnostic_details, name='diagnostic_details'),
    path('specialities/<int:speciality_id>/',
         views.speciality_detail, name='speciality_detail'),
    path('email/', views.render_email_page, name='render_email_page'),
    path('email/update/', views.update_email_view, name='update_email_view'),
    path('search_patients/', views.search_patients, name='search_patients'),
    path('load_doctors/', views.load_doctors, name='load_doctors'),
    path('load_specialities/', views.load_specialities, name='load_specialities'),

    # Eliminar usuarios
    path('users/delete/', views.delete_user, name='delete_user'),
    path('delete_doctor/', views.delete_doctor, name='delete_doctor'),

    # Crear y editar doctor
    path('create-doctor/', views.create_or_edit_doctor, name='create_doctor'),
    path('edit_doctor/<int:doctor_id>/',
         views.create_or_edit_doctor, name='edit_doctor'),

    # Crear y editar especialidad
    path('create-speciality/', views.create_or_edit_speciality,
         name='create-speciality'),
    path('edit_speciality/<int:speciality_id>/',
         views.create_or_edit_speciality, name='edit_speciality'),

    # Eliminar especialidad
    path('delete_speciality/', views.delete_speciality, name='delete_speciality'),


    # Vistas para editar las citas
    path("appointments/edit/<int:appointment_id>/",
         views.edit_appointment_view, name="edit_appointment_view"),
    path("appointments/edit/<int:appointment_id>/save/",
         views.edit_appointment, name="edit_appointment"),
]
