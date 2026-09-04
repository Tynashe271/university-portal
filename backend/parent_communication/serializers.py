from rest_framework import serializers
from .models import Message, ConferenceSchedule

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class ConferenceScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceSchedule
        fields = '__all__'