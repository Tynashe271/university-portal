from rest_framework import serializers
from .models import AdmissionApplication, MeritList

class AdmissionApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionApplication
        fields = '__all__'
        read_only_fields = ['application_number', 'created_at', 'updated_at']

class MeritListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeritList
        fields = '__all__'