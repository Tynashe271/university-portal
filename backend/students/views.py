from rest_framework import generics, status, permissions, throttling
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer, UserProfileUpdateSerializer, EmailVerificationSerializer, ResendVerificationSerializer, BehavioralIncidentSerializer
from .models import BehavioralIncident
from config.permissions import IsAdminUser

User = get_user_model()

class RegisterThrottle(throttling.UserRateThrottle):
    scope = 'register'

class LoginThrottle(throttling.UserRateThrottle):
    scope = 'login'

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    throttle_classes = [RegisterThrottle]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([LoginThrottle])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        
        if user:
            # Check if email is verified (warning only, not blocking)
            email_verified = user.email_verified
            
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            response_data = {
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'Login successful'
            }
            
            if not email_verified:
                response_data['warning'] = 'Email not verified. Please verify your email for full access.'
            
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except:
        return Response({'error': 'Error during logout'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserProfileUpdateSerializer

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Disable default pagination for this view

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            queryset = User.objects.all()
            role = self.request.query_params.get('role')
            if role:
                queryset = queryset.filter(role=role)
            return queryset.order_by('-enrollment_date')
        else:
            return User.objects.filter(id=user.id)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return User.objects.all()
        else:
            return User.objects.filter(id=user.id)

    def perform_destroy(self, instance):
        # A user may only view/edit their own record via this endpoint (see
        # get_queryset); deleting an account is admin-only regardless.
        if not self.request.user.is_admin_user():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins can delete accounts.")
        instance.delete()

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    serializer = EmailVerificationSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        
        try:
            user = User.objects.get(email_verification_token=token)
            user.email_verified = True
            user.email_verification_token = None
            user.save()
            
            return Response({
                'message': 'Email verified successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid verification token'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resend_verification(request):
    serializer = ResendVerificationSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            if user.email_verified:
                return Response({
                    'message': 'Email already verified'
                }, status=status.HTTP_200_OK)
            
            # Generate new token
            token = user.generate_verification_token()
            
            # Send verification email
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
            
            send_mail(
                'Verify Your Email - University Portal',
                f'Please verify your email by visiting: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'Verification email sent successfully'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User with this email not found'
            }, status=status.HTTP_404_NOT_FOUND)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BehavioralIncidentListCreateView(generics.ListCreateAPIView):
    """Discipline module — the model already existed, unwired to any API
    (no serializer/view/url at all) until now."""
    queryset = BehavioralIncident.objects.select_related('student', 'reported_by').all()
    serializer_class = BehavioralIncidentSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        student = self.request.query_params.get('student')
        severity = self.request.query_params.get('severity')
        if student:
            queryset = queryset.filter(student=student)
        if severity:
            queryset = queryset.filter(severity=severity)
        return queryset

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)


class BehavioralIncidentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BehavioralIncident.objects.all()
    serializer_class = BehavioralIncidentSerializer
    permission_classes = [IsAdminUser]
