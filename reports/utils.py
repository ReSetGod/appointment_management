from django.utils import timezone
from enum import Enum

from .generators.pdf_generator import PDFReportGenerator
from .generators.excel_generator import ExcelReportGenerator
from .generators.docx_generator import DocxReportGenerator
from datetime import datetime


class ReportFormat(Enum):
    PDF = 'pdf'
    EXCEL = 'excel'
    DOCX = 'docx'


class ReportType(Enum):
    APPOINTMENTS = 'appointments'
    PATIENTS = 'patients'
    DOCTORS = 'doctors'


def get_report_generator(format_type):
    generators = {
        ReportFormat.PDF: PDFReportGenerator(),
        ReportFormat.EXCEL: ExcelReportGenerator(),
        ReportFormat.DOCX: DocxReportGenerator()
    }
    return generators.get(format_type)


def generate_report(report_type, format_type, data):
    generator = get_report_generator(format_type)
    template = f'reports/{report_type.value}.html'
    return generator.generate(data, template)


def get_date_range(start_date, end_date):
    date_range = {}

    if start_date:
        date_range['gte'] = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        date_range['lte'] = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d'))
    if start_date and not end_date:
        date_range['lte'] = timezone.now()
    if end_date and not start_date:
        date_range['gte'] = timezone.make_aware(datetime.min)

    return date_range
