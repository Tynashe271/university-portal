from rest_framework import viewsets
from .models import Message, ConferenceSchedule
from .serializers import MessageSerializer, ConferenceScheduleSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class ConferenceScheduleViewSet(viewsets.ModelViewSet):
    queryset = ConferenceSchedule.objects.all()
    serializer_class = ConferenceScheduleSerializer