from django.utils import timezone
from .base import ReportGenerator

from django.template.loader import render_to_string
from weasyprint import HTML


class PDFReportGenerator(ReportGenerator):
    def generate(self, data, template):
        context = {
            'data': data,
            'report_date': timezone.now(),
        }

        try:
            # Renderizar el template con los datos
            html = render_to_string(template, context)

            # Generar el PDF
            pdf = HTML(
                string=html,
                encoding='utf-8'
            ).write_pdf(
                presentational_hints=True
            )
            return pdf

        except Exception as e:
            raise Exception(f"Error generating PDF: {str(e)}")
