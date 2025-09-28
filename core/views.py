# core/views.py
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import UserPassesTestMixin
from core.monitoring import PerformanceMonitor, ErrorMonitor
import json

class MonitoringDashboardView(UserPassesTestMixin, TemplateView):
    """Monitoring dashboard"""
    template_name = 'core/monitoring_dashboard.html'
    login_url = '/kullanici/giris/'
    
    def test_func(self):
        """Sadece staff kullanıcıları erişebilir"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Yetkisiz erişim durumunda 403 sayfasını göster"""
        return render(self.request, '403.html', status=403)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Sistem metriklerini al
        context['system_metrics'] = PerformanceMonitor.get_system_metrics()
        context['db_health'] = PerformanceMonitor.check_database_health()
        context['cache_health'] = PerformanceMonitor.check_cache_health()
        
        return context

@csrf_exempt
def monitoring_api(request):
    """Monitoring API endpoint"""
    # Staff kontrolü
    if not request.user.is_staff:
        return JsonResponse({
            'status': 'error',
            'message': 'Yetkisiz erişim. Sadece yönetici kullanıcıları erişebilir.'
        }, status=403)
    
    if request.method == 'GET':
        try:
            # Performans raporu oluştur
            report = PerformanceMonitor.generate_performance_report()
            
            return JsonResponse({
                'status': 'success',
                'data': report
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)