import io
import logging

from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa

logger = logging.getLogger(__name__)


def generate_acceptance_letter(application):
    """Render the acceptance letter as a PDF and save it onto
    `application.admission_letter`, so it shows up in the applicant
    portal as soon as staff approve the application.

    Never raises — a broken PDF renderer should not block an approval
    decision. Returns True/False for callers that want to know whether
    the letter was actually generated.
    """
    context = {
        'application': application,
        'grade_label': application.get_grade_applying_for_display(),
        'issue_date': timezone.now(),
    }
    try:
        html = render_to_string('pdf/acceptance_letter.html', context)
        buffer = io.BytesIO()
        result = pisa.CreatePDF(html, dest=buffer)
        if result.err:
            raise RuntimeError('xhtml2pdf reported errors rendering the acceptance letter')
        filename = f"acceptance_letter_{application.application_number}.pdf"
        application.admission_letter.save(filename, ContentFile(buffer.getvalue()), save=True)
        return True
    except Exception:
        logger.exception(
            f"Failed to generate acceptance letter for {application.application_number}"
        )
        return False
