from rest_framework import viewsets
from config.permissions import IsAdminUser
from .models import Club, ClubMembership, ClubEvent, Achievement
from .serializers import ClubSerializer, ClubMembershipSerializer, ClubEventSerializer, AchievementSerializer


class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.select_related('coach').all()
    serializer_class = ClubSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class ClubMembershipViewSet(viewsets.ModelViewSet):
    queryset = ClubMembership.objects.select_related('club', 'student').all()
    serializer_class = ClubMembershipSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        club = self.request.query_params.get('club')
        student = self.request.query_params.get('student')
        if club:
            queryset = queryset.filter(club=club)
        if student:
            queryset = queryset.filter(student=student)
        return queryset


class ClubEventViewSet(viewsets.ModelViewSet):
    queryset = ClubEvent.objects.select_related('club').all()
    serializer_class = ClubEventSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        club = self.request.query_params.get('club')
        if club:
            queryset = queryset.filter(club=club)
        return queryset


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.select_related('club', 'student').all()
    serializer_class = AchievementSerializer
    permission_classes = [IsAdminUser]
