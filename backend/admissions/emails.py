import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_application_confirmation_email(application):
    """Email the parent/guardian their application reference so they can
    track the application later in the applicant portal.

    Never raises: a broken or unconfigured mail server should not stop an
    application from being accepted. Returns True/False for callers that
    want to know whether it actually went out.
    """
    if not application.parent_email:
        return False

    context = {
        'application': application,
        'grade_label': application.get_grade_applying_for_display(),
        'portal_url': f"{settings.FRONTEND_URL}/applicant-portal",
    }
    subject = f"Application received - {application.application_number}"

    try:
        text_body = render_to_string('email/admission_confirmation.txt', context)
        html_body = render_to_string('email/admission_confirmation.html', context)
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[application.parent_email],
        )
        message.attach_alternative(html_body, 'text/html')
        message.send(fail_silently=False)
        return True
    except Exception:
        logger.exception(
            f"Failed to send admission confirmation email for {application.application_number}"
        )
        return False
