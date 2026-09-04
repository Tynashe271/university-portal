def log_action(user, action, model_name, object_id=None, description='', request=None):
    """Write one row to the audit trail (admins.SystemLog). Call this from
    the handful of actions where knowing who did what actually matters:
    admission decisions, payments, student-record changes — not every
    read or routine list view.
    """
    from .models import SystemLog
    ip = None
    if request is not None:
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = xff.split(',')[0] if xff else request.META.get('REMOTE_ADDR')
    SystemLog.objects.create(
        user=user, action=action, model_name=model_name,
        object_id=object_id, description=description, ip_address=ip,
    )
