from allauth.account.forms import SignupForm
from allauth.account.models import EmailAddress
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group
from .models import Doctor, MedicalHistory, Prescription, Rating, Speciality, User


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='Nombre', widget=forms.TextInput(
        attrs={'class': 'input100', 'placeholder': 'Primer nombre'}))
    last_name = forms.CharField(max_length=30, label='Apellido', widget=forms.TextInput(
        attrs={'class': 'input100', 'placeholder': 'Primer apellido'}))
    middle_name = forms.CharField(max_length=30, label='Segundo nombre', widget=forms.TextInput(
        attrs={'class': 'input100', 'placeholder': 'Segundo nombre'}))
    maternal_surname = forms.CharField(max_length=30, label='Segundo apellido', widget=forms.TextInput(
        attrs={'class': 'input100', 'placeholder': 'Segundo apellido'}))
    identification = forms.CharField(max_length=13, label='Identificación', widget=forms.TextInput(
        attrs={'class': 'input100', 'placeholder': 'Número de Ruc o cédula'}))
    address = forms.CharField(max_length=50, label='Dirección', widget=forms.TextInput(
        attrs={'class': 'input100', 'placeholder': 'Lugar de residencia'}))
    city = forms.CharField(max_length=15, label='Ciudad de residencia',
                           widget=forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Ej. Quito'}))
    phone_number = forms.CharField(max_length=10, label='Celular', widget=forms.TextInput(
        attrs={'class': 'input100', 'placeholder': 'Tu número de teléfono'}))
    birth_date = forms.DateField(
        label='Fecha de nacimiento', required=False, widget=forms.DateInput(attrs={'class': 'input100', 'type': 'date'}))
    GENRE_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    genre = forms.ChoiceField(choices=GENRE_CHOICES,
                              label='Género', widget=forms.RadioSelect(attrs={'class': 'input100'}))

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.middle_name = self.cleaned_data['middle_name']
        user.maternal_surname = self.cleaned_data['maternal_surname']
        user.identification = self.cleaned_data['identification']
        user.address = self.cleaned_data['address']
        user.city = self.cleaned_data['city']
        user.phone_number = self.cleaned_data['phone_number']
        user.birth_date = self.cleaned_data['birth_date']
        user.genre = self.cleaned_data['genre']
        user.save()

        # Asigna el grupo "Paciente"
        patient_group = Group.objects.get(name='Paciente')
        user.groups.add(patient_group)

        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username", "first_name", "last_name", "middle_name",
            "maternal_surname", "identification", "address", "city",
            "phone_number", "birth_date", "genre"
        ]
        labels = {
            "username": "Nombre de usuario",
            "first_name": "Primer nombre",
            "last_name": "Primer apellido",
            "middle_name": "Segundo nombre",
            "maternal_surname": "Segundo apellido",
            "identification": "Identificación",
            "address": "Dirección",
            "city": "Ciudad de residencia",
            "phone_number": "Número de celular",
            "birth_date": "Fecha de nacimiento",
            "genre": "Género",
        }
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "middle_name": forms.TextInput(attrs={"class": "form-control"}),
            "maternal_surname": forms.TextInput(attrs={"class": "form-control"}),
            "identification": forms.TextInput(attrs={
                "class": "form-control",
                "maxlength": "13",
                "minlength": "10",
                "pattern": "[0-9]+",
                "title": "Debe contener entre 10 y 13 números"
            }),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={
                "class": "form-control",
                "maxlength": "10",
                "minlength": "10",
                "pattern": "[0-9]+",
                "title": "Debe contener exactamente 10 números"
            }),
            "birth_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d"
            ),
            "genre": forms.Select(attrs={"class": "form-select"}, choices=[
                ('M', 'Masculino'),
                ('F', 'Femenino'),
            ]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurarse de que la fecha siga el formato correcto
        if self.instance and self.instance.birth_date:
            self.initial["birth_date"] = self.instance.birth_date.strftime(
                "%Y-%m-%d")


class CustomEmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu nuevo correo electrónico'
        }),
        label="Nuevo Correo Electrónico",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verifica si el correo ya está asociado a este usuario
        if EmailAddress.objects.filter(user=self.user, email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            'username', 'first_name', 'middle_name', 'last_name', 'maternal_surname',
            'email', 'identification', 'address', 'city', 'phone_number',
            'birth_date', 'genre', 'specialities'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'maternal_surname': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'identification': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '13',
            }),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '10',
            }),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'specialities': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Primer nombre',
            'middle_name': 'Segundo nombre',
            'last_name': 'Primer apellido',
            'maternal_surname': 'Segundo apellido',
            'email': 'Correo electrónico',
            'identification': 'Identificación',
            'address': 'Dirección',
            'city': 'Ciudad',
            'phone_number': 'Teléfono',
            'birth_date': 'Fecha de nacimiento',
            'genre': 'Género',
            'specialities': 'Especialidades',
        }

    def clean_identification(self):
        identification = self.cleaned_data.get('identification')
        if not identification.isdigit():
            raise forms.ValidationError(
                "La identificación solo debe contener números.")
        if len(identification) > 13:
            raise forms.ValidationError(
                "La identificación no puede exceder los 13 caracteres.")
        return identification

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError(
                "El teléfono solo debe contener números.")
        if len(phone_number) > 10:
            raise forms.ValidationError(
                "El teléfono no puede exceder los 10 caracteres.")
        return phone_number


