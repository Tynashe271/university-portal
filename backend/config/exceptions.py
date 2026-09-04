from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging
import traceback

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Log the exception with more details
        request = context.get('request')
        view = context.get('view')
        
        logger.error(
            f"Exception in {view.__class__.__name__ if view else 'Unknown View'}: {str(exc)}",
            extra={
                'request_method': request.method if request else None,
                'request_path': request.path if request else None,
                'user': str(request.user) if request and hasattr(request, 'user') else None,
                'status_code': response.status_code
            },
            exc_info=True
        )
        
        # Customize the error response
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': str(exc),
            'details': response.data if hasattr(response, 'data') else None,
            'timestamp': None
        }
        
        # Add specific error messages based on status code
        if response.status_code == 400:
            custom_response_data['message'] = 'Bad request - Invalid input data'
        elif response.status_code == 401:
            custom_response_data['message'] = 'Authentication required'
        elif response.status_code == 403:
            custom_response_data['message'] = 'Permission denied'
        elif response.status_code == 404:
            custom_response_data['message'] = 'Resource not found'
        elif response.status_code == 405:
            custom_response_data['message'] = 'Method not allowed'
        elif response.status_code == 429:
            custom_response_data['message'] = 'Rate limit exceeded'
            custom_response_data['retry_after'] = getattr(exc, 'retry_after', None)
        elif response.status_code == 500:
            custom_response_data['message'] = 'Internal server error'
            custom_response_data['details'] = 'An unexpected error occurred. Please try again later.'
        
        # Add request ID for tracking
        if request:
            custom_response_data['request_id'] = getattr(request, 'id', None)
        
        response.data = custom_response_data
    
    return response

class APIException(Exception):
    """Base API exception class"""
    def __init__(self, message, status_code=400, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class ValidationException(APIException):
    """Exception for validation errors"""
    def __init__(self, message, field_errors=None):
        if field_errors:
            super().__init__(message, status_code=400)
            self.details = field_errors
        else:
            super().__init__(message, status_code=400)

class AuthenticationException(APIException):
    """Exception for authentication errors"""
    def __init__(self, message="Authentication failed"):
        super().__init__(message, status_code=401)

class PermissionException(APIException):
    """Exception for permission errors"""
    def __init__(self, message="Permission denied"):
        super().__init__(message, status_code=403)

class NotFoundException(APIException):
    """Exception for resource not found errors"""
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)

class RateLimitException(APIException):
    """Exception for rate limit errors"""
    def __init__(self, message="Rate limit exceeded", retry_after=None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after