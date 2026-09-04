from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import AdminPermission, SystemLog

User = get_user_model()

class AdminPermissionModelTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        self.permission = AdminPermission.objects.create(
            admin=self.admin_user,
            permission='manage_courses',
            granted_by=self.admin_user
        )
    
    def test_permission_creation(self):
        self.assertEqual(self.permission.admin, self.admin_user)
        self.assertEqual(self.permission.permission, 'manage_courses')
    
    def test_permission_str(self):
        expected = f"{self.admin_user.username} - manage_courses"
        self.assertEqual(str(self.permission), expected)

class SystemLogModelTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        self.log = SystemLog.objects.create(
            action='create',
            user=self.admin_user,
            model_name='Course',
            object_id=1,
            description='Created new course',
            ip_address='127.0.0.1'
        )
    
    def test_log_creation(self):
        self.assertEqual(self.log.action, 'create')
        self.assertEqual(self.log.user, self.admin_user)
        self.assertEqual(self.log.model_name, 'Course')
    
    def test_log_str(self):
        expected = f"{self.admin_user.username} - create - Course"
        self.assertEqual(str(self.log), expected)

class AdminAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.super_admin = User.objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='superadmin123',
            role='admin'
        )
        self.regular_admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='student123',
            role='student'
        )
    
    def tearDown(self):
        # Clean up test data
        AdminPermission.objects.all().delete()
        SystemLog.objects.all().delete()
    
    def test_create_permission(self):
        self.client.force_authenticate(user=self.super_admin)
        url = '/api/admin/permissions/'
        data = {
            'admin': self.regular_admin.id,
            'permission': 'manage_users'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AdminPermission.objects.filter(
            admin=self.regular_admin,
            permission='manage_users'
        ).exists())
    
    def test_list_permissions_admin(self):
        AdminPermission.objects.create(
            admin=self.regular_admin,
            permission='manage_courses',
            granted_by=self.super_admin
        )
        self.client.force_authenticate(user=self.super_admin)
        url = '/api/admin/permissions/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # At least our created permission
    
    def test_list_permissions_regular_admin(self):
        AdminPermission.objects.create(
            admin=self.regular_admin,
            permission='manage_courses',
            granted_by=self.super_admin
        )
        self.client.force_authenticate(user=self.regular_admin)
        url = '/api/admin/permissions/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # At least their own permissions
    
    def test_grant_permission(self):
        self.client.force_authenticate(user=self.super_admin)
        url = '/api/admin/permissions/grant/'
        data = {
            'admin_id': self.regular_admin.id,
            'permission': 'manage_grades'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AdminPermission.objects.filter(
            admin=self.regular_admin,
            permission='manage_grades'
        ).exists())
    
    def test_grant_permission_student_denied(self):
        self.client.force_authenticate(user=self.student_user)
        url = '/api/admin/permissions/grant/'
        data = {
            'admin_id': self.regular_admin.id,
            'permission': 'manage_grades'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_duplicate_permission_denied(self):
        AdminPermission.objects.create(
            admin=self.regular_admin,
            permission='manage_courses',
            granted_by=self.super_admin
        )
        self.client.force_authenticate(user=self.super_admin)
        url = '/api/admin/permissions/grant/'
        data = {
            'admin_id': self.regular_admin.id,
            'permission': 'manage_courses'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_system_logs_admin(self):
        SystemLog.objects.create(
            action='create',
            user=self.super_admin,
            model_name='Course',
            object_id=1,
            description='Test log'
        )
        self.client.force_authenticate(user=self.super_admin)
        url = '/api/admin/logs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # At least our created log
    
    def test_system_logs_student(self):
        SystemLog.objects.create(
            action='create',
            user=self.student_user,
            model_name='Enrollment',
            object_id=1,
            description='Student action'
        )
        self.client.force_authenticate(user=self.student_user)
        url = '/api/admin/logs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # At least their own logs
    
    def test_permission_deletion(self):
        permission = AdminPermission.objects.create(
            admin=self.regular_admin,
            permission='manage_users',
            granted_by=self.super_admin
        )
        self.client.force_authenticate(user=self.super_admin)
        url = f'/api/admin/permissions/{permission.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AdminPermission.objects.filter(id=permission.id).exists())
    
    def test_permission_update(self):
        permission = AdminPermission.objects.create(
            admin=self.regular_admin,
            permission='manage_courses',
            granted_by=self.super_admin
        )
        self.client.force_authenticate(user=self.super_admin)
        url = f'/api/admin/permissions/{permission.id}/'
        data = {
            'admin': self.regular_admin.id,
            'permission': 'manage_grades'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        permission.refresh_from_db()
        self.assertEqual(permission.permission, 'manage_grades')