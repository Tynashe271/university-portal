from rest_framework import serializers
from .models import CalendarEvent


class CalendarEventSerializer(serializers.ModelSerializer):
    term_label = serializers.SerializerMethodField()

    class Meta:
        model = CalendarEvent
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']

    def get_term_label(self, obj):
        return str(obj.term) if obj.term else None
