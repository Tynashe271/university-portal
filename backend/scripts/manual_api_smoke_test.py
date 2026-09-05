# Manual smoke test — not part of the automated suite (`manage.py test`
# only discovers real Django TestCases under each app's tests.py/tests/).
# This hits a *running* server directly over HTTP, so it needs:
#   1. `pip install requests` (deliberately not in requirements.txt —
#      nothing in the app itself imports it)
#   2. the backend running separately: `python manage.py runserver 8001`
# then: `python scripts/manual_api_smoke_test.py`
import requests

BASE_URL = "http://localhost:8001/api"

def test_registration():
    print("Testing User Registration...")
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": "test_student",
        "email": "test@university.edu",
        "password": "testpass123",
        "password2": "testpass123",
        "first_name": "Test",
        "last_name": "Student",
        "role": "student",
        "student_id": "TEST001"
    }
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_login():
    print("\nTesting Login...")
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_courses(token):
    print("\nTesting Courses List...")
    url = f"{BASE_URL}/courses/courses/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_departments(token):
    print("\nTesting Departments List...")
    url = f"{BASE_URL}/courses/departments/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_enrollment(token):
    print("\nTesting Student Enrollment...")
    url = f"{BASE_URL}/courses/enroll/"
    headers = {"Authorization": f"Token {token}"}
    data = {
        "course_id": 1,
        "semester": "Fall 2026",
        "academic_year": "2026-2027"
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_student_login():
    print("\nTesting Student Login...")
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "test_student",
        "password": "testpass123"
    }
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_student_dashboard(token):
    print("\nTesting Student Dashboard...")
    url = f"{BASE_URL}/courses/dashboard/student/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_admin_dashboard(token):
    print("\nTesting Admin Dashboard...")
    url = f"{BASE_URL}/courses/dashboard/admin/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    try:
        # Test registration
        reg_result = test_registration()
        
        # Test admin login
        login_result = test_login()
        admin_token = login_result.get('token')
        
        if admin_token:
            # Test authenticated endpoints with admin
            test_courses(admin_token)
            test_departments(admin_token)
            test_admin_dashboard(admin_token)
        else:
            print("Admin login failed, skipping admin tests")
        
        # Test student login and enrollment
        student_login_result = test_student_login()
        student_token = student_login_result.get('token')
        
        if student_token:
            test_enrollment(student_token)
            test_student_dashboard(student_token)
        else:
            print("Student login failed, skipping enrollment test")
            
    except Exception as e:
        print(f"Error: {e}")