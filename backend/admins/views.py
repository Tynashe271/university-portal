from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import AdminPermission, SystemLog, SchoolSettings
from .serializers import AdminPermissionSerializer, SystemLogSerializer, SchoolSettingsSerializer
from students.models import User

class AdminPermissionListCreateView(generics.ListCreateAPIView):
    queryset = AdminPermission.objects.all()
    serializer_class = AdminPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return AdminPermission.objects.all()
        return AdminPermission.objects.filter(admin=user)
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save(granted_by=user)

class AdminPermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdminPermission.objects.all()
    serializer_class = AdminPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return AdminPermission.objects.all()
        return AdminPermission.objects.filter(admin=user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def grant_permission(request):
    admin_id = request.data.get('admin_id')
    permission = request.data.get('permission')
    
    try:
        if not request.user.is_admin_user():
            return Response({'error': 'Only admins can grant permissions'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        admin_user = User.objects.get(id=admin_id, role='admin')
        
        existing_permission = AdminPermission.objects.filter(
            admin=admin_user, 
            permission=permission
        ).first()
        
        if existing_permission:
            return Response({'error': 'Permission already granted'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        admin_permission = AdminPermission.objects.create(
            admin=admin_user,
            permission=permission,
            granted_by=request.user
        )
        
        # Log the action
        SystemLog.objects.create(
            action='create',
            user=request.user,
            model_name='AdminPermission',
            object_id=admin_permission.id,
            description=f'Granted {permission} permission to {admin_user.username}',
            ip_address=get_client_ip(request)
        )
        
        return Response(AdminPermissionSerializer(admin_permission).data, 
                      status=status.HTTP_201_CREATED)
        
    except User.DoesNotExist:
        return Response({'error': 'Admin user not found'}, 
                      status=status.HTTP_404_NOT_FOUND)

class SystemLogListView(generics.ListAPIView):
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return SystemLog.objects.all()
        return SystemLog.objects.filter(user=user)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class SchoolSettingsView(generics.RetrieveUpdateAPIView):
    """Single-row settings — GET/PATCH the school's own configuration."""
    serializer_class = SchoolSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return SchoolSettings.load()

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        from config.permissions import IsAdminUser
        return [IsAdminUser()]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def reports(request):
    """Cross-module numbers for the Reports & Analytics panel — every
    figure here is a real query against live data, not a placeholder."""
    if not request.user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    from datetime import timedelta
    from django.utils import timezone
    from django.db.models import Sum, Count

    now = timezone.now()

    # Enrolment
    students_qs = User.objects.filter(role='student')
    total_students = students_qs.count()
    by_grade = list(
        students_qs.exclude(classroom__isnull=True)
        .values('classroom__grade').annotate(count=Count('id')).order_by('-count')
    )

    # Attendance (last 30 days)
    from attendance.models import DailyAttendance
    since = now.date() - timedelta(days=30)
    recent = DailyAttendance.objects.filter(date__gte=since)
    attendance_total = recent.count()
    attendance_present = recent.filter(status__in=['present', 'late']).count()
    attendance_rate = round(attendance_present / attendance_total * 100, 1) if attendance_total else None

    # Fees
    from fees.models import FeeAccount, FeePayment
    total_collected = FeePayment.objects.filter(status='completed').aggregate(t=Sum('amount'))['t'] or 0
    total_outstanding = FeeAccount.objects.aggregate(t=Sum('fees_due'))['t'] or 0

    # Admissions
    from admissions.models import AdmissionApplication
    admissions_by_status = list(
        AdmissionApplication.objects.values('status').annotate(count=Count('id')).order_by('-count')
    )

    # Library
    from library.models import BookCheckout
    active_checkouts = BookCheckout.objects.filter(status='checked_out').count()
    overdue_checkouts = BookCheckout.objects.filter(status='checked_out', due_date__lt=now.date()).count()

    # Discipline
    from students.models import BehavioralIncident
    incidents_by_severity = list(
        BehavioralIncident.objects.values('severity').annotate(count=Count('id')).order_by('-count')
    )

    return Response({
        'generated_at': now,
        'enrolment': {'total_students': total_students, 'by_grade': by_grade},
        'attendance': {'rate_last_30_days': attendance_rate, 'records_last_30_days': attendance_total},
        'fees': {'total_collected': total_collected, 'total_outstanding': total_outstanding},
        'admissions': {'by_status': admissions_by_status},
        'library': {'active_checkouts': active_checkouts, 'overdue_checkouts': overdue_checkouts},
        'discipline': {'by_severity': incidents_by_severity},
    })
