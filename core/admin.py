from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Speciality, Doctor, User, Appointment


class CustomUserAdmin(BaseUserAdmin):
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


# Registra el modelo User con la administración personalizada
admin.site.register(User, CustomUserAdmin)
admin.site.register(Speciality)
admin.site.register(Doctor)
admin.site.register(Appointment)
