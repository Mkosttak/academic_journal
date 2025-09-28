# articles/admin.py

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
import csv
from .models import Makale, DergiSayisi, Yazar, DergiIcerigi # Yeni model de import edin

# YENİ: Yazar modelini admin paneline kaydedelim
@admin.register(Yazar)
class YazarAdmin(admin.ModelAdmin):
    list_display = ('isim_soyisim', 'user_hesabi', 'makale_sayisi')
    search_fields = ('isim_soyisim', 'user_hesabi__username', 'user_hesabi__email', 'user_hesabi__first_name', 'user_hesabi__last_name')
    list_filter = ('user_hesabi__is_editor', 'user_hesabi__is_chief_editor')
    autocomplete_fields = ['user_hesabi']
    readonly_fields = ('makale_sayisi',)
    ordering = ['isim_soyisim']
    
    fieldsets = (
        ('Yazar Bilgileri', {
            'fields': ('isim_soyisim', 'user_hesabi')
        }),
        ('İstatistikler', {
            'fields': ('makale_sayisi',),
            'classes': ('collapse',)
        })
    )
    
    def makale_sayisi(self, obj):
        return obj.makaleler.count()
    makale_sayisi.short_description = 'Makale Sayısı'


@admin.register(Makale)
class MakaleAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'get_yazarlar_display', 'dergi_sayisi', 'goster_makaleler_sayfasinda', 'status_badge', 'goruntulenme_sayisi', 'olusturulma_tarihi')
    list_filter = ('goster_makaleler_sayfasinda', 'dergi_sayisi', 'olusturulma_tarihi', 'yazarlar', 'admin_notu_okundu')
    list_editable = ('goster_makaleler_sayfasinda',)
    search_fields = ('baslik', 'aciklama', 'anahtar_kelimeler', 'yazarlar__isim_soyisim', 'yazarlar__user_hesabi__username', 'yazarlar__user_hesabi__email')
    prepopulated_fields = {'slug': ('baslik',)}
    filter_horizontal = ('yazarlar',)
    readonly_fields = ('goruntulenme_sayisi', 'olusturulma_tarihi', 'guncellenme_tarihi')
    ordering = ['-olusturulma_tarihi']
    list_per_page = 25
    list_max_show_all = 100
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('baslik', 'slug', 'aciklama', 'anahtar_kelimeler')
        }),
        ('Dosya ve Yayın', {
            'fields': ('pdf_dosyasi', 'goster_makaleler_sayfasinda', 'siralama')
        }),
        ('Yazarlar ve Dergi', {
            'fields': ('yazarlar', 'dergi_sayisi'),
            'classes': ('wide',)
        }),
        ('Admin Notları', {
            'fields': ('admin_notu', 'admin_notu_okundu'),
            'classes': ('collapse',)
        }),
        ('İstatistikler', {
            'fields': ('goruntulenme_sayisi', 'olusturulma_tarihi', 'guncellenme_tarihi'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['make_published', 'make_draft', 'mark_as_read', 'export_to_csv']
    
    def status_badge(self, obj):
        from django.utils.html import format_html
        if obj.goster_makaleler_sayfasinda:
            return format_html('<span style="color: green; font-weight: bold;">✓ Yayında</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">📝 Taslak</span>')
    status_badge.short_description = 'Durum'
    
    def make_published(self, request, queryset):
        updated = queryset.update(goster_makaleler_sayfasinda=True)
        self.message_user(request, f'{updated} makale yayına alındı.')
    make_published.short_description = 'Seçili makaleleri yayına al'
    
    def make_draft(self, request, queryset):
        updated = queryset.update(goster_makaleler_sayfasinda=False)
        self.message_user(request, f'{updated} makale taslağa çevrildi.')
    make_draft.short_description = 'Seçili makaleleri taslağa çevir'
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(admin_notu_okundu=True)
        self.message_user(request, f'{updated} makalenin admin notu okundu olarak işaretlendi.')
    mark_as_read.short_description = 'Admin notlarını okundu olarak işaretle'
    
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="makaleler.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Başlık', 'Yazarlar', 'Dergi Sayısı', 'Durum', 'Görüntülenme', 'Oluşturulma Tarihi'])
        
        for makale in queryset:
            yazarlar = ', '.join([yazar.isim_soyisim for yazar in makale.yazarlar.all()])
            durum = 'Yayında' if makale.goster_makaleler_sayfasinda else 'Taslak'
            writer.writerow([
                makale.baslik,
                yazarlar,
                str(makale.dergi_sayisi) if makale.dergi_sayisi else '',
                durum,
                makale.goruntulenme_sayisi,
                makale.olusturulma_tarihi.strftime('%d.%m.%Y %H:%M')
            ])
        
        return response
    export_to_csv.short_description = 'Seçili makaleleri CSV olarak dışa aktar'
    
    def get_queryset(self, request):
        """Admin listesinde görüntülenecek verileri optimize et"""
        return super().get_queryset(request).select_related('dergi_sayisi').prefetch_related('yazarlar')
    
    def changelist_view(self, request, extra_context=None):
        """Admin listesine ek istatistikler ekle"""
        extra_context = extra_context or {}
        
        # İstatistikleri hesapla
        total_articles = Makale.objects.count()
        published_articles = Makale.objects.filter(goster_makaleler_sayfasinda=True).count()
        draft_articles = total_articles - published_articles
        total_views = sum(Makale.objects.values_list('goruntulenme_sayisi', flat=True))
        
        extra_context.update({
            'stats': {
                'total_articles': total_articles,
                'published_articles': published_articles,
                'draft_articles': draft_articles,
                'total_views': total_views,
            }
        })
        
        return super().changelist_view(request, extra_context)


@admin.register(DergiSayisi)
class DergiSayisiAdmin(admin.ModelAdmin):
    list_display = ('get_tarih_format', 'get_cilt_sayi_format', 'status_badge', 'makale_sayisi', 'icerik_sayisi', 'ordering_actions')
    search_fields = ('yil', 'cilt', 'sayi_no', 'slug')
    list_filter = ('yil', 'ay', 'cilt', 'yayinlandi_mi', 'yayinlanma_secimi', 'olusturulma_tarihi')
    readonly_fields = ('yayinlandi_mi', 'makale_sayisi', 'icerik_sayisi', 'olusturulma_tarihi')
    ordering = ['-yil', '-ay', '-sayi_no']
    prepopulated_fields = {'slug': ('yil', 'ay', 'cilt', 'sayi_no')}
    list_per_page = 20
    
    fieldsets = (
        ('Dergi Bilgileri', {
            'fields': ('yil', 'ay', 'cilt', 'sayi_no', 'slug', 'kapak_gorseli')
        }),
        ('Yayınlanma', {
            'fields': ('yayinlanma_secimi', 'yayinlandi_mi'),
            'classes': ('collapse',)
        }),
        ('İstatistikler', {
            'fields': ('makale_sayisi', 'icerik_sayisi', 'olusturulma_tarihi'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['publish_journal', 'unpublish_journal', 'export_journals_to_csv']
    
    def status_badge(self, obj):
        from django.utils.html import format_html
        if obj.yayinlandi_mi:
            return format_html('<span style="color: green; font-weight: bold;">✓ Yayında</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">📝 Taslak</span>')
    status_badge.short_description = 'Durum'
    
    def icerik_sayisi(self, obj):
        return obj.icerikler.count()
    icerik_sayisi.short_description = 'İçerik Sayısı'
    
    def publish_journal(self, request, queryset):
        updated = queryset.update(yayinlandi_mi=True)
        self.message_user(request, f'{updated} dergi sayısı yayına alındı.')
    publish_journal.short_description = 'Seçili dergi sayılarını yayına al'
    
    def unpublish_journal(self, request, queryset):
        updated = queryset.update(yayinlandi_mi=False)
        self.message_user(request, f'{updated} dergi sayısı yayından kaldırıldı.')
    unpublish_journal.short_description = 'Seçili dergi sayılarını yayından kaldır'
    
    def export_journals_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="dergi_sayilari.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Yıl', 'Ay', 'Cilt', 'Sayı', 'Durum', 'Makale Sayısı', 'İçerik Sayısı', 'Oluşturulma Tarihi'])
        
        for dergi in queryset:
            durum = 'Yayında' if dergi.yayinlandi_mi else 'Taslak'
            ay_adi = dict(dergi.AYLAR)[dergi.ay]
            writer.writerow([
                dergi.yil,
                ay_adi,
                dergi.cilt,
                dergi.sayi_no,
                durum,
                dergi.makale_sayisi,
                dergi.icerik_sayisi,
                dergi.olusturulma_tarihi.strftime('%d.%m.%Y %H:%M')
            ])
        
        return response
    export_journals_to_csv.short_description = 'Seçili dergi sayılarını CSV olarak dışa aktar'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('siralama/<int:dergi_sayisi_id>/', 
                 self.admin_site.admin_view(self.article_ordering_view),
                 name='articles_dergisayisi_ordering'),
        ]
        return custom_urls + urls
    
    def article_ordering_view(self, request, dergi_sayisi_id):
        from django.shortcuts import render
        from .models import DergiSayisi, Makale, DergiIcerigi
        
        try:
            dergi_sayisi = DergiSayisi.objects.get(id=dergi_sayisi_id)
            makaleler = Makale.objects.filter(dergi_sayisi=dergi_sayisi).order_by('siralama', '-olusturulma_tarihi')
            icerikler = DergiIcerigi.objects.filter(dergi_sayisi=dergi_sayisi).order_by('siralama', '-olusturulma_tarihi')
            
            # Tüm içerikleri birleştir ve sırala (makaleler + içerikler)
            all_items = []
            
            # Makaleleri ekle
            for makale in makaleler:
                all_items.append({
                    'id': makale.id,
                    'type': 'makale',
                    'siralama': makale.siralama,
                    'obj': makale
                })
            
            # İçerikleri ekle
            for icerik in icerikler:
                all_items.append({
                    'id': icerik.id,
                    'type': 'icerik',
                    'siralama': icerik.siralama,
                    'obj': icerik
                })
            
            # Sıralamaya göre sırala
            all_items.sort(key=lambda x: x['siralama'])
            
            context = {
                'title': f'İçerik Sıralaması - {dergi_sayisi}',
                'dergi_sayisi': dergi_sayisi,
                'makaleler': makaleler,
                'icerikler': icerikler,
                'all_items': all_items,
                'opts': self.model._meta,
                'has_change_permission': self.has_change_permission(request),
            }
            return render(request, 'admin/articles/dergisayisi/ordering.html', context)
        except DergiSayisi.DoesNotExist:
            from django.http import Http404
            raise Http404("Dergi sayısı bulunamadı.")
    
    def ordering_actions(self, obj):
        """Sıralama butonunu gösterir"""
        if obj.makale_sayisi > 0:
            from django.urls import reverse
            from django.utils.html import format_html
            url = reverse('admin:articles_dergisayisi_ordering', args=[obj.pk])
            return format_html(
                '<a href="{}" class="button" style="background: #007cba; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; font-size: 12px;">📝 Sırala</a>',
                url
            )
        return '-'
    
    ordering_actions.short_description = 'Sıralama'


@admin.register(DergiIcerigi)
class DergiIcerigiAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'dergi_sayisi', 'yayinda_mi', 'status_badge', 'icerik_turu', 'olusturan_admin', 'goruntulenme_sayisi', 'olusturulma_tarihi')
    list_filter = ('yayinda_mi', 'icerik_turu', 'dergi_sayisi', 'olusturan_admin', 'olusturulma_tarihi')
    search_fields = ('baslik', 'aciklama', 'anahtar_kelimeler')
    prepopulated_fields = {'slug': ('baslik',)}
    readonly_fields = ('olusturan_admin', 'goruntulenme_sayisi', 'olusturulma_tarihi', 'guncellenme_tarihi')
    list_editable = ('yayinda_mi',)
    ordering = ['-olusturulma_tarihi']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('baslik', 'slug', 'dergi_sayisi', 'icerik_turu')
        }),
        ('İçerik', {
            'fields': ('aciklama', 'pdf_dosyasi', 'anahtar_kelimeler')
        }),
        ('Yayın Durumu', {
            'fields': ('yayinda_mi', 'siralama')
        }),
        ('Yazarlar', {
            'fields': ('yazarlar',),
            'classes': ('wide',)
        }),
        ('Sistem Bilgileri', {
            'fields': ('olusturan_admin', 'goruntulenme_sayisi', 'olusturulma_tarihi', 'guncellenme_tarihi'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['make_published', 'make_draft']
    
    def status_badge(self, obj):
        from django.utils.html import format_html
        if obj.yayinda_mi:
            return format_html('<span style="color: green; font-weight: bold;">✓ Yayında</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">📝 Taslak</span>')
    status_badge.short_description = 'Durum'
    
    def make_published(self, request, queryset):
        updated = queryset.update(yayinda_mi=True)
        self.message_user(request, f'{updated} içerik yayına alındı.')
    make_published.short_description = 'Seçili içerikleri yayına al'
    
    def make_draft(self, request, queryset):
        updated = queryset.update(yayinda_mi=False)
        self.message_user(request, f'{updated} içerik taslağa çevrildi.')
    make_draft.short_description = 'Seçili içerikleri taslağa çevir'
    
    def save_model(self, request, obj, form, change):
        """İçerik kaydedilirken otomatik olarak admin kullanıcısını ata"""
        if not change:  # Yeni oluşturuluyorsa
            obj.olusturan_admin = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        # Sadece superuser ekleyebilir
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        # Sadece superuser düzenleyebilir
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        # Sadece superuser silebilir
        return request.user.is_superuser
