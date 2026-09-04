import time
import logging
from django.core.cache import cache
from django.db import connection
from django.conf import settings

logger = logging.getLogger('api')

class APIMonitor:
    """
    Class for monitoring API performance and usage
    """
    
    @staticmethod
    def track_request(request, response, duration):
        """
        Track API request metrics
        """
        try:
            endpoint = request.path
            method = request.method
            status_code = response.status_code
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None
            
            # Cache key for metrics
            cache_key = f"api_metrics:{endpoint}:{method}"
            
            # Get existing metrics
            metrics = cache.get(cache_key, {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'total_duration': 0,
                'avg_duration': 0,
                'status_codes': {},
                'last_accessed': None
            })
            
            # Update metrics
            metrics['total_requests'] += 1
            metrics['total_duration'] += duration
            metrics['avg_duration'] = metrics['total_duration'] / metrics['total_requests']
            metrics['last_accessed'] = time.time()
            
            if 200 <= status_code < 400:
                metrics['successful_requests'] += 1
            else:
                metrics['failed_requests'] += 1
            
            # Track status codes
            metrics['status_codes'][status_code] = metrics['status_codes'].get(status_code, 0) + 1
            
            # Cache for 1 hour
            cache.set(cache_key, metrics, 3600)
            
            # Log slow requests
            if duration > 1.0:  # Log requests taking more than 1 second
                logger.warning(
                    f"Slow request detected: {method} {endpoint} took {duration:.2f}s",
                    extra={
                        'endpoint': endpoint,
                        'method': method,
                        'duration': duration,
                        'user_id': user_id
                    }
                )
            
        except Exception as e:
            logger.error(f"Error tracking request metrics: {e}")

    @staticmethod
    def get_metrics(endpoint=None, method=None):
        """
        Get API metrics for a specific endpoint or all endpoints
        """
        try:
            if endpoint and method:
                cache_key = f"api_metrics:{endpoint}:{method}"
                return cache.get(cache_key, {})
            else:
                # Get all metrics (this would need a more sophisticated implementation)
                return {}
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {}

    @staticmethod
    def track_database_query():
        """
        Track database query performance
        """
        try:
            from django.db import connection
            from django.conf import settings
            
            # Only track if DEBUG is enabled
            if settings.DEBUG:
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
                    
                    # Alert on slow queries
                    if total_time > 0.5:  # More than 500ms
                        logger.warning(
                            f"Slow database queries detected: {query_count} queries took {total_time:.3f}s",
                            extra={
                                'query_count': query_count,
                                'total_time': total_time,
                                'queries': queries
                            }
                        )
        except Exception as e:
            logger.error(f"Error tracking database queries: {e}")

class PerformanceMonitor:
    """
    Class for monitoring application performance
    """
    
    @staticmethod
    def track_memory_usage():
        """
        Track memory usage
        """
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            logger.info(
                f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB",
                extra={
                    'memory_mb': memory_info.rss / 1024 / 1024,
                    'memory_percent': process.memory_percent()
                }
            )
            
            # Alert on high memory usage
            if process.memory_percent() > 80:
                logger.warning(
                    f"High memory usage: {process.memory_percent():.2f}%",
                    extra={'memory_percent': process.memory_percent()}
                )
                
        except ImportError:
            pass  # psutil not installed, skip memory monitoring
        except Exception as e:
            logger.error(f"Error tracking memory usage: {e}")

    @staticmethod
    def track_cpu_usage():
        """
        Track CPU usage
        """
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            
            logger.info(
                f"CPU usage: {cpu_percent}%",
                extra={'cpu_percent': cpu_percent}
            )
            
            # Alert on high CPU usage
            if cpu_percent > 80:
                logger.warning(
                    f"High CPU usage: {cpu_percent}%",
                    extra={'cpu_percent': cpu_percent}
                )
                
        except ImportError:
            pass  # psutil not installed, skip CPU monitoring
        except Exception as e:
            logger.error(f"Error tracking CPU usage: {e}")

class ErrorTracker:
    """
    Class for tracking and managing errors
    """
    
    @staticmethod
    def track_error(error, request=None, context=None):
        """
        Track errors with context
        """
        try:
            error_type = type(error).__name__
            error_message = str(error)
            
            # Cache key for error tracking
            cache_key = f"error_tracker:{error_type}"
            
            # Get existing error count
            error_count = cache.get(cache_key, 0)
            error_count += 1
            
            # Cache for 1 hour
            cache.set(cache_key, error_count, 3600)
            
            # Log error with context
            logger.error(
                f"Error tracked: {error_type} - {error_message}",
                extra={
                    'error_type': error_type,
                    'error_message': error_message,
                    'error_count': error_count,
                    'request_path': request.path if request else None,
                    'request_method': request.method if request else None,
                    'user_id': request.user.id if request and hasattr(request, 'user') and request.user.is_authenticated else None,
                    'context': context
                },
                exc_info=True
            )
            
            # Alert on frequent errors
            if error_count > 10:  # More than 10 errors of this type in the last hour
                logger.critical(
                    f"High error rate detected: {error_type} occurred {error_count} times in the last hour",
                    extra={
                        'error_type': error_type,
                        'error_count': error_count
                    }
                )
            
        except Exception as e:
            logger.error(f"Error tracking error: {e}")

    @staticmethod
    def get_error_stats():
        """
        Get error statistics
        """
        try:
            # This would need a more sophisticated implementation
            # to get all error types from cache
            return {}
        except Exception as e:
            logger.error(f"Error getting error stats: {e}")
            return {}

class HealthCheck:
    """
    Class for health checks
    """
    
    @staticmethod
    def check_database():
        """
        Check database connectivity
        """
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True, "Database connection OK"
        except Exception as e:
            return False, f"Database connection failed: {str(e)}"
    
    @staticmethod
    def check_cache():
        """
        Check cache connectivity
        """
        try:
            cache.set('health_check', 'test', 10)
            result = cache.get('health_check')
            if result == 'test':
                return True, "Cache connection OK"
            return False, "Cache read/write failed"
        except Exception as e:
            return False, f"Cache connection failed: {str(e)}"
    
    @staticmethod
    def check_redis():
        """
        Check Redis connectivity
        """
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            return True, "Redis connection OK"
        except ImportError:
            return True, "Redis client not installed (optional)"
        except Exception as e:
            return False, f"Redis connection failed: {str(e)}"
    
    @staticmethod
    def overall_health():
        """
        Perform overall health check
        """
        health_status = {
            'status': 'healthy',
            'checks': {},
            'timestamp': time.time()
        }
        
        # Database check
        db_ok, db_message = HealthCheck.check_database()
        health_status['checks']['database'] = {
            'status': 'ok' if db_ok else 'error',
            'message': db_message
        }
        
        # Cache check
        cache_ok, cache_message = HealthCheck.check_cache()
        health_status['checks']['cache'] = {
            'status': 'ok' if cache_ok else 'error',
            'message': cache_message
        }
        
        # Redis check (optional)
        redis_ok, redis_message = HealthCheck.check_redis()
        health_status['checks']['redis'] = {
            'status': 'ok' if redis_ok else 'warning',
            'message': redis_message
        }
        
        # Overall status (only critical checks)
        critical_checks = ['database', 'cache']
        if any(health_status['checks'][check]['status'] == 'error' for check in critical_checks):
            health_status['status'] = 'unhealthy'
        
        return health_status