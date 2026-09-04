from rest_framework import serializers
from .models import BusRoute, BusStop, Bus, Driver, StudentBusAssignment

class BusRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusRoute
        fields = '__all__'


class BusStopSerializer(serializers.ModelSerializer):
    route_name = serializers.CharField(source='route.route_name', read_only=True)

    class Meta:
        model = BusStop
        fields = '__all__'


class BusSerializer(serializers.ModelSerializer):
    route_name = serializers.CharField(source='route.route_name', read_only=True, default=None)

    class Meta:
        model = Bus
        fields = '__all__'


class DriverSerializer(serializers.ModelSerializer):
    driver_name = serializers.SerializerMethodField()
    bus_number = serializers.CharField(source='assigned_bus.bus_number', read_only=True, default=None)

    class Meta:
        model = Driver
        fields = '__all__'

    def get_driver_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username


class StudentBusAssignmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    bus_number = serializers.CharField(source='bus.bus_number', read_only=True)
    pickup_stop_name = serializers.CharField(source='pickup_stop.stop_name', read_only=True)
    dropoff_stop_name = serializers.CharField(source='dropoff_stop.stop_name', read_only=True)

    class Meta:
        model = StudentBusAssignment
        fields = '__all__'

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username
