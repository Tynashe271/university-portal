from rest_framework import serializers
from .models import FeeStructure, FeeAccount, FeePayment

class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = '__all__'

class FeeAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeAccount
        fields = '__all__'

class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = '__all__'