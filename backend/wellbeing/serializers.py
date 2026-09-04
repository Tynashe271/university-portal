from rest_framework import serializers
from .models import DailySELCheckIn

class DailySELCheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySELCheckIn
        fields = '__all__'