from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from config.permissions import IsAdminUser
from .models import BusRoute, BusStop, Bus, Driver, StudentBusAssignment
from .serializers import BusRouteSerializer, BusStopSerializer, BusSerializer, DriverSerializer, StudentBusAssignmentSerializer

class BusRouteViewSet(viewsets.ModelViewSet):
    queryset = BusRoute.objects.all()
    serializer_class = BusRouteSerializer
    permission_classes = [IsAdminUser]


class BusStopViewSet(viewsets.ModelViewSet):
    queryset = BusStop.objects.all()
    serializer_class = BusStopSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        route = self.request.query_params.get('route')
        if route:
            queryset = queryset.filter(route=route)
        return queryset


class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    permission_classes = [IsAdminUser]


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.select_related('user', 'assigned_bus').all()
    serializer_class = DriverSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['post'])
    def quick_add(self, request):
        """Create a driver login account and profile in one call — same
        reasoning as admissions' convert_to_student and parents' quick_add."""
        full_name = (request.data.get('full_name') or '').strip()
        license_number = request.data.get('license_number')
        license_expiry_date = request.data.get('license_expiry_date')
        if not full_name or not license_number or not license_expiry_date:
            return Response(
                {'error': 'full_name, license_number and license_expiry_date are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.utils.crypto import get_random_string
        from django.utils import timezone
        from students.models import User

        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        year = timezone.now().year
        count = User.objects.filter(role='driver', enrollment_date__year=year).count() + 1
        username = f"driver{year}{count:04d}"
        raw_password = get_random_string(10)

        user = User.objects.create_user(
            username=username, password=raw_password, first_name=first_name,
            last_name=last_name, role='driver', phone=request.data.get('phone', ''),
        )
        driver = Driver.objects.create(
            user=user,
            license_number=license_number,
            license_expiry_date=license_expiry_date,
            assigned_bus_id=request.data.get('assigned_bus') or None,
            phone=request.data.get('phone', ''),
            emergency_contact=request.data.get('emergency_contact', ''),
        )
        return Response({
            'username': user.username,
            'temporary_password': raw_password,
            'driver': DriverSerializer(driver).data,
        }, status=status.HTTP_201_CREATED)


class StudentBusAssignmentViewSet(viewsets.ModelViewSet):
    queryset = StudentBusAssignment.objects.select_related('student', 'bus', 'pickup_stop', 'dropoff_stop').all()
    serializer_class = StudentBusAssignmentSerializer
    permission_classes = [IsAdminUser]
