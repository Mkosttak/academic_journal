from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Count

class CustomAdminSite(AdminSite):
    site_header = "📚 Akademik Dergi Yönetim Paneli"
    site_title = "Akademik Dergi Admin"
    index_title = "Yönetim Paneli Ana Sayfa"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='admin_dashboard'),
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
