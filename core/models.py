from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    maternal_surname = models.CharField(max_length=30, blank=True, null=True)
    identification = models.CharField(max_length=13, blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    GENRE_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    genre = models.CharField(
        max_length=1, choices=GENRE_CHOICES, blank=False, null=False)

    def __str__(self):
        return self.username


class Speciality(models.Model):
    name = models.CharField(max_length=80)
    description = models.TextField()
    detailed_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'

    def __str__(self):
        return self.name


class Doctor(User):
    specialities = models.ManyToManyField(Speciality)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_doctors')

    class Meta:
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctores'

    def __str__(self):
        return f'{self.username} - {", ".join([speciality.name for speciality in self.specialities.all()])}'


class Appointment(models.Model):
    patient = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(
        'Doctor', on_delete=models.CASCADE, related_name='doctor_appointments')
    speciality = models.ForeignKey(
        'Speciality', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()

    # Campos adicionales
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pendiente'),
            ('CONFIRMED', 'Confirmada'),
            ('CANCELLED', 'Cancelada'),
            ('ATTENDED', 'Atendida'),
            ('NO_SHOW', 'No asistió'),
        ],
        default='CONFIRMED'
    )

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'

    def __str__(self):
        return f'{self.patient.first_name} {self.patient.last_name} - {self.appointment_date} - {self.appointment_time}'

    def clean(self):
        # Obtener la fecha y hora actuales en la zona horaria local
        current_datetime = timezone.localtime()
        current_date = current_datetime.date()
        current_time = current_datetime.time()

        # Validación para evitar duplicados a nivel de modelo, considerando solo citas confirmadas
        if self.status == 'CONFIRMED' and Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date=self.appointment_date,
            appointment_time=self.appointment_time,
            status='CONFIRMED'  # Solo se consideran las citas confirmadas
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                f'Este doctor ya tiene una cita confirmada en esta hora y fecha'
            )

        # Validación para que la fecha de la cita no sea en el pasado
        if self.appointment_date < current_date:
            raise ValidationError(
                'La fecha de la cita no puede ser en el pasado.')

        # Validación para que la hora de la cita para el mismo día no sea anterior a la hora actual.
        if self.appointment_date == current_date and self.appointment_time < current_time:
            raise ValidationError(
                'La hora de la cita no puede ser en el pasado.')

        # Validación para máximo dos citas con diferentes médicos en el mismo día
        if self.status == 'CONFIRMED':
            same_day_appointments = Appointment.objects.filter(
                patient=self.patient,
                appointment_date=self.appointment_date,
                status='CONFIRMED'
            ).exclude(pk=self.pk).values('doctor').distinct()
            if len(same_day_appointments) >= 2:
                raise ValidationError(
                    'No puedes reservar más de dos citas con diferentes médicos en el mismo día.'
                )

        # Validación para evitar citas duplicadas en la misma fecha y hora para el mismo paciente
        if self.status == 'CONFIRMED' and Appointment.objects.filter(
            patient=self.patient,
            appointment_date=self.appointment_date,
            appointment_time=self.appointment_time,
            status='CONFIRMED'
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                'Ya tienes una cita en este horario y fecha. Por favor, elige otro horario.'
            )

    def save(self, *args, **kwargs):
        # Llamada a full_clean para realizar todas las validaciones (incluyendo clean)
        self.full_clean()
        super().save(*args, **kwargs)


class MedicalHistory(models.Model):
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='medical_histories')
    doctor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='diagnosed_histories'
    )
    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name='medical_histories', null=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_histories')
    diagnosis = models.TextField()
    treatment = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVE', 'Activo'),
            ('ARCHIVED', 'Archivado'),
            ('PENDING', 'Pendiente'),
        ],
        default='ACTIVE'
    )

    def __str__(self):
        return f'Historial Médico de {self.patient.username} - {self.created_at.strftime("%Y-%m-%d")}'


class Prescription(models.Model):
    medical_history = models.ForeignKey(
        MedicalHistory, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='issued_prescriptions')
    issued_at = models.DateTimeField(default=timezone.now, editable=False)
    medication_details = models.TextField(
        help_text="Detalles del medicamento: nombre, gramos, tabletas, etc.")
    instructions = models.TextField(
        help_text="Indicaciones: cómo y cuándo tomar el medicamento.")
    pdf_file = models.FileField(
        upload_to='prescriptions/', blank=True, null=True)

    class Meta:
        verbose_name = 'Receta Médica'
        verbose_name_plural = 'Recetas Médicas'

    def __str__(self):
        return f'Receta de {self.doctor.username} para {self.patient.username} - {self.issued_at.strftime("%Y-%m-%d")}'


class ActionLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    module = models.CharField(max_length=100)
    functionality = models.CharField(max_length=100)
    action = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.user} - {self.module} - {self.action} - {self.timestamp}'
