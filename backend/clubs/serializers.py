from rest_framework import serializers
from .models import Club, ClubMembership, ClubEvent, Achievement


class ClubSerializer(serializers.ModelSerializer):
    coach_name = serializers.SerializerMethodField()
    member_count = serializers.IntegerField(source='memberships.count', read_only=True)

    class Meta:
        model = Club
        fields = '__all__'

    def get_coach_name(self, obj):
        return obj.coach.name if obj.coach else None


class ClubMembershipSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    club_name = serializers.CharField(source='club.name', read_only=True)

    class Meta:
        model = ClubMembership
        fields = '__all__'

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username


class ClubEventSerializer(serializers.ModelSerializer):
    club_name = serializers.CharField(source='club.name', read_only=True)

    class Meta:
        model = ClubEvent
        fields = '__all__'


class AchievementSerializer(serializers.ModelSerializer):
    club_name = serializers.CharField(source='club.name', read_only=True, default=None)
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = '__all__'

    def get_student_name(self, obj):
        if not obj.student:
            return None
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username
