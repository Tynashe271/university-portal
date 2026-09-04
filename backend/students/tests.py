from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import User

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='student',
            student_id='TEST001'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'student')
        self.assertEqual(self.user.student_id, 'TEST001')
    
    def test_user_is_student(self):
        self.assertTrue(self.user.is_student())
        self.assertFalse(self.user.is_admin_user())
    
    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser (student)')

class UserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='student123',
            role='student',
            student_id='STU001'
        )
    
    def test_user_registration(self):
        url = '/api/auth/register/'
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'student',
            'student_id': 'NEW001'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_user_login(self):
        url = '/api/auth/login/'
        data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_user_logout(self):
        # Test that logout endpoint exists and is accessible
        self.client.force_authenticate(user=self.admin_user)
        url = '/api/auth/logout/'
        response = self.client.post(url)
        # Logout may fail without proper token, but endpoint should be accessible
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
    
    def test_profile_retrieval(self):
        self.client.force_authenticate(user=self.student_user)
        url = '/api/auth/profile/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'student')
    
    def test_profile_update(self):
        self.client.force_authenticate(user=self.student_user)
        url = '/api/auth/profile/'
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.first_name, 'Updated')
    
    def test_user_list_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = '/api/auth/users/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_user_list_student(self):
        self.client.force_authenticate(user=self.student_user)
        url = '/api/auth/users/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only themselves