import uuid
import logging
import time
from django.utils.deprecation import MiddlewareMixin
from .monitoring import APIMonitor, ErrorTracker

logger = logging.getLogger('api')

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all API requests with unique request IDs and timing information.
    """
    
    def process_request(self, request):
        # Generate unique request ID
        request.id = str(uuid.uuid4())
        request.start_time = time.time()
        
        # Log request details
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'request_id': request.id,
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
                'ip_address': self.get_client_ip(request),
            }
        )
        
        return None
    
    def process_response(self, request, response):
        # Calculate request duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response['X-Request-ID'] = request.id
            response['X-Response-Time'] = f"{duration:.3f}s"
            
            # Track API metrics
            APIMonitor.track_request(request, response, duration)
            
            # Log response details
            logger.info(
                f"Request completed: {request.method} {request.path} - {response.status_code}",
                extra={
                    'request_id': request.id,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration': duration,
                    'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
                }
            )
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class ErrorLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log errors and exceptions.
    """
    
    def process_exception(self, request, exception):
        # Track error with monitoring
        ErrorTracker.track_error(
            exception,
            request=request,
            context={
                'view': str(request.resolver_match.view_name) if hasattr(request, 'resolver_match') else None,
                'args': request.resolver_match.args if hasattr(request, 'resolver_match') else None,
                'kwargs': request.resolver_match.kwargs if hasattr(request, 'resolver_match') else None,
            }
        )
        
        logger.error(
            f"Exception occurred: {str(exception)}",
            extra={
                'request_id': getattr(request, 'id', None),
                'method': request.method if request else None,
                'path': request.path if request else None,
                'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
                'exception_type': type(exception).__name__,
            },
            exc_info=True
        )
        return None

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor performance metrics.
    """
    
    def process_response(self, request, response):
        try:
            # Track database queries only if DEBUG is enabled
            from django.conf import settings
            if settings.DEBUG:
                from django.db import connection
                queries = connection.queries
                if queries:
                    total_time = sum(float(q['time']) for q in queries)
                    query_count = len(queries)
                    
                    logger.info(
                        f"Database queries: {query_count}, Total time: {total_time:.3f}s",
                        extra={
                            'query_count': query_count,
                            'total_time': total_time,
                            'avg_time': total_time / query_count if query_count > 0 else 0
                        }
                    )
        except Exception as e:
            logger.error(f"Error in performance monitoring: {e}")
        
        return response