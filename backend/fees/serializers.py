from rest_framework import serializers
from .models import FeeStructure, FeeAccount, FeePayment

class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = '__all__'

class FeeAccountSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_number = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = FeeAccount
        fields = '__all__'
        read_only_fields = ['fees_due']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username

class FeePaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = FeePayment
        fields = '__all__'
        read_only_fields = ['payment_date', 'transaction_id', 'receipt_number', 'receipt_generated', 'processed_by', 'status']

    def get_student_name(self, obj):
        student = obj.fee_account.student
        return f"{student.first_name} {student.last_name}".strip() or student.username

    def validate(self, data):
        amount = data.get('amount')
        fee_account = data.get('fee_account', getattr(self.instance, 'fee_account', None))
        if amount is not None and amount <= 0:
            raise serializers.ValidationError({'amount': 'Payment amount must be greater than zero.'})
        return data
