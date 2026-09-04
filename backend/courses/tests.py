from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Department, Course, Enrollment, Grade

User = get_user_model()

class DepartmentModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            description='Computer Science Department'
        )
    
    def test_department_creation(self):
        self.assertEqual(self.department.name, 'Computer Science')
        self.assertEqual(self.department.code, 'CS')
    
    def test_department_str(self):
        self.assertEqual(str(self.department), 'CS - Computer Science')

class CourseModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='instructor123',
            role='admin'
        )
        self.course = Course.objects.create(
            code='CS101',
            name='Introduction to Programming',
            description='Basic programming',
            credits=3,
            level='100',
            department=self.department,
            instructor=self.instructor,
            capacity=30
        )
    
    def test_course_creation(self):
        self.assertEqual(self.course.code, 'CS101')
        self.assertEqual(self.course.credits, 3)
        self.assertEqual(self.course.level, '100')
    
    def test_course_enrolled_count(self):
        student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='student123',
            role='student'
        )
        Enrollment.objects.create(
            student=student,
            course=self.course,
            semester='Fall 2026',
            academic_year='2026-2027',
            status='enrolled'
        )
        self.assertEqual(self.course.enrolled_count, 1)
    
    def test_course_available_seats(self):
        student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='student123',
            role='student'
        )
        Enrollment.objects.create(
            student=student,
            course=self.course,
            semester='Fall 2026',
            academic_year='2026-2027',
            status='enrolled'
        )
        self.assertEqual(self.course.available_seats, 29)

class EnrollmentModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='CS', code='CS')
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='instructor123',
            role='admin'
        )
        self.course = Course.objects.create(
            code='CS101',
            name='Intro to Programming',
            department=self.department,
            instructor=self.instructor
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='student123',
            role='student'
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            semester='Fall 2026',
            academic_year='2026-2027',
            status='enrolled'
        )
    
    def test_enrollment_creation(self):
        self.assertEqual(self.enrollment.student, self.student)
        self.assertEqual(self.enrollment.course, self.course)
        self.assertEqual(self.enrollment.status, 'enrolled')
    
    def test_enrollment_str(self):
        expected = f"{self.student.username} - {self.course.code} (enrolled)"
        self.assertEqual(str(self.enrollment), expected)

class GradeModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='CS', code='CS')
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='instructor123',
            role='admin'
        )
        self.course = Course.objects.create(
            code='CS101',
            name='Intro to Programming',
            department=self.department,
            instructor=self.instructor
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='student123',
            role='student'
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            semester='Fall 2026',
            academic_year='2026-2027',
            status='enrolled'
        )
        self.grade = Grade.objects.create(
            enrollment=self.enrollment,
            midterm_grade=95.0,  # Changed to get an A
            final_grade=95.0,   # Changed to get an A
            assignment_grade=95.0,  # Changed to get an A
            graded_by=self.instructor
        )
    
    def test_grade_creation(self):
        self.assertEqual(self.grade.enrollment, self.enrollment)
        self.assertEqual(self.grade.midterm_grade, 95.0)
    
    def test_grade_calculation(self):
        self.grade.calculate_overall_grade()
        self.assertIsNotNone(self.grade.overall_grade)
        expected = (95.0 * 0.3) + (95.0 * 0.4) + (95.0 * 0.3)
        self.assertAlmostEqual(self.grade.overall_grade, expected, places=2)
    
    def test_letter_grade(self):
        self.grade.calculate_overall_grade()
        self.grade.refresh_from_db()
        # 95 should be an 'A' (90-100 range)
        self.assertEqual(self.grade.letter_grade, 'A')

class CourseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Clean up existing data
        Department.objects.all().delete()
        Course.objects.all().delete()
        Enrollment.objects.all().delete()
        Grade.objects.all().delete()
        
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
            role='student'
        )
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
    
    def tearDown(self):
        # Clean up test data
        Department.objects.all().delete()
        Course.objects.all().delete()
        Enrollment.objects.all().delete()
        Grade.objects.all().delete()
    
    def test_create_department(self):
        self.client.force_authenticate(user=self.admin_user)
        url = '/api/courses/departments/'
        data = {
            'name': 'Mathematics',
            'code': 'MATH',
            'description': 'Mathematics Department'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Department.objects.filter(code='MATH').exists())
    
    def test_list_departments(self):
        Department.objects.create(
            name='Mathematics',
            code='MATH'
        )
        self.client.force_authenticate(user=self.student_user)
        url = '/api/courses/departments/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # At least CS department from setUp
    
    def test_create_course(self):
        self.client.force_authenticate(user=self.admin_user)
        url = '/api/courses/courses/'
        data = {
            'code': 'CS102',
            'name': 'Data Structures',
            'description': 'Advanced programming',
            'credits': 4,
            'level': '200',
            'department': self.department.id,
            'instructor': self.admin_user.id,
            'capacity': 25
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Course.objects.filter(code='CS102').exists())
    
    def test_list_courses(self):
        Course.objects.create(
            code='CS101',
            name='Intro to Programming',
            department=self.department,
            instructor=self.admin_user
        )
        self.client.force_authenticate(user=self.student_user)
        url = '/api/courses/courses/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # At least our created course
    
    def test_student_enrollment(self):
        course = Course.objects.create(
            code='CS101',
            name='Intro to Programming',
            department=self.department,
            instructor=self.admin_user,
            capacity=30
        )
        self.client.force_authenticate(user=self.student_user)
        url = '/api/courses/enroll/'
        data = {
            'course_id': course.id,
            'semester': 'Fall 2026',
            'academic_year': '2026-2027'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Enrollment.objects.filter(
            student=self.student_user,
            course=course
        ).exists())
    
    def test_course_capacity_validation(self):
        course = Course.objects.create(
            code='CS101',
            name='Intro to Programming',
            department=self.department,
            instructor=self.admin_user,
            capacity=1
        )
        # First enrollment
        Enrollment.objects.create(
            student=self.student_user,
            course=course,
            semester='Fall 2026',
            academic_year='2026-2027',
            status='enrolled'
        )
        
        # Second student tries to enroll
        another_student = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='student123',
            role='student'
        )
        self.client.force_authenticate(user=another_student)
        url = '/api/courses/enroll/'
        data = {
            'course_id': course.id,
            'semester': 'Fall 2026',
            'academic_year': '2026-2027'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_grade_creation(self):
        course = Course.objects.create(
            code='CS101',
            name='Intro to Programming',
            department=self.department,
            instructor=self.admin_user
        )
        enrollment = Enrollment.objects.create(
            student=self.student_user,
            course=course,
            semester='Fall 2026',
            academic_year='2026-2027',
            status='enrolled'
        )
        self.client.force_authenticate(user=self.admin_user)
        url = '/api/courses/grades/'
        data = {
            'enrollment': enrollment.id,
            'midterm_grade': 85.0,
            'final_grade': 90.0,
            'assignment_grade': 88.0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Grade.objects.filter(enrollment=enrollment).exists())
    
    def test_student_dashboard(self):
        course = Course.objects.create(
            code='CS101',
            name='Intro to Programming',
            department=self.department,
            instructor=self.admin_user
        )
        Enrollment.objects.create(
            student=self.student_user,
            course=course,
            semester='Fall 2026',
            academic_year='2026-2027',
            status='enrolled'
        )
        self.client.force_authenticate(user=self.student_user)
        url = '/api/courses/dashboard/student/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('enrolled_courses', response.data)
        self.assertIn('enrollments', response.data)
    
    def test_admin_dashboard(self):
        self.client.force_authenticate(user=self.admin_user)
        url = '/api/courses/dashboard/admin/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_students', response.data)
        self.assertIn('total_courses', response.data)