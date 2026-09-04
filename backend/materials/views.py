from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import FileResponse
from django.core.exceptions import PermissionDenied
from .models import CourseMaterial, MaterialFolder
from .serializers import CourseMaterialSerializer, MaterialFolderSerializer
from courses.models import Course
from students.models import User

class CourseMaterialListCreateView(generics.ListCreateAPIView):
    queryset = CourseMaterial.objects.all()
    serializer_class = CourseMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course', None)
        folder_id = self.request.query_params.get('folder', None)
        
        queryset = CourseMaterial.objects.all()
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        
        if user.is_student():
            return queryset.filter(is_public=True)
        elif user.is_admin_user():
            return queryset
        return CourseMaterial.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save(uploaded_by=user)
        else:
            raise PermissionDenied("Only admins can upload materials")

class CourseMaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CourseMaterial.objects.all()
    serializer_class = CourseMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student():
            return CourseMaterial.objects.filter(is_public=True)
        elif user.is_admin_user():
            return CourseMaterial.objects.all()
        return CourseMaterial.objects.none()
    
    def perform_update(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save()
        else:
            raise PermissionDenied("Only admins can update materials")
    
    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_admin_user():
            instance.delete()
        else:
            raise PermissionDenied("Only admins can delete materials")

class MaterialFolderListCreateView(generics.ListCreateAPIView):
    queryset = MaterialFolder.objects.all()
    serializer_class = MaterialFolderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course', None)
        
        queryset = MaterialFolder.objects.all()
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        if user.is_admin_user():
            return queryset
        return queryset.filter(is_public=True) if hasattr(queryset.model, 'is_public') else queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save(created_by=user)
        else:
            raise PermissionDenied("Only admins can create folders")

class MaterialFolderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MaterialFolder.objects.all()
    serializer_class = MaterialFolderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save()
        else:
            raise PermissionDenied("Only admins can update folders")
    
    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_admin_user():
            instance.delete()
        else:
            raise PermissionDenied("Only admins can delete folders")

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_material(request, material_id):
    try:
        material = CourseMaterial.objects.get(id=material_id)
        user = request.user
        
        # Check permissions
        if user.is_student() and not material.is_public:
            return Response({'error': 'Material is not public'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        if material.file:
            material.increment_download()
            file_handle = material.file.open('rb')
            response = FileResponse(file_handle, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{material.title}"'
            return response
        elif material.url:
            material.increment_download()
            return Response({'url': material.url}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No file or URL available'}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
    except CourseMaterial.DoesNotExist:
        return Response({'error': 'Material not found'}, 
                      status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def course_materials(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        user = request.user
        
        # Check if user has access to this course
        if user.is_student():
            from courses.models import Enrollment
            if not Enrollment.objects.filter(
                student=user, 
                course=course, 
                status='enrolled'
            ).exists():
                return Response({'error': 'Not enrolled in this course'}, 
                              status=status.HTTP_403_FORBIDDEN)
        
        materials = CourseMaterial.objects.filter(course=course)
        if user.is_student():
            materials = materials.filter(is_public=True)
        
        folders = MaterialFolder.objects.filter(course=course)
        
        return Response({
            'materials': CourseMaterialSerializer(materials, many=True).data,
            'folders': MaterialFolderSerializer(folders, many=True).data
        })
        
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, 
                      status=status.HTTP_404_NOT_FOUND)
