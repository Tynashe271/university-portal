from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin_user()

class IsStudentUser(permissions.BasePermission):
    """
    Custom permission to only allow student users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_student()

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users can access any object
        if request.user.is_admin_user():
            return True
        
        # Check if the user is the owner of the object
        if hasattr(obj, 'student'):
            return obj.student == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'uploaded_by'):
            return obj.uploaded_by == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False

class IsEnrolledOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow enrolled students or admins to access course-related content.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin users can access any course content
        if request.user.is_admin_user():
            return True
        
        # Check if student is enrolled in the course
        if request.user.is_student():
            if hasattr(obj, 'course'):
                from courses.models import Enrollment
                return Enrollment.objects.filter(
                    student=request.user,
                    course=obj.course,
                    status='enrolled'
                ).exists()
            elif hasattr(obj, 'enrollment'):
                return obj.enrollment.student == request.user
        
        return False

class IsVerifiedUser(permissions.BasePermission):
    """
    Custom permission to only allow users with verified email addresses.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.email_verified