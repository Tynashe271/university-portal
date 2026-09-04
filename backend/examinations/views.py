from rest_framework import viewsets
from .models import QuestionBank
from .serializers import QuestionBankSerializer

class QuestionBankViewSet(viewsets.ModelViewSet):
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer