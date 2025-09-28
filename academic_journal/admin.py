from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from django.contrib import messages

class CustomAdminSite(AdminSite):
    site_header = "📚 Akademik Dergi Yönetim Paneli"
    site_title = "Akademik Dergi Admin"
    index_title = "Yönetim Paneli Ana Sayfa"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='admin_dashboard'),
            path('monitoring/', self.admin_view(self.monitoring_view), name='monitoring_dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """Özel admin dashboard görünümü"""
        from articles.models import Makale, DergiSayisi, DergiIcerigi, Yazar
        from users.models import User
        from pages.models import IletisimFormu
        
        context = {
            'title': 'Admin Dashboard',
            'stats': {
                'total_users': User.objects.count(),
                'total_articles': Makale.objects.count(),
                'published_articles': Makale.objects.filter(goster_makaleler_sayfasinda=True).count(),
                'draft_articles': Makale.objects.filter(goster_makaleler_sayfasinda=False).count(),
                'total_journals': DergiSayisi.objects.count(),
                'published_journals': DergiSayisi.objects.filter(yayinlandi_mi=True).count(),
                'total_contents': DergiIcerigi.objects.count(),
                'published_contents': DergiIcerigi.objects.filter(yayinda_mi=True).count(),
                'total_authors': Yazar.objects.count(),
                'pending_messages': IletisimFormu.objects.filter(cevaplandi=False).count(),
                'total_messages': IletisimFormu.objects.count(),
            },
            'recent_articles': Makale.objects.select_related('dergi_sayisi').order_by('-olusturulma_tarihi')[:5],
            'recent_messages': IletisimFormu.objects.order_by('-olusturulma_tarihi')[:5],
            'recent_users': User.objects.order_by('-date_joined')[:5],
        }
        return render(request, 'admin/dashboard.html', context)
    
    def monitoring_view(self, request):
        """Monitoring dashboard view for admin"""
        # Staff kontrolü
        if not request.user.is_staff:
            from django.shortcuts import render
            return render(request, '403.html', status=403)
        
        from core.monitoring import PerformanceMonitor
        from core.backup import BackupManager
        import os
        
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
            if os.path.exists(backup_dir):
                backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
                backup_files.sort(key=lambda x: os.path.getctime(os.path.join(backup_dir, x)), reverse=True)
                recent_backups = backup_files[:5]  # Son 5 yedek
        except Exception:
            pass
        
        # Action handling
        action = request.GET.get('action')
        if action == 'backup':
            try:
                backup_path = backup_manager.run_scheduled_backup()
                messages.success(request, f'Yedekleme başarıyla oluşturuldu: {os.path.basename(backup_path)}')
            except Exception as e:
                messages.error(request, f'Yedekleme hatası: {str(e)}')
        elif action == 'cleanup':
            try:
                backup_manager.full_backup.cleanup_old_backups()
                messages.success(request, 'Eski yedekler temizlendi.')
            except Exception as e:
                messages.error(request, f'Temizleme hatası: {str(e)}')
        
        context = {
            'title': 'Monitoring Dashboard',
            'system_metrics': system_metrics,
            'db_health': db_health,
            'cache_health': cache_health,
            'recent_backups': recent_backups,
            'backup_dir': backup_dir,
        }
        
        return render(request, 'admin/monitoring_dashboard.html', context)
    
    def index(self, request, extra_context=None):
        """Ana sayfa için özel context ekle"""
        extra_context = extra_context or {}
        
        # İstatistikleri ekle
        from articles.models import Makale, DergiSayisi, DergiIcerigi, Yazar
        from users.models import User
        from pages.models import IletisimFormu
        
        extra_context.update({
            'quick_stats': {
                'users': User.objects.count(),
                'articles': Makale.objects.count(),
                'journals': DergiSayisi.objects.count(),
                'messages': IletisimFormu.objects.filter(cevaplandi=False).count(),
            },
            'recent_activity': {
                'recent_articles': Makale.objects.select_related('dergi_sayisi').order_by('-olusturulma_tarihi')[:3],
                'recent_messages': IletisimFormu.objects.order_by('-olusturulma_tarihi')[:3],
            }
        })
        
        return super().index(request, extra_context)

# Özel admin site'ı oluştur
admin_site = CustomAdminSite(name='custom_admin')

# Tüm modelleri özel admin site'a kaydet
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from users.models import User
from users.admin import CustomUserAdmin
from articles.models import Makale, DergiSayisi, DergiIcerigi, Yazar
from articles.admin import MakaleAdmin, DergiSayisiAdmin, DergiIcerigiAdmin, YazarAdmin
from pages.models import IletisimFormu
from pages.admin import IletisimFormuAdmin

admin_site.register(User, CustomUserAdmin)
admin_site.register(Group)
admin_site.register(Makale, MakaleAdmin)
admin_site.register(DergiSayisi, DergiSayisiAdmin)
admin_site.register(DergiIcerigi, DergiIcerigiAdmin)
admin_site.register(Yazar, YazarAdmin)
admin_site.register(IletisimFormu, IletisimFormuAdmin)
