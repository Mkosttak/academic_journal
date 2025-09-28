# core/cache_utils.py
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.conf import settings
import hashlib
import json
from functools import wraps
import time

class CacheManager:
    """Gelişmiş cache yönetimi sınıfı"""
    
    @staticmethod
    def get_cache_key(prefix, *args, **kwargs):
        """Cache key oluştur"""
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_string = f"{prefix}:{hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()}"
        return key_string
    
    @staticmethod
    def cache_result(timeout=300, cache_alias='default', key_prefix=''):
        """Fonksiyon sonuçlarını cache'le decorator'ı"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Cache key oluştur
                cache_key = CacheManager.get_cache_key(
                    f"{key_prefix}:{func.__name__}", 
                    *args, 
                    **kwargs
                )
                
                # Cache'den kontrol et
                result = cache.get(cache_key, cache_alias)
                if result is not None:
                    return result
                
                # Fonksiyonu çalıştır ve sonucu cache'le
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout, cache_alias)
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def invalidate_pattern(pattern):
        """Belirli pattern'e uyan cache'leri temizle"""
        try:
            # Redis için pattern temizleme
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            keys = redis_conn.keys(f"*{pattern}*")
            if keys:
                redis_conn.delete(*keys)
        except Exception as e:
            print(f"Cache invalidation error: {e}")
    
    @staticmethod
    def warm_cache():
        """Cache'i önceden doldur"""
        from articles.models import Makale, DergiSayisi
        from users.models import User
        
        # Popüler makaleleri cache'le
        popular_articles = Makale.objects.filter(
            goster_makaleler_sayfasinda=True
        ).select_related('dergi_sayisi').prefetch_related('yazarlar').order_by(
            '-goruntulenme_sayisi'
        )[:10]
        
        cache.set('popular_articles', list(popular_articles.values()), 3600)
        
        # Dergi sayılarını cache'le
        recent_issues = DergiSayisi.objects.filter(
            yayinlandi_mi=True
        ).select_related().prefetch_related('makaleler').order_by(
            '-yil', '-ay', '-sayi_no'
        )[:20]
        
        cache.set('recent_issues', list(recent_issues.values()), 1800)
        
        # Kullanıcı istatistiklerini cache'le
        user_stats = {
            'total_users': User.objects.count(),
            'total_editors': User.objects.filter(is_editor=True).count(),
            'total_articles': Makale.objects.count(),
            'published_articles': Makale.objects.filter(goster_makaleler_sayfasinda=True).count(),
        }
        
        cache.set('user_stats', user_stats, 1800)

def cache_page(timeout=300, cache_alias='default'):
    """Sayfa cache decorator'ı"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Cache key oluştur
            cache_key = f"page:{request.path}:{request.GET.urlencode()}"
            
            # Cache'den kontrol et
            response = cache.get(cache_key, cache_alias)
            if response is not None:
                return response
            
            # View'ı çalıştır
            response = view_func(request, *args, **kwargs)
            
            # Sadece GET istekleri ve başarılı yanıtları cache'le
            if request.method == 'GET' and response.status_code == 200:
                cache.set(cache_key, response, timeout, cache_alias)
            
            return response
        return wrapper
    return decorator

def cache_template_fragment(timeout=300, cache_alias='default'):
    """Template fragment cache decorator'ı"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Template fragment key oluştur
            fragment_key = make_template_fragment_key(
                func.__name__, 
                args, 
                kwargs
            )
            
            # Cache'den kontrol et
            result = cache.get(fragment_key, cache_alias)
            if result is not None:
                return result
            
            # Fonksiyonu çalıştır
            result = func(*args, **kwargs)
            
            # Sonucu cache'le
            cache.set(fragment_key, result, timeout, cache_alias)
            return result
        return wrapper
    return decorator

class QueryCache:
    """Veritabanı sorgularını cache'le"""
    
    @staticmethod
    def cache_queryset(queryset, cache_key, timeout=300, cache_alias='default'):
        """QuerySet'i cache'le"""
        result = cache.get(cache_key, cache_alias)
        if result is not None:
            return result
        
        # QuerySet'i evaluate et ve cache'le
        data = list(queryset.values())
        cache.set(cache_key, data, timeout, cache_alias)
        return data
    
    @staticmethod
    def get_or_create_cached(queryset, cache_key, timeout=300, cache_alias='default'):
        """Cache'den al veya oluştur"""
        result = cache.get(cache_key, cache_alias)
        if result is not None:
            return result
        
        # QuerySet'i çalıştır ve cache'le
        data = list(queryset)
        cache.set(cache_key, data, timeout, cache_alias)
        return data