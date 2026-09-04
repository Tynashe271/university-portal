# University Portal Backend

A comprehensive Django REST API backend for a university student and admin portal system.

## Features

### User Management
- User registration and authentication
- Role-based access control (Student/Admin)
- Profile management
- Token-based authentication

### Course Management
- Department management
- Course creation and management
- Course capacity tracking
- Course status management (active/inactive/archived)
- Course prerequisites

### Enrollment System
- Student course enrollment
- Enrollment status tracking
- Semester and academic year management
- Capacity validation

### Grade Management
- Grade assignment and management
- Automatic grade calculation
- Letter grade conversion
- Grade history tracking

### Admin Features
- Admin permission management
- System logging and auditing
- Admin dashboard with statistics
- User management capabilities

## Tech Stack

- **Backend Framework**: Django 6.0.3
- **API Framework**: Django REST Framework 3.18.0
- **Database**: SQLite (default) / PostgreSQL (configurable)
- **Authentication**: Token Authentication + Session Authentication
- **CORS**: django-cors-headers

## Project Structure

```
university-portal/
├── config/                 # Main Django project configuration
│   ├── settings.py        # Project settings
│   ├── urls.py           # Main URL routing
│   └── wsgi.py           # WSGI configuration
├── students/             # Student management app
│   ├── models.py         # User model and student data
│   ├── serializers.py    # API serializers
│   ├── views.py          # API views
│   └── urls.py           # Student URLs
├── courses/              # Course management app
│   ├── models.py         # Course, Department, Enrollment, Grade models
│   ├── serializers.py    # API serializers
│   ├── views.py          # API views
│   └── urls.py           # Course URLs
├── admins/               # Admin management app
│   ├── models.py         # Admin permissions and system logs
│   ├── serializers.py    # API serializers
│   ├── views.py          # API views
│   └── urls.py           # Admin URLs
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── test_api.py          # API testing script
```

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup Steps

1. **Clone the repository**
   ```bash
   cd university-portal
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000`

### Root Endpoint
The root endpoint (`http://localhost:8000/`) provides API information:
```json
{
  "message": "University Portal API",
  "version": "1.0",
  "endpoints": {
    "authentication": "/api/auth/",
    "courses": "/api/courses/",
    "admin": "/api/admin/",
    "admin_panel": "/admin/"
  },
  "documentation": "See README.md for API documentation"
}
```

## Database Configuration

### SQLite (Default)
The project is configured to use SQLite by default for development.

