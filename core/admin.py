from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.forms import CustomUserChangeForm, CustomUserCreationForm
from .models import Speciality, Doctor, User, Appointment, MedicalHistory, Prescription


class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        'username', 'email', 'first_name', 'middle_name', 'last_name', 'maternal_surname',
        'identification', 'address', 'city', 'phone_number', 'birth_date', 'genre', 'is_staff', 'get_groups'
    )

    search_fields = ('username', 'email', 'first_name',
                     'last_name', 'identification')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'genre')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Grupos'

    fieldsets = (
        ('Información personal', {
            'fields': ('username', 'email', 'password', 'first_name', 'middle_name', 'last_name', 'maternal_surname', 'identification', 'birth_date', 'genre')
        }),
        ('Información de contacto', {
            'fields': ('address', 'city', 'phone_number')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        ('Información personal', {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                ('first_name', 'middle_name'), ('last_name', 'maternal_surname'),
                'identification', 'birth_date',
                'genre',
            )
        }),
        ('Información de contacto', {
            'fields': ('address', 'city', 'phone_number')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'patient',
        'doctor',
        'speciality',
        'appointment_date',
        'appointment_time',
        'status',
    )
    search_fields = ('patient__username', 'doctor__username', 'status')
    list_filter = ('status', 'appointment_date', 'doctor')


# Clase personalizada para MedicalHistory en el admin
@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'created_at',
                    'status')  # Campos visibles en la lista
    # Filtros para facilitar búsqueda
    list_filter = ('status', 'created_at', 'doctor')
    search_fields = ('patient__username', 'doctor__username',
                     'diagnosis')  # Campos de búsqueda
    readonly_fields = ('created_at', 'modified_at')  # Campos de solo lectura

    # Configuración de los campos visibles en el formulario de edición
    fields = (
        'patient', 'doctor', 'diagnosis', 'treatment', 'status',
        'created_at', 'modified_at', 'modified_by', 'appointment'
    )

    # Opcional: personalizar el nombre de las columnas en la lista
    def patient_name(self, obj):
        return obj.patient.first_name
    patient_name.short_description = 'Paciente'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'medical_history', 'doctor', 'issued_at')
    list_filter = ('issued_at', 'doctor')
    search_fields = ('medical_history__patient__username',
                     'doctor__username', 'medication_details')
    readonly_fields = ('issued_at',)


# Registra el modelo User con la administración personalizada
admin.site.register(User, CustomUserAdmin)
admin.site.register(Speciality)
admin.site.register(Doctor)
