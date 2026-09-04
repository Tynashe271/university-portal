"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from .monitoring import HealthCheck

def api_root(request):
    return JsonResponse({
        'message': 'University Portal API',
        'version': '2.0',
        'endpoints': {
            'authentication': '/api/auth/',
            'courses': '/api/courses/',
            'admin': '/api/admin/',
            'materials': '/api/materials/',
            'announcements': '/api/announcements/',
            'attendance': '/api/attendance/',
            'schedule': '/api/schedule/',
            'assignments': '/api/assignments/',
            'forums': '/api/forums/',
            'password_reset': '/api/auth/password-reset/',
            'health': '/api/health/',
            'metrics': '/api/metrics/',
            'admissions': '/api/admissions/',
            'fees': '/api/fees/',
            'parent_communication': '/api/parent-communication/',
            'library': '/api/library/',
            'transportation': '/api/transportation/',
            'inventory': '/api/inventory/',
            'cafeteria': '/api/cafeteria/',
            'examinations': '/api/examinations/',
            'wellbeing': '/api/wellbeing/',
            'staff': '/api/staff/',
            'admin_panel': '/admin/'
        },
        'documentation': 'See README.md for API documentation'
    })

def health_check(request):
    health_status = HealthCheck.overall_health()
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)

def metrics(request):
    from .monitoring import APIMonitor
    metrics_data = APIMonitor.get_metrics()
    return JsonResponse(metrics_data)

urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('api/auth/', include('students.urls')),
    path('api/auth/password-reset/', include('django_rest_passwordreset.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/admin/', include('admins.urls')),
    path('api/materials/', include('materials.urls')),
    path('api/announcements/', include('announcements.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/schedule/', include('schedule.urls')),
    path('api/assignments/', include('assignments.urls')),
    path('api/forums/', include('forums.urls')),
    path('api/health/', health_check),
    path('api/metrics/', metrics),
    path('api/admissions/', include('admissions.urls')),
    path('api/fees/', include('fees.urls')),
    path('api/parent-communication/', include('parent_communication.urls')),
    path('api/library/', include('library.urls')),
    path('api/transportation/', include('transportation.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/cafeteria/', include('cafeteria.urls')),
    path('api/examinations/', include('examinations.urls')),
    path('api/wellbeing/', include('wellbeing.urls')),
    path('api/staff/', include('staff.urls')),
]
