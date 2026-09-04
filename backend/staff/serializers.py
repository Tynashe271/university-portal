from rest_framework import serializers
from .models import StaffProfile

class StaffProfileSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='name', read_only=True)
    employee_type_label = serializers.CharField(source='get_employee_type_display', read_only=True)

    class Meta:
        model = StaffProfile
        fields = '__all__'
        read_only_fields = ['employee_id', 'created_at', 'updated_at']

    def validate(self, data):
        # A record needs some way to show a name: either a linked user
        # account, or a name typed in directly on the quick-add form.
        user = data.get('user', getattr(self.instance, 'user', None))
        full_name = data.get('full_name', getattr(self.instance, 'full_name', ''))
        if not user and not full_name:
            raise serializers.ValidationError({'full_name': 'Enter a name, or link a user account.'})
        return data
