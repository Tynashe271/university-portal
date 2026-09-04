from rest_framework import serializers
from .models import NewsEvent


class NewsEventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = NewsEvent
        fields = [
            'id', 'title', 'summary', 'body', 'category', 'event_date', 'location',
            'published', 'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
