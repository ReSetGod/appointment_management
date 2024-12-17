from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.models import Group
from .models import Appointment, Doctor, Speciality, User


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
            "identification": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "birth_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d"
            ),
            "genre": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurarse de que la fecha siga el formato correcto
        if self.instance and self.instance.birth_date:
            self.initial["birth_date"] = self.instance.birth_date.strftime(
                "%Y-%m-%d")