### PostgreSQL
To use PostgreSQL, update the `DATABASES` setting in `config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'university_portal',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile

### User Management
- `GET /api/auth/users/` - List all users (admin only)
- `GET /api/auth/users/<id>/` - Get user details
- `PUT /api/auth/users/<id>/` - Update user
- `DELETE /api/auth/users/<id>/` - Delete user

### Departments
- `GET /api/courses/departments/` - List all departments
- `POST /api/courses/departments/` - Create department (admin)
- `GET /api/courses/departments/<id>/` - Get department details
- `PUT /api/courses/departments/<id>/` - Update department (admin)
- `DELETE /api/courses/departments/<id>/` - Delete department (admin)

### Courses
- `GET /api/courses/courses/` - List all courses
- `POST /api/courses/courses/` - Create course (admin)
- `GET /api/courses/courses/<id>/` - Get course details
- `PUT /api/courses/courses/<id>/` - Update course (admin)
- `DELETE /api/courses/courses/<id>/` - Delete course (admin)

### Enrollments
- `GET /api/courses/enrollments/` - List enrollments
- `POST /api/courses/enrollments/` - Create enrollment (admin)
- `POST /api/courses/enroll/` - Student self-enrollment
- `GET /api/courses/enrollments/<id>/` - Get enrollment details
- `PUT /api/courses/enrollments/<id>/` - Update enrollment (admin)
- `DELETE /api/courses/enrollments/<id>/` - Delete enrollment (admin)

### Grades
- `GET /api/courses/grades/` - List grades
- `POST /api/courses/grades/` - Create grade (admin)
- `GET /api/courses/grades/<id>/` - Get grade details
- `PUT /api/courses/grades/<id>/` - Update grade (admin)

### Admin
- `GET /api/admin/permissions/` - List admin permissions
- `POST /api/admin/permissions/` - Create permission (admin)
- `POST /api/admin/permissions/grant/` - Grant permission to admin
- `GET /api/admin/logs/` - View system logs (admin)

### Dashboards
- `GET /api/courses/dashboard/student/` - Student dashboard
- `GET /api/courses/dashboard/admin/` - Admin dashboard

## Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - Email address
- `first_name` - First name
- `last_name` - Last name
- `role` - Student or Admin
- `student_id` - Student ID number
- `phone` - Phone number
- `date_of_birth` - Date of birth
- `address` - Address
- `enrollment_date` - Enrollment date
- `profile_picture` - Profile picture

### Departments Table
- `id` - Primary key
- `name` - Department name
- `code` - Department code
- `description` - Department description

### Courses Table
- `id` - Primary key
- `code` - Course code
- `name` - Course name
- `description` - Course description
- `credits` - Credit hours
- `level` - Course level (100-500)
- `department` - Foreign key to Department
- `instructor` - Foreign key to User
- `capacity` - Maximum students
- `status` - Active/Inactive/Archived
- `prerequisite` - Foreign key to self

### Enrollments Table
- `id` - Primary key
- `student` - Foreign key to User
- `course` - Foreign key to Course
- `status` - Pending/Enrolled/Completed/Dropped/Failed
- `enrollment_date` - Enrollment date
- `completion_date` - Completion date
- `semester` - Semester
- `academic_year` - Academic year

### Grades Table
- `id` - Primary key
- `enrollment` - Foreign key to Enrollment
- `midterm_grade` - Midterm grade
- `final_grade` - Final grade
- `assignment_grade` - Assignment grade
- `overall_grade` - Calculated overall grade
- `letter_grade` - Letter grade (A-F)
- `comments` - Grade comments
- `graded_by` - Foreign key to User
- `graded_date` - Grading date

## Authentication

The API uses Token Authentication. Include the token in the Authorization header:

```
Authorization: Token <your_token_here>
```

### Example Usage

#### 1. Register a new user
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newstudent",
    "email": "newstudent@university.edu",
    "password": "password123",
    "password2": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "student_id": "STU002"
  }'
```

#### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Response:
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@university.edu",
    "role": "admin"
  },
  "token": "4b098b60d7588c543559ea2a46e5a3ba5fbbb694",
  "message": "Login successful"
}
```

#### 3. Get courses (authenticated)
```bash
curl -X GET http://localhost:8000/api/courses/courses/ \
  -H "Authorization: Token 4b098b60d7588c543559ea2a46e5a3ba5fbbb694"
```

#### 4. Enroll in a course (student)
```bash
curl -X POST http://localhost:8000/api/courses/enroll/ \
  -H "Authorization: Token <student_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": 1,
    "semester": "Fall 2026",
    "academic_year": "2026-2027"
  }'
```

#### 5. Get student dashboard
```bash
curl -X GET http://localhost:8000/api/courses/dashboard/student/ \
  -H "Authorization: Token <student_token>"
```

## Testing

Run the provided test script to verify API functionality:

```bash
python test_api.py
```

This script tests:
- User registration
- Login functionality
- Course listing
- Department listing
- Student enrollment
- Dashboard endpoints

## Default Users

The system comes with pre-configured users:

- **Admin**: Username: `admin`, Password: `admin123`
- **Student**: Username: `student1`, Password: `student123`
- **Test Student**: Username: `test_student`, Password: `testpass123`

## Development

### Running Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

### Accessing Django Admin
Navigate to `http://localhost:8000/admin/` to access the Django admin interface.

## Security Considerations

- Change the `SECRET_KEY` in production
- Set `DEBUG = False` in production
- Configure proper `ALLOWED_HOSTS`
- Use environment variables for sensitive data
- Implement rate limiting for API endpoints
- Use HTTPS in production

## Future Enhancements

- Email verification for registration
- Password reset functionality
- File upload for course materials
- Real-time notifications
- Advanced reporting and analytics
- Mobile API endpoints
- Integration with payment systems
- Calendar integration
- Chat/messaging system

## License

This project is provided as-is for educational purposes.

## Support

For issues and questions, please refer to the Django and Django REST Framework documentation.