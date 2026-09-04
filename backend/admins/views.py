from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import AdminPermission, SystemLog
from .serializers import AdminPermissionSerializer, SystemLogSerializer
from students.models import User

class AdminPermissionListCreateView(generics.ListCreateAPIView):
    queryset = AdminPermission.objects.all()
    serializer_class = AdminPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return AdminPermission.objects.all()
        return AdminPermission.objects.filter(admin=user)
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save(granted_by=user)

class AdminPermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdminPermission.objects.all()
    serializer_class = AdminPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return AdminPermission.objects.all()
        return AdminPermission.objects.filter(admin=user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def grant_permission(request):
    admin_id = request.data.get('admin_id')
    permission = request.data.get('permission')
    
    try:
        if not request.user.is_admin_user():
            return Response({'error': 'Only admins can grant permissions'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        admin_user = User.objects.get(id=admin_id, role='admin')
        
        existing_permission = AdminPermission.objects.filter(
            admin=admin_user, 
            permission=permission
        ).first()
        
        if existing_permission:
            return Response({'error': 'Permission already granted'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        admin_permission = AdminPermission.objects.create(
            admin=admin_user,
            permission=permission,
            granted_by=request.user
        )
        
        # Log the action
        SystemLog.objects.create(
            action='create',
            user=request.user,
            model_name='AdminPermission',
            object_id=admin_permission.id,
            description=f'Granted {permission} permission to {admin_user.username}',
            ip_address=get_client_ip(request)
        )
        
        return Response(AdminPermissionSerializer(admin_permission).data, 
                      status=status.HTTP_201_CREATED)
        
    except User.DoesNotExist:
        return Response({'error': 'Admin user not found'}, 
                      status=status.HTTP_404_NOT_FOUND)

class SystemLogListView(generics.ListAPIView):
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return SystemLog.objects.all()
        return SystemLog.objects.filter(user=user)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
