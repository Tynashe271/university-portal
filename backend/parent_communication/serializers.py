from rest_framework import serializers
from .models import Message, ConferenceSchedule, ParentProfile, StudentParentRelation


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    recipient_name = serializers.CharField(source='recipient.username', read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['sender', 'sent_at', 'read_at', 'is_read']


class ConferenceScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceSchedule
        fields = '__all__'


class StudentParentRelationSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentParentRelation
        fields = ['id', 'student', 'student_name', 'parent', 'relationship', 'is_primary_contact', 'pickup_permission', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username


class ParentProfileSerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = ParentProfile
        fields = ['id', 'user', 'parent_name', 'username', 'email', 'phone', 'relationship',
                  'occupation', 'work_phone', 'receives_sms', 'receives_email', 'children']
        read_only_fields = ['id', 'user']

    def get_parent_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def get_children(self, obj):
        return StudentParentRelationSerializer(
            StudentParentRelation.objects.filter(parent=obj.user), many=True
        ).data
