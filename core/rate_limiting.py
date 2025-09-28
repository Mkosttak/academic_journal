# core/rate_limiting.py
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
import hashlib
import json
import time
from functools import wraps

# Redis kontrolü
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: Redis not available. Rate limiting will use memory cache.")

User = get_user_model()

class RateLimiter:
    """Rate limiting sınıfı"""
    
    @staticmethod
    def get_client_ip(request):
        """Client IP adresini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_cache_key(prefix, identifier, action=None):
        """Rate limit cache key oluştur"""
        if action:
            return f"rate_limit:{prefix}:{identifier}:{action}"
        return f"rate_limit:{prefix}:{identifier}"
    
    @staticmethod
    def is_rate_limited(identifier, limit, window, action=None):
        """Rate limit kontrolü yap"""
        cache_key = RateLimiter.get_cache_key('general', identifier, action)
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= limit:
            return True
        
        # Request sayısını artır
        cache.set(cache_key, current_requests + 1, window)
        return False
    
    @staticmethod
    def get_remaining_requests(identifier, limit, window, action=None):
        """Kalan request sayısını döndür"""
        cache_key = RateLimiter.get_cache_key('general', identifier, action)
        current_requests = cache.get(cache_key, 0)
        return max(0, limit - current_requests)
    
    @staticmethod
    def reset_rate_limit(identifier, action=None):
        """Rate limit'i sıfırla"""
        cache_key = RateLimiter.get_cache_key('general', identifier, action)
        cache.delete(cache_key)

class BruteForceProtection:
    """Brute force saldırı koruması"""
    
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME = 900  # 15 dakika
    MAX_IP_ATTEMPTS = 10
    IP_LOCKOUT_TIME = 1800  # 30 dakika
    
    @staticmethod
    def get_login_attempts_key(username, ip):
        """Login attempt cache key"""
        return f"login_attempts:{username}:{ip}"
    
    @staticmethod
    def get_ip_attempts_key(ip):
        """IP attempt cache key"""
        return f"ip_attempts:{ip}"
    
    @staticmethod
    def is_account_locked(username, ip):
        """Hesap kilitli mi kontrol et"""
        attempts_key = BruteForceProtection.get_login_attempts_key(username, ip)
        attempts = cache.get(attempts_key, 0)
        return attempts >= BruteForceProtection.MAX_LOGIN_ATTEMPTS
    
    @staticmethod
    def is_ip_locked(ip):
        """IP kilitli mi kontrol et"""
        ip_key = BruteForceProtection.get_ip_attempts_key(ip)
        attempts = cache.get(ip_key, 0)
        return attempts >= BruteForceProtection.MAX_IP_ATTEMPTS
    
    @staticmethod
    def record_failed_login(username, ip):
        """Başarısız login kaydet"""
        # Username + IP için attempt sayısını artır
        attempts_key = BruteForceProtection.get_login_attempts_key(username, ip)
        attempts = cache.get(attempts_key, 0) + 1
        cache.set(attempts_key, attempts, BruteForceProtection.LOCKOUT_TIME)
        
        # IP için attempt sayısını artır
        ip_key = BruteForceProtection.get_ip_attempts_key(ip)
        ip_attempts = cache.get(ip_key, 0) + 1
        cache.set(ip_key, ip_attempts, BruteForceProtection.IP_LOCKOUT_TIME)
        
        # Log kaydet
        from core.monitoring import SecurityMonitor
        SecurityMonitor.log_suspicious_activity(
            None,
            'failed_login',
            {
                'username': username,
                'ip': ip,
                'attempts': attempts,
                'ip_attempts': ip_attempts
            }
        )
    
    @staticmethod
    def record_successful_login(username, ip):
        """Başarılı login kaydet ve attempt'leri temizle"""
        attempts_key = BruteForceProtection.get_login_attempts_key(username, ip)
        cache.delete(attempts_key)
    
    @staticmethod
    def get_lockout_time_remaining(username, ip):
        """Kilit süresinin ne kadar kaldığını döndür"""
        attempts_key = BruteForceProtection.get_login_attempts_key(username, ip)
        ttl = cache.ttl(attempts_key)
        return max(0, ttl) if ttl else 0

def rate_limit(limit=100, window=3600, per='ip', action=None):
    """Rate limiting decorator"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Identifier belirle
            if per == 'ip':
                identifier = RateLimiter.get_client_ip(request)
            elif per == 'user':
                if request.user.is_authenticated:
                    identifier = str(request.user.id)
                else:
                    identifier = RateLimiter.get_client_ip(request)
            else:
                identifier = RateLimiter.get_client_ip(request)
            
            # Rate limit kontrolü
            if RateLimiter.is_rate_limited(identifier, limit, window, action):
                remaining = RateLimiter.get_remaining_requests(identifier, limit, window, action)
                reset_time = timezone.now().timestamp() + window
                
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'limit': limit,
                        'remaining': remaining,
                        'reset_time': reset_time
                    }, status=429)
                else:
                    response = HttpResponse(
                        f"Rate limit exceeded. Try again in {window} seconds.",
                        status=429
                    )
                    return response
            
            # View'ı çalıştır
            response = view_func(request, *args, **kwargs)
            
            # Response header'larına rate limit bilgilerini ekle
            remaining = RateLimiter.get_remaining_requests(identifier, limit, window, action)
            response['X-RateLimit-Limit'] = str(limit)
            response['X-RateLimit-Remaining'] = str(remaining)
            response['X-RateLimit-Reset'] = str(int(timezone.now().timestamp() + window))
            
            return response
        return wrapper
    return decorator

def brute_force_protection(view_func):
    """Brute force koruması decorator'ı"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            username = request.POST.get('username', '')
            ip = RateLimiter.get_client_ip(request)
            
            # Brute force kontrolü
            if BruteForceProtection.is_account_locked(username, ip):
                lockout_time = BruteForceProtection.get_lockout_time_remaining(username, ip)
                return JsonResponse({
                    'error': 'Account temporarily locked due to too many failed login attempts',
                    'lockout_time': lockout_time
                }, status=423)
            
            if BruteForceProtection.is_ip_locked(ip):
                return JsonResponse({
                    'error': 'IP address temporarily locked due to suspicious activity'
                }, status=423)
        
        return view_func(request, *args, **kwargs)
    return wrapper

# Signal handlers
@receiver(user_login_failed)
def handle_failed_login(sender, credentials, request, **kwargs):
    """Başarısız login signal handler"""
    username = credentials.get('username', '')
    ip = RateLimiter.get_client_ip(request)
    BruteForceProtection.record_failed_login(username, ip)

# API Rate Limiting
class APIRateLimiter:
    """API endpoint'leri için rate limiting"""
    
    RATES = {
        'login': {'limit': 5, 'window': 300},  # 5 dakikada 5 login
        'register': {'limit': 3, 'window': 3600},  # 1 saatte 3 kayıt
        'password_reset': {'limit': 3, 'window': 3600},  # 1 saatte 3 şifre sıfırlama
        'api': {'limit': 1000, 'window': 3600},  # 1 saatte 1000 API çağrısı
        'upload': {'limit': 10, 'window': 3600},  # 1 saatte 10 dosya yükleme
    }
    
    @staticmethod
    def check_rate_limit(request, action='api'):
        """API rate limit kontrolü"""
        if action not in APIRateLimiter.RATES:
            return True, None
        
        rate_config = APIRateLimiter.RATES[action]
        identifier = RateLimiter.get_client_ip(request)
        
        if request.user.is_authenticated:
            identifier = f"user_{request.user.id}"
        
        is_limited = RateLimiter.is_rate_limited(
            identifier, 
            rate_config['limit'], 
            rate_config['window'], 
            action
        )
        
        if is_limited:
            remaining = RateLimiter.get_remaining_requests(
                identifier, 
                rate_config['limit'], 
                rate_config['window'], 
                action
            )
            return False, {
                'limit': rate_config['limit'],
                'remaining': remaining,
                'reset_time': timezone.now().timestamp() + rate_config['window']
            }
        
        return True, None

# Middleware
class RateLimitMiddleware:
    """Rate limiting middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # API endpoint'leri için rate limiting
        if request.path.startswith('/api/'):
            allowed, rate_info = APIRateLimiter.check_rate_limit(request, 'api')
            if not allowed:
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    **rate_info
                }, status=429)
        
        response = self.get_response(request)
        return response
