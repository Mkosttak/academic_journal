# core/admin.py
from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from core.monitoring import PerformanceMonitor
from core.backup import BackupManager
from core.backup import FullBackup
import json

@admin.register
class MonitoringAdmin:
    """Monitoring admin interface"""
    
    def monitoring_dashboard(self, request):
        """Monitoring dashboard view for admin"""
        if not request.user.is_staff:
            return HttpResponseRedirect(reverse('admin:index'))
        
        # Sistem metriklerini al
        system_metrics = PerformanceMonitor.get_system_metrics()
        db_health = PerformanceMonitor.check_database_health()
        cache_health = PerformanceMonitor.check_cache_health()
        
        # Backup bilgilerini al
        backup_manager = BackupManager()
        backup_dir = backup_manager.full_backup.backup_dir
        
        # Son yedekleri listele
        recent_backups = []
        try:
            import os
            if os.path.exists(backup_dir):
                backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
                backup_files.sort(key=lambda x: os.path.getctime(os.path.join(backup_dir, x)), reverse=True)
                recent_backups = backup_files[:5]  # Son 5 yedek
        except Exception:
            pass
        
        context = {
            'title': 'Monitoring Dashboard',
            'system_metrics': system_metrics,
            'db_health': db_health,
            'cache_health': cache_health,
            'recent_backups': recent_backups,
            'backup_dir': backup_dir,
        }
        
        return render(request, 'admin/monitoring_dashboard.html', context)
    
    def get_urls(self):
        """Admin URL'leri"""
        urls = [
            path('monitoring/', self.monitoring_dashboard, name='monitoring_dashboard'),
        ]
        return urls

# Admin site'a monitoring linki ekle
def add_monitoring_link(request):
    """Admin ana sayfasına monitoring linki ekle"""
    if request.user.is_staff:
        return {
            'monitoring_url': reverse('admin:monitoring_dashboard'),
        }
    return {}

# Admin template context'e ekle
admin.site.site_header = "Akademik Dergi Yönetim Paneli"
admin.site.site_title = "Admin Panel"
admin.site.index_title = "Yönetim Paneli"