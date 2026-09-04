from django.urls import path
from .views import (
    ForumListCreateView, ForumDetailView,
    ThreadListCreateView, ThreadDetailView,
    ReplyListCreateView, ReplyDetailView,
    like_thread, subscribe_forum, user_subscriptions, forum_statistics
)

urlpatterns = [
    # Forums
    path('forums/', ForumListCreateView.as_view(), name='forum-list'),
    path('forums/<int:pk>/', ForumDetailView.as_view(), name='forum-detail'),
    
    # Threads
    path('threads/', ThreadListCreateView.as_view(), name='thread-list'),
    path('threads/<int:pk>/', ThreadDetailView.as_view(), name='thread-detail'),
    path('threads/<int:thread_id>/like/', like_thread, name='like-thread'),
    
    # Replies
    path('replies/', ReplyListCreateView.as_view(), name='reply-list'),
    path('replies/<int:pk>/', ReplyDetailView.as_view(), name='reply-detail'),
    
    # Subscriptions
    path('forums/<int:forum_id>/subscribe/', subscribe_forum, name='subscribe-forum'),
    path('subscriptions/', user_subscriptions, name='user-subscriptions'),
    
    # Statistics
    path('forums/<int:forum_id>/statistics/', forum_statistics, name='forum-statistics'),
]