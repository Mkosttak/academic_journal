# core/monitoring.py
import logging
import time
import psutil
import os
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.db import connection
from django.core.cache import cache
import json

# Logger yapılandırması
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Performans izleme sınıfı"""
    
    @staticmethod
    def log_slow_queries():
        """Yavaş sorguları logla"""
        if hasattr(settings, 'DEBUG') and settings.DEBUG:
            for query in connection.queries:
                if float(query['time']) > 0.1:  # 100ms'den yavaş sorgular
                    logger.warning(f"Slow query detected: {query['sql'][:100]}... (Time: {query['time']}s)")
    
    @staticmethod
    def get_system_metrics():
        """Sistem metriklerini al"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'timestamp': timezone.now().isoformat()
        }
    
    @staticmethod
    def check_database_health():
        """Veritabanı sağlığını kontrol et"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    @staticmethod
    def check_cache_health():
        """Cache sağlığını kontrol et"""
        try:
            cache.set('health_check', 'ok', 10)
            result = cache.get('health_check')
            return result == 'ok'
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False

class ErrorMonitor:
    """Hata izleme sınıfı"""
    
    @staticmethod
    def log_error(error, request=None, user=None):
        """Hataları logla ve admin'e bildir"""
        error_data = {
            'error': str(error),
            'timestamp': timezone.now().isoformat(),
            'user': str(user) if user else 'Anonymous',
            'path': request.path if request else 'Unknown',
            'method': request.method if request else 'Unknown',
            'ip': request.META.get('REMOTE_ADDR') if request else 'Unknown'
        }
        
        logger.error(f"Error occurred: {json.dumps(error_data)}")
        
        # Kritik hatalar için admin'e e-posta gönder
        if settings.DEBUG == False:  # Sadece production'da
            ErrorMonitor.send_error_notification(error_data)
    
    @staticmethod
    def send_error_notification(error_data):
        """Admin'e hata bildirimi gönder"""
        try:
            subject = f"Site Hatası - {error_data['timestamp']}"
            message = f"""
            Hata Detayları:
            - Hata: {error_data['error']}
            - Kullanıcı: {error_data['user']}
            - Sayfa: {error_data['path']}
            - IP: {error_data['ip']}
            - Zaman: {error_data['timestamp']}
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin[1] for admin in settings.ADMINS],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")

class SecurityMonitor:
    """Güvenlik izleme sınıfı"""
    
    @staticmethod
    def log_suspicious_activity(request, activity_type, details=None):
        """Şüpheli aktiviteleri logla"""
        suspicious_data = {
            'activity_type': activity_type,
            'ip': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'path': request.path,
            'timestamp': timezone.now().isoformat(),
            'details': details or {}
        }
        
        logger.warning(f"Suspicious activity detected: {json.dumps(suspicious_data)}")
    
    @staticmethod
    def check_brute_force_attempts(ip, username):
        """Brute force saldırılarını kontrol et"""
        key = f"login_attempts_{ip}_{username}"
        attempts = cache.get(key, 0)
        
        if attempts >= 5:  # 5 başarısız deneme
            SecurityMonitor.log_suspicious_activity(
                None, 
                'brute_force_attempt',
                {'ip': ip, 'username': username, 'attempts': attempts}
            )
            return True
        
        cache.set(key, attempts + 1, 300)  # 5 dakika cache
        return False

# Middleware for automatic monitoring
class MonitoringMiddleware:
    """Otomatik izleme middleware'i"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Request öncesi kontroller
        if not PerformanceMonitor.check_database_health():
            logger.error("Database health check failed before request")
        
        response = self.get_response(request)
        
        # Request sonrası metrikler
        process_time = time.time() - start_time
        
        # Yavaş sayfaları logla
        if process_time > 2.0:  # 2 saniyeden yavaş
            logger.warning(f"Slow page detected: {request.path} took {process_time:.2f}s")
        
        # Yavaş sorguları logla
        PerformanceMonitor.log_slow_queries()
        
        return response

# Management command for monitoring
class MonitoringCommands:
    """Monitoring komutları"""
    
    @staticmethod
    def generate_performance_report():
        """Performans raporu oluştur"""
        metrics = PerformanceMonitor.get_system_metrics()
        db_health = PerformanceMonitor.check_database_health()
        cache_health = PerformanceMonitor.check_cache_health()
        
        report = {
            'timestamp': timezone.now().isoformat(),
            'system_metrics': metrics,
            'database_health': db_health,
            'cache_health': cache_health,
            'status': 'healthy' if all([db_health, cache_health, metrics['cpu_percent'] < 80]) else 'warning'
        }
        
        logger.info(f"Performance report: {json.dumps(report)}")
        return report
