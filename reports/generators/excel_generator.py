from io import BytesIO
import pandas as pd
from .base import ReportGenerator


class ExcelReportGenerator(ReportGenerator):
    def get_headers(self, report_type):
        headers = {
            'appointments': {
                'id': 'ID',
                'appointment_date': 'Fecha',
                'appointment_time': 'Hora',
                'patient__first_name': 'Nombre Paciente',
                'patient__last_name': 'Apellido Paciente',
                'doctor__first_name': 'Nombre Doctor',
                'doctor__last_name': 'Apellido Doctor',
                'speciality__name': 'Especialidad',
                'status': 'Estado'
            },
            'patients': {
                'id': 'ID',
                'first_name': 'Nombre',
                'last_name': 'Apellido',
                'email': 'Correo',
                'identification': 'Cédula',
                'phone_number': 'Teléfono',
                'birth_date': 'Fecha Nacimiento',
                'genre': 'Género'
            },
            'doctors': {
                'id': 'ID',
                'first_name': 'Nombre',
                'last_name': 'Apellido',
                'middle_name': 'Segundo nombre',
                'maternal_surname': 'Segundo apellido',
                'email': 'Correo',
                'identification': 'Cédula',
                'phone_number': 'Teléfono',
                'specialities__name': 'Especialidades',
                'address': 'Dirección',
                'city': 'Ciudad'
            }
        }
        return headers.get(report_type, {})

    def generate(self, data, template=None):
        df = pd.DataFrame(data)
        report_type = template.split('/')[-1].split('.')[0]
        headers = self.get_headers(report_type)

        # Formatear el género antes de renombrar las columnas
        if 'genre' in df.columns:
            genre_map = {
                'F': 'Femenino',
                'M': 'Masculino'
            }
            df['genre'] = df['genre'].map(genre_map)

        # Formatear estatus antes de renombrar las columnas
        if 'status' in df.columns:
            status_map = {
                'PENDING': 'Pendiente',
                'CONFIRMED': 'Confirmada',
                'CANCELLED': 'Cancelada',
                'ATTENDED': 'Atendida',
                'NO_SHOW': 'No asistió'
            }
            df['status'] = df['status'].map(status_map)

        # Renombrar las columnas
        if headers:
            df = df.rename(columns=headers)

        excel_file = BytesIO()
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).apply(
                    len).max(), len(str(col))) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = max_length

        excel_file.seek(0)
        return excel_file.getvalue()
