from rest_framework import serializers
from .models import Hostel, Room, Bed, BoardingAllocation, LeaveRequest, RollCall, RollCallRecord, Visitor


class HostelSerializer(serializers.ModelSerializer):
    warden_name = serializers.SerializerMethodField()
    room_count = serializers.IntegerField(source='rooms.count', read_only=True)

    class Meta:
        model = Hostel
        fields = '__all__'

    def get_warden_name(self, obj):
        return obj.warden.name if obj.warden else None


class RoomSerializer(serializers.ModelSerializer):
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)
    bed_count = serializers.IntegerField(source='beds.count', read_only=True)

    class Meta:
        model = Room
        fields = '__all__'


class BedSerializer(serializers.ModelSerializer):
    room_label = serializers.CharField(source='room.room_number', read_only=True)
    hostel_name = serializers.CharField(source='room.hostel.name', read_only=True)

    class Meta:
        model = Bed
        fields = '__all__'


class BoardingAllocationSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    bed_label = serializers.CharField(source='bed.bed_number', read_only=True)
    room_label = serializers.CharField(source='bed.room.room_number', read_only=True)
    hostel_name = serializers.CharField(source='bed.room.hostel.name', read_only=True)
    hostel_id = serializers.IntegerField(source='bed.room.hostel.id', read_only=True)

    class Meta:
        model = BoardingAllocation
        fields = '__all__'
        read_only_fields = ['date_allocated', 'date_vacated', 'status', 'allocated_by']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username


class LeaveRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['status', 'requested_at', 'decided_by', 'decided_at']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username


class RollCallRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = RollCallRecord
        fields = '__all__'

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username


class RollCallSerializer(serializers.ModelSerializer):
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)
    records = RollCallRecordSerializer(many=True, read_only=True)
    present_count = serializers.SerializerMethodField()
    absent_count = serializers.SerializerMethodField()

    class Meta:
        model = RollCall
        fields = '__all__'
        read_only_fields = ['taken_by', 'created_at']

    def get_present_count(self, obj):
        return obj.records.filter(present=True).count()

    def get_absent_count(self, obj):
        return obj.records.filter(present=False).count()


class VisitorSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Visitor
        fields = '__all__'
        read_only_fields = ['recorded_by']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username
