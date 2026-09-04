from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import Department, Course, Enrollment, Grade
from .serializers import DepartmentSerializer, CourseSerializer, EnrollmentSerializer, GradeSerializer
from students.models import User

class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return Department.objects.all()
        return Department.objects.all()

class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Course.objects.all()
        
        status_filter = self.request.query_params.get('status', None)
        department = self.request.query_params.get('department', None)
        level = self.request.query_params.get('level', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if department:
            queryset = queryset.filter(department_id=department)
        if level:
            queryset = queryset.filter(level=level)
            
        if user.is_student():
            return queryset.filter(status='active')
        return queryset

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

class EnrollmentListCreateView(generics.ListCreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return Enrollment.objects.all()
        elif user.is_student():
            return Enrollment.objects.filter(student=user)
        return Enrollment.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_student():
            serializer.save(student=user)
        elif user.is_admin_user():
            serializer.save()

class EnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return Enrollment.objects.all()
        elif user.is_student():
            return Enrollment.objects.filter(student=user)
        return Enrollment.objects.none()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def enroll_student(request):
    course_id = request.data.get('course_id')
    semester = request.data.get('semester', 'Fall 2026')
    academic_year = request.data.get('academic_year', '2026-2027')
    
    try:
        course = Course.objects.get(id=course_id)
        user = request.user
        
        if not user.is_student():
            return Response({'error': 'Only students can enroll in courses'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        if course.available_seats <= 0:
            return Response({'error': 'Course is full'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        existing_enrollment = Enrollment.objects.filter(
            student=user, 
            course=course, 
            semester=semester, 
            academic_year=academic_year
        ).first()
        
        if existing_enrollment:
            return Response({'error': 'Already enrolled in this course'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        enrollment = Enrollment.objects.create(
            student=user,
            course=course,
            semester=semester,
            academic_year=academic_year,
            status='enrolled'
        )
        
        return Response(EnrollmentSerializer(enrollment).data, 
                      status=status.HTTP_201_CREATED)
        
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, 
                      status=status.HTTP_404_NOT_FOUND)

class GradeListCreateView(generics.ListCreateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return Grade.objects.all()
        elif user.is_student():
            return Grade.objects.filter(enrollment__student=user)
        return Grade.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save(graded_by=user)

class GradeDetailView(generics.RetrieveUpdateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return Grade.objects.all()
        elif user.is_student():
            return Grade.objects.filter(enrollment__student=user)
        return Grade.objects.none()
    
    def perform_update(self, serializer):
        grade = serializer.save()
        grade.calculate_overall_grade()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_dashboard(request):
    user = request.user
    
    if user.is_student():
        enrollments = Enrollment.objects.filter(student=user)
        courses = [e.course for e in enrollments if e.status == 'enrolled']
        grades = Grade.objects.filter(enrollment__student=user)
        
        return Response({
            'user': user.username,
            'enrolled_courses': CourseSerializer(courses, many=True).data,
            'enrollments': EnrollmentSerializer(enrollments, many=True).data,
            'grades': GradeSerializer(grades, many=True).data,
        })
    
    return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_dashboard(request):
    user = request.user
    
    if user.is_admin_user():
        total_students = User.objects.filter(role='student').count()
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()
        active_enrollments = Enrollment.objects.filter(status='enrolled').count()
        
        return Response({
            'total_students': total_students,
            'total_courses': total_courses,
            'total_enrollments': total_enrollments,
            'active_enrollments': active_enrollments,
        })
    
    return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
