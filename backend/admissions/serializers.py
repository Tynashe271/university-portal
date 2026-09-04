from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import AdmissionApplication, MeritList

class AdmissionApplicationSerializer(serializers.ModelSerializer):
    portal_password = serializers.CharField(write_only=True, required=True, min_length=4)
    has_student_account = serializers.SerializerMethodField()

    class Meta:
        model = AdmissionApplication
        fields = '__all__'
        read_only_fields = ['application_number', 'created_at', 'updated_at']

    def get_has_student_account(self, obj):
        return hasattr(obj, 'student_account') and obj.student_account is not None

    def create(self, validated_data):
        raw_password = validated_data.pop('portal_password')
        validated_data['portal_password'] = make_password(raw_password)
        return super().create(validated_data)

class MeritListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeritList
        fields = '__all__'
