from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Forum, Thread, Reply, ForumLike, ForumSubscription
from .serializers import ForumSerializer, ThreadSerializer, ReplySerializer, ForumLikeSerializer, ForumSubscriptionSerializer
from courses.models import Course, Enrollment
from students.models import User

class ForumListCreateView(generics.ListCreateAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course', None)
        forum_type = self.request.query_params.get('type', None)
        
        queryset = Forum.objects.filter(is_active=True)
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if forum_type:
            queryset = queryset.filter(forum_type=forum_type)
        
        if user.is_student():
            return queryset.filter(is_public=True)
        elif user.is_admin_user():
            return queryset
        return Forum.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save(created_by=user)
        else:
            raise PermissionError("Only admins can create forums")

class ForumDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student():
            return Forum.objects.filter(is_public=True, is_active=True)
        elif user.is_admin_user():
            return Forum.objects.all()
        return Forum.objects.none()
    
    def perform_update(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save()
        else:
            raise PermissionError("Only admins can update forums")
    
    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_admin_user():
            instance.delete()
        else:
            raise PermissionError("Only admins can delete forums")

class ThreadListCreateView(generics.ListCreateAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        forum_id = self.request.query_params.get('forum', None)
        
        queryset = Thread.objects.all()
        
        if forum_id:
            queryset = queryset.filter(forum_id=forum_id)
        
        # Filter by accessible forums
        if user.is_student():
            accessible_forums = Forum.objects.filter(is_public=True, is_active=True)
            return queryset.filter(forum__in=accessible_forums)
        elif user.is_admin_user():
            return queryset
        return Thread.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        forum_id = self.request.data.get('forum')
        
        try:
            forum = Forum.objects.get(id=forum_id)
            
            if not forum.is_active:
                raise ValueError("Forum is not active")
            
            if user.is_student() and not forum.is_public:
                raise PermissionError("Cannot post in private forums")
            
            thread = serializer.save(author=user)
            return thread
            
        except Forum.DoesNotExist:
            raise ValueError("Forum not found")

class ThreadDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student():
            accessible_forums = Forum.objects.filter(is_public=True, is_active=True)
            return Thread.objects.filter(forum__in=accessible_forums)
        elif user.is_admin_user():
            return Thread.objects.all()
        return Thread.objects.none()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.views += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        user = self.request.user
        thread = self.get_object()
        
        if user.is_admin_user():
            serializer.save()
        elif user == thread.author and not thread.is_locked:
            serializer.save(is_edited=True)
        else:
            raise PermissionError("Permission denied")
    
    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_admin_user() or user == instance.author:
            instance.delete()
        else:
            raise PermissionError("Permission denied")

class ReplyListCreateView(generics.ListCreateAPIView):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        thread_id = self.request.query_params.get('thread', None)
        
        queryset = Reply.objects.all()
        
        if thread_id:
            queryset = queryset.filter(thread_id=thread_id)
        
        # Filter by accessible threads
        if user.is_student():
            accessible_forums = Forum.objects.filter(is_public=True, is_active=True)
            return queryset.filter(thread__forum__in=accessible_forums)
        elif user.is_admin_user():
            return queryset
        return Reply.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        thread_id = self.request.data.get('thread')
        
        try:
            thread = Thread.objects.get(id=thread_id)
            
            if thread.is_locked:
                raise PermissionError("Thread is locked")
            
            reply = serializer.save(author=user)
            return reply
            
        except Thread.DoesNotExist:
            raise ValueError("Thread not found")

class ReplyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student():
            accessible_forums = Forum.objects.filter(is_public=True, is_active=True)
            return Reply.objects.filter(thread__forum__in=accessible_forums)
        elif user.is_admin_user():
            return Reply.objects.all()
        return Reply.objects.none()
    
    def perform_update(self, serializer):
        user = self.request.user
        reply = self.get_object()
        
        if user.is_admin_user():
            serializer.save(is_edited=True)
        elif user == reply.author and not reply.thread.is_locked:
            serializer.save(is_edited=True)
        else:
            raise PermissionError("Permission denied")
    
    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_admin_user() or user == instance.author:
            instance.delete()
        else:
            raise PermissionError("Permission denied")

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_thread(request, thread_id):
    user = request.user
    
    try:
        thread = Thread.objects.get(id=thread_id)
        
        # Check if already liked
        existing_like = ForumLike.objects.filter(thread=thread, user=user).first()
        
        if existing_like:
            existing_like.delete()
            return Response({'message': 'Like removed', 'liked': False}, status=status.HTTP_200_OK)
        else:
            ForumLike.objects.create(thread=thread, user=user)
            return Response({'message': 'Thread liked', 'liked': True}, status=status.HTTP_201_CREATED)
            
    except Thread.DoesNotExist:
        return Response({'error': 'Thread not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def subscribe_forum(request, forum_id):
    user = request.user
    
    try:
        forum = Forum.objects.get(id=forum_id)
        
        subscription, created = ForumSubscription.objects.get_or_create(
            forum=forum,
            user=user
        )
        
        if created:
            return Response({'message': 'Subscribed to forum'}, status=status.HTTP_201_CREATED)
        else:
            subscription.delete()
            return Response({'message': 'Unsubscribed from forum'}, status=status.HTTP_200_OK)
            
    except Forum.DoesNotExist:
        return Response({'error': 'Forum not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_subscriptions(request):
    user = request.user
    
    subscriptions = ForumSubscription.objects.filter(user=user)
    serializer = ForumSubscriptionSerializer(subscriptions, many=True)
    
    return Response({
        'user': user.username,
        'subscriptions': serializer.data
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def forum_statistics(request, forum_id):
    user = request.user
    
    if not user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        forum = Forum.objects.get(id=forum_id)
        
        total_threads = forum.threads.count()
        total_replies = Reply.objects.filter(thread__forum=forum).count()
        total_subscribers = forum.subscribers.count()
        total_views = sum(thread.views for thread in forum.threads.all())
        
        return Response({
            'forum': forum.name,
            'total_threads': total_threads,
            'total_replies': total_replies,
            'total_subscribers': total_subscribers,
            'total_views': total_views
        })
        
    except Forum.DoesNotExist:
        return Response({'error': 'Forum not found'}, status=status.HTTP_404_NOT_FOUND)