class SpecialityForm(forms.ModelForm):
    STATUS_CHOICES = (
        ('True', 'Activo'),
        ('False', 'Inactivo'),
    )

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.RadioSelect,
        label="Estado"
    )

    class Meta:
        model = Speciality
        fields = [
            'name', 'description', 'detailed_description', 'status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción breve',
                'rows': 3  # Cambiar tamaño del textarea
            }),
            'detailed_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción detallada (opcional)',
                'rows': 4  # Cambiar tamaño del textarea
            }),
        }
        labels = {
            'name': 'Nombre de la especialidad',
            'description': 'Descripción',
            'detailed_description': 'Descripción detallada',
            'status': 'Estado',
        }

    def save(self, commit=True):
        """Convierte el valor del estado a booleano antes de guardar."""
        instance = super().save(commit=False)
        instance.status = self.cleaned_data['status'] == 'True'
        if commit:
            instance.save()
        return instance


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'middle_name', 'last_name', 'maternal_surname',
            'email', 'identification', 'address', 'city', 'phone_number',
            'birth_date', 'genre'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'maternal_surname': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'identification': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '13',
            }),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '10',
            }),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Primer nombre',
            'middle_name': 'Segundo nombre',
            'last_name': 'Primer apellido',
            'maternal_surname': 'Segundo apellido',
            'email': 'Correo electrónico',
            'identification': 'Identificación',
            'address': 'Dirección',
            'city': 'Ciudad',
            'phone_number': 'Teléfono',
            'birth_date': 'Fecha de nacimiento',
            'genre': 'Género'
        }

    def clean_identification(self):
        identification = self.cleaned_data.get('identification')
        if not identification.isdigit():
            raise forms.ValidationError(
                "La identificación solo debe contener números.")
        if len(identification) > 13:
            raise forms.ValidationError(
                "La identificación no puede exceder los 13 caracteres.")
        return identification

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError(
                "El teléfono solo debe contener números.")
        if len(phone_number) > 10:
            raise forms.ValidationError(
                "El teléfono no puede exceder los 10 caracteres.")
        return phone_number


class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        fields = ['appointment', 'diagnosis', 'treatment', 'status']
        widgets = {
            'appointment': forms.Select(attrs={
                'id': 'appointmentSearch',
                'placeholder': 'Seleccione una cita...',
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detalles del diagnóstico...'
            }),
            'treatment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Plan de tratamiento o indicaciones...'
            }),
            'status': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'appointment': 'Cita',
            'diagnosis': 'Diagnóstico',
            'treatment': 'Tratamiento',
            'status': 'Estado',
        }

    def save(self, commit=True, doctor=None):
        instance = super().save(commit=False)
        if doctor:
            instance.doctor = doctor
        # Vincula automáticamente el paciente basado en la cita seleccionada
        if instance.appointment:
            instance.patient = instance.appointment.patient
        if commit:
            instance.save()
        return instance


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medication_details', 'instructions']
        widgets = {
            'medication_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Nombre, gramos, tabletas, etc.'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Cómo y cuándo tomar el medicamento.'
            }),
        }
        labels = {
            'medication_details': 'Detalles del Medicamento',
            'instructions': 'Indicaciones',
        }


class RatingForm(forms.ModelForm):
    score = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={
            'class': 'rating-radio',
        }),
        label='Calificación:'
    )

    class Meta:
        model = Rating
        fields = ['score', 'comment']
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Comparte tu experiencia con el servicio recibido...'
                }
            ),
        }
        labels = {
            'comment': 'Comentario (opcional):'
        }


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username', 'email', 'password1', 'password2',
            'first_name', 'middle_name', 'last_name', 'maternal_surname',
            'identification', 'birth_date', 'genre', 'address', 'city', 'phone_number'
        )
        labels = {
            'first_name': 'Primer Nombre',
            'middle_name': 'Segundo Nombre',
            'last_name': 'Primer Apellido',
            'maternal_surname': 'Segundo Apellido',
            'identification': 'Identificación',
            'birth_date': 'Fecha de Nacimiento',
            'genre': 'Género',
            'address': 'Dirección',
            'city': 'Ciudad',
            'phone_number': 'Teléfono',
        }


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            'username', 'email', 'first_name', 'middle_name', 'last_name', 'maternal_surname',
            'identification', 'birth_date', 'genre', 'address', 'city', 'phone_number'
        )
        labels = {
            'first_name': 'Primer Nombre',
            'middle_name': 'Segundo Nombre',
            'last_name': 'Primer Apellido',
            'maternal_surname': 'Segundo Apellido',
            'identification': 'Identificación',
            'birth_date': 'Fecha de Nacimiento',
            'genre': 'Género',
            'address': 'Dirección',
            'city': 'Ciudad',
            'phone_number': 'Teléfono',
        }


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            'username', 'email', 'first_name', 'middle_name', 'last_name', 'maternal_surname',
            'identification', 'birth_date', 'genre', 'address', 'city', 'phone_number'
        )
        labels = {
            'first_name': 'Primer Nombre',
            'middle_name': 'Segundo Nombre',
            'last_name': 'Primer Apellido',
            'maternal_surname': 'Segundo Apellido',
            'identification': 'Identificación',
            'birth_date': 'Fecha de Nacimiento',
            'genre': 'Género',
            'address': 'Dirección',
            'city': 'Ciudad',
            'phone_number': 'Teléfono',
        }
