from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Announcement, AnnouncementRead
from .serializers import AnnouncementSerializer, AnnouncementReadSerializer
from students.models import User

class AnnouncementListCreateView(generics.ListCreateAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Announcement.objects.filter(published=True)
        
        # Filter by target audience
        target = self.request.query_params.get('target', None)
        if target:
            queryset = queryset.filter(target_audience=target)
        
        # Filter by priority
        priority = self.request.query_params.get('priority', None)
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter active announcements
        active_only = self.request.query_params.get('active', 'true')
        if active_only == 'true':
            queryset = [a for a in queryset if a.is_active()]
        
        # Role-based filtering
        if user.is_student():
            return [a for a in queryset if a.target_audience in ['all', 'students']]
        elif user.is_admin_user():
            return [a for a in queryset if a.target_audience in ['all', 'admins']]
        return []
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save(author=user)
        else:
            raise PermissionError("Only admins can create announcements")

class AnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Announcement.objects.filter(published=True)
        
        if user.is_student():
            return [a for a in queryset if a.target_audience in ['all', 'students']]
        elif user.is_admin_user():
            return [a for a in queryset if a.target_audience in ['all', 'admins']]
        return []
    
    def perform_update(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save()
        else:
            raise PermissionError("Only admins can update announcements")
    
    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_admin_user():
            instance.delete()
        else:
            raise PermissionError("Only admins can delete announcements")

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_as_read(request, announcement_id):
    try:
        announcement = Announcement.objects.get(id=announcement_id)
        user = request.user
        
        # Check if user has access to this announcement
        if user.is_student() and announcement.target_audience not in ['all', 'students']:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        elif user.is_admin_user() and announcement.target_audience not in ['all', 'admins']:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Create or get the read record
        read_record, created = AnnouncementRead.objects.get_or_create(
            announcement=announcement,
            user=user
        )
        
        if created:
            return Response({'message': 'Marked as read'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Already read'}, status=status.HTTP_200_OK)
            
    except Announcement.DoesNotExist:
        return Response({'error': 'Announcement not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_announcements(request):
    user = request.user
    announcements = Announcement.objects.filter(published=True)
    
    # Filter based on user role
    if user.is_student():
        announcements = [a for a in announcements if a.target_audience in ['all', 'students']]
    elif user.is_admin_user():
        announcements = [a for a in announcements if a.target_audience in ['all', 'admins']]
    
    # Filter active announcements
    announcements = [a for a in announcements if a.is_active()]
    
    # Get read status
    read_announcement_ids = AnnouncementRead.objects.filter(
        user=user
    ).values_list('announcement_id', flat=True)
    
    for announcement in announcements:
        announcement.is_read_by_user = announcement.id in read_announcement_ids
    
    serializer = AnnouncementSerializer(announcements, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def announcement_stats(request):
    user = request.user
    
    if not user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    total_announcements = Announcement.objects.count()
    active_announcements = len([a for a in Announcement.objects.all() if a.is_active()])
    total_reads = AnnouncementRead.objects.count()
    
    return Response({
        'total_announcements': total_announcements,
        'active_announcements': active_announcements,
        'total_reads': total_reads,
    })
