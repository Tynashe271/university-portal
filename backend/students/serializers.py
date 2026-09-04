from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import uuid
import re

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source='classroom.name', read_only=True, default=None)
    application_number = serializers.CharField(source='admission_application.application_number', read_only=True, default=None)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role',
                  'student_id', 'phone', 'date_of_birth', 'address', 'enrollment_date',
                  'profile_picture', 'email_verified', 'student_status', 'classroom',
                  'classroom_name', 'admission_application', 'application_number',
                  'blood_group', 'medical_conditions', 'allergies', 'medications',
                  'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
                  'previous_school', 'previous_grade']
        read_only_fields = ['id', 'enrollment_date', 'email_verified', 'admission_application']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 
                  'role', 'student_id', 'phone', 'date_of_birth', 'address']
    
    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and @/./+/-/_ characters.")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_student_id(self, value):
        if value and not re.match(r'^[A-Z]{2,4}\d{3,6}$', value):
            raise serializers.ValidationError("Student ID must be in format like 'STU00123' (2-4 letters followed by 3-6 numbers).")
        if value and User.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("A user with this student ID already exists.")
        return value
    
    def validate_phone(self, value):
        if value and not re.match(r'^\+?[\d\s-()]+$', value):
            raise serializers.ValidationError("Please enter a valid phone number.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Additional validation for role-specific fields
        if attrs.get('role') == 'student' and not attrs.get('student_id'):
            raise serializers.ValidationError({"student_id": "Student ID is required for student role."})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.generate_verification_token()
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError("Username is required.")
        return value
    
    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password is required.")
        return value

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'address', 'profile_picture']
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_phone(self, value):
        if value and not re.match(r'^\+?[\d\s-()]+$', value):
            raise serializers.ValidationError("Please enter a valid phone number.")
        return value

class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    
    def validate_token(self, value):
        if not User.objects.filter(email_verification_token=value).exists():
            raise serializers.ValidationError("Invalid or expired verification token.")
        return value

class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value