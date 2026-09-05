from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from config.permissions import IsAdminUser
from .models import Hostel, Room, Bed, BoardingAllocation, LeaveRequest, RollCall, RollCallRecord, Visitor
from .serializers import (
    HostelSerializer, RoomSerializer, BedSerializer, BoardingAllocationSerializer,
    LeaveRequestSerializer, RollCallSerializer, RollCallRecordSerializer, VisitorSerializer,
)


class HostelViewSet(viewsets.ModelViewSet):
    queryset = Hostel.objects.select_related('warden').all()
    serializer_class = HostelSerializer
    permission_classes = [IsAdminUser]


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.select_related('hostel').all()
    serializer_class = RoomSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        hostel = self.request.query_params.get('hostel')
        if hostel:
            queryset = queryset.filter(hostel=hostel)
        return queryset


class BedViewSet(viewsets.ModelViewSet):
    queryset = Bed.objects.select_related('room', 'room__hostel').all()
    serializer_class = BedSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        room = self.request.query_params.get('room')
        status_param = self.request.query_params.get('status')
        if room:
            queryset = queryset.filter(room=room)
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset


class BoardingAllocationViewSet(viewsets.ModelViewSet):
    queryset = BoardingAllocation.objects.select_related('student', 'bed', 'bed__room', 'bed__room__hostel').all()
    serializer_class = BoardingAllocationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    def perform_create(self, serializer):
        allocation = serializer.save(allocated_by=self.request.user)
        allocation.bed.status = 'occupied'
        allocation.bed.save(update_fields=['status'])

    @action(detail=True, methods=['post'])
    def vacate(self, request, pk=None):
        allocation = self.get_object()
        if allocation.status == 'vacated':
            return Response({'error': 'This allocation is already vacated.'}, status=status.HTTP_400_BAD_REQUEST)
        allocation.status = 'vacated'
        allocation.date_vacated = timezone.localdate()
        allocation.save(update_fields=['status', 'date_vacated'])
        allocation.bed.status = 'available'
        allocation.bed.save(update_fields=['status'])
        return Response(BoardingAllocationSerializer(allocation).data)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('student').all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'approved'
        leave.decided_by = request.user
        leave.decided_at = timezone.now()
        leave.save(update_fields=['status', 'decided_by', 'decided_at'])
        return Response(LeaveRequestSerializer(leave).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'rejected'
        leave.decided_by = request.user
        leave.decided_at = timezone.now()
        leave.save(update_fields=['status', 'decided_by', 'decided_at'])
        return Response(LeaveRequestSerializer(leave).data)


class RollCallViewSet(viewsets.ModelViewSet):
    queryset = RollCall.objects.select_related('hostel').prefetch_related('records').all()
    serializer_class = RollCallSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        hostel = self.request.query_params.get('hostel')
        date = self.request.query_params.get('date')
        if hostel:
            queryset = queryset.filter(hostel=hostel)
        if date:
            queryset = queryset.filter(date=date)
        return queryset

    def perform_create(self, serializer):
        serializer.save(taken_by=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_mark(self, request):
        """Take a whole hostel's roll call in one call:
        {"hostel": 1, "date": "2026-09-04", "session": "evening",
         "entries": [{"student": 5, "present": true, "notes": ""}, ...]}
        """
        hostel_id = request.data.get('hostel')
        date = request.data.get('date')
        session = request.data.get('session')
        entries = request.data.get('entries', [])
        if not hostel_id or not date or not session or not entries:
            return Response({'error': 'hostel, date, session and entries are required.'}, status=status.HTTP_400_BAD_REQUEST)

        roll_call, _created = RollCall.objects.update_or_create(
            hostel_id=hostel_id, date=date, session=session,
            defaults={'taken_by': request.user},
        )
        for entry in entries:
            student_id = entry.get('student')
            if not student_id:
                continue
            RollCallRecord.objects.update_or_create(
                roll_call=roll_call, student_id=student_id,
                defaults={'present': entry.get('present', True), 'notes': entry.get('notes', '')},
            )
        return Response(RollCallSerializer(roll_call).data, status=status.HTTP_201_CREATED)


class VisitorViewSet(viewsets.ModelViewSet):
    queryset = Visitor.objects.select_related('student').all()
    serializer_class = VisitorSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        student = self.request.query_params.get('student')
        if student:
            queryset = queryset.filter(student=student)
        return queryset

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)
