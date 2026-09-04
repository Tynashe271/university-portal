# Frontend Integration Guide

This guide provides comprehensive examples for integrating the University Portal API with a frontend application.

## Table of Contents
1. [Setup](#setup)
2. [Authentication](#authentication)
3. [API Client](#api-client)
4. [Components](#components)
5. [Hooks](#hooks)
6. [State Management](#state-management)

## Setup

### Prerequisites
- Node.js 16+
- React 18+
- Axios

### Installation
```bash
npm install axios react-router-dom @reduxjs/toolkit react-redux
```

## Authentication

### Auth Context
```javascript
// src/context/AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.get('http://localhost:8000/api/auth/profile/', {
        headers: { Authorization: `Token ${token}` }
      })
      .then(response => {
        setUser(response.data);
        setLoading(false);
      })
      .catch(() => {
        localStorage.removeItem('token');
        setToken(null);
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await axios.post('http://localhost:8000/api/auth/login/', {
        username,
        password
      });
      
      const { token, user } = response.data;
      localStorage.setItem('token', token);
      setToken(token);
      setUser(user);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post('http://localhost:8000/api/auth/register/', userData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!token
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

## API Client

### Axios Configuration
```javascript
// src/utils/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### API Services
```javascript
// src/services/api.js
import api from '../utils/api';

export const authService = {
  login: (username, password) => 
    api.post('/auth/login/', { username, password }),
  
  register: (userData) => 
    api.post('/auth/register/', userData),
  
  logout: () => 
    api.post('/auth/logout/'),
  
  getProfile: () => 
    api.get('/auth/profile/'),
  
  updateProfile: (data) => 
    api.put('/auth/profile/', data),
};

export const courseService = {
  getCourses: (params = {}) => 
    api.get('/courses/courses/', { params }),
  
  getCourse: (id) => 
    api.get(`/courses/courses/${id}/`),
  
  enroll: (courseId, semester, academicYear) => 
    api.post('/courses/enroll/', {
      course_id: courseId,
      semester,
      academic_year: academicYear
    }),
  
  getEnrollments: () => 
    api.get('/courses/enrollments/'),
  
  getStudentDashboard: () => 
    api.get('/courses/dashboard/student/'),
};

export const materialService = {
  getCourseMaterials: (courseId) => 
    api.get(`/materials/courses/${courseId}/materials/`),
  
  uploadMaterial: (data) => 
    api.post('/materials/materials/', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  
  downloadMaterial: (materialId) => 
    api.get(`/materials/materials/${materialId}/download/`, {
      responseType: 'blob'
    }),
};

export const assignmentService = {
  getStudentAssignments: () => 
    api.get('/assignments/student/'),
  
  submitAssignment: (data) => 
    api.post('/assignments/submissions/', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  
  getSubmission: (id) => 
    api.get(`/assignments/submissions/${id}/`),
};

export const attendanceService = {
  getStudentAttendance: () => 
    api.get('/attendance/report/student/'),
  
  getCourseAttendance: (courseId) => 
    api.get(`/attendance/report/course/${courseId}/`),
};
```

## Components

### Login Component
```javascript
// src/components/auth/Login.js
import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(formData.username, formData.password);
    
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="login-container">
      <h2>University Portal Login</h2>
      {error && <div className="error">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username:</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label>Password:</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      
      <p>
        Don't have an account? <a href="/register">Register</a>
      </p>
    </div>
  );
};

export default Login;
```

### Student Dashboard Component
```javascript
// src/components/dashboard/StudentDashboard.js
import React, { useEffect, useState } from 'react';
import { courseService, assignmentService, attendanceService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const StudentDashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState({
    enrolledCourses: [],
    assignments: [],
    attendance: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [courses, assignments, attendance] = await Promise.all([
          courseService.getStudentDashboard(),
          assignmentService.getStudentAssignments(),
          attendanceService.getStudentAttendance()
        ]);

        setDashboardData({
          enrolledCourses: courses.data.enrolled_courses || [],
          assignments: assignments.data.assignments || [],
          attendance: attendance.data.attendance_summaries || []
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="dashboard">
      <h1>Welcome, {user?.first_name}!</h1>
      
      <div className="dashboard-grid">
        <div className="card">
          <h2>Enrolled Courses</h2>
          <ul>
            {dashboardData.enrolledCourses.map(course => (
              <li key={course.id}>
                {course.code} - {course.name}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="card">
          <h2>Assignments</h2>
          <ul>
            {dashboardData.assignments.map(assignment => (
              <li key={assignment.id}>
                {assignment.title} - Due: {new Date(assignment.due_date).toLocaleDateString()}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="card">
          <h2>Attendance</h2>
          <ul>
            {dashboardData.attendance.map(summary => (
              <li key={summary.id}>
                {summary.course_code}: {summary.attendance_percentage}%
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
```

### Course List Component
```javascript
// src/components/courses/CourseList.js
import React, { useEffect, useState } from 'react';
import { courseService } from '../../services/api';

const CourseList = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await courseService.getCourses();
        setCourses(response.data);
      } catch (error) {
        console.error('Error fetching courses:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, []);

  const handleEnroll = async (courseId) => {
    try {
      await courseService.enroll(courseId, 'Fall 2026', '2026-2027');
      alert('Successfully enrolled!');
      // Refresh courses
      const response = await courseService.getCourses();
      setCourses(response.data);
    } catch (error) {
      alert('Enrollment failed: ' + (error.response?.data?.error || 'Unknown error'));
    }
  };

  const filteredCourses = courses.filter(course =>
    course.name.toLowerCase().includes(filter.toLowerCase()) ||
    course.code.toLowerCase().includes(filter.toLowerCase())
  );

  if (loading) return <div>Loading courses...</div>;

  return (
    <div className="course-list">
      <h2>Available Courses</h2>
      
      <input
        type="text"
        placeholder="Search courses..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        className="search-input"
      />
      
      <div className="courses-grid">
        {filteredCourses.map(course => (
          <div key={course.id} className="course-card">
            <h3>{course.code} - {course.name}</h3>
            <p>{course.description}</p>
            <div className="course-details">
              <span>Credits: {course.credits}</span>
              <span>Level: {course.level}</span>
              <span>Available Seats: {course.available_seats}</span>
            </div>
            <button onClick={() => handleEnroll(course.id)}>
              Enroll
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CourseList;
```

## Hooks

### useApi Hook
```javascript
// src/hooks/useApi.js
import { useState, useEffect } from 'react';

export const useApi = (apiFunction, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await apiFunction();
        setData(response.data);
        setError(null);
      } catch (err) {
        setError(err);
        setData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, dependencies);

  return { data, loading, error, refetch: () => fetchData() };
};
```

### usePagination Hook
```javascript
// src/hooks/usePagination.js
import { useState } from 'react';

export const usePagination = (itemsPerPage = 10) => {
  const [currentPage, setCurrentPage] = useState(1);

  const paginate = (items) => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return items.slice(startIndex, startIndex + itemsPerPage);
  };

  const totalPages = (totalItems) => Math.ceil(totalItems / itemsPerPage);

  const nextPage = () => {
    setCurrentPage(prev => prev + 1);
  };

  const prevPage = () => {
    setCurrentPage(prev => Math.max(prev - 1, 1));
  };

  const goToPage = (page) => {
    setCurrentPage(Math.max(1, page));
  };

  return {
    currentPage,
    setCurrentPage,
    paginate,
    totalPages,
    nextPage,
    prevPage,
    goToPage
  };
};
```

## State Management

### Redux Store Setup
```javascript
// src/store/index.js
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import courseReducer from './slices/courseSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    courses: courseReducer,
  },
});

// src/store/slices/authSlice.js
import { createSlice } from '@reduxjs/toolkit';

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token'),
  },
  reducers: {
    setCredentials: (state, action) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.isAuthenticated = true;
      localStorage.setItem('token', action.payload.token);
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      localStorage.removeItem('token');
    },
  },
});

export const { setCredentials, logout } = authSlice.actions;
export default authSlice.reducer;
```

## Error Handling

### Error Boundary
```javascript
// src/components/ErrorBoundary.js
import React, { Component } from 'react';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

## Styling

### CSS Example
```css
/* src/styles/dashboard.css */
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card h2 {
  margin-top: 0;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  background: #007bff;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background: #0056b3;
}

.error {
  color: #dc3545;
  padding: 10px;
  background: #f8d7da;
  border-radius: 4px;
  margin-bottom: 15px;
}
```

## Environment Configuration

### .env file
```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_FRONTEND_URL=http://localhost:3000
```

### Environment Setup
```javascript
// src/config.js
const config = {
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  frontendUrl: process.env.REACT_APP_FRONTEND_URL || 'http://localhost:3000',
};

export default config;
```

This guide provides a comprehensive foundation for building a React frontend that integrates with the University Portal API. Adjust the examples according to your specific requirements and design preferences.