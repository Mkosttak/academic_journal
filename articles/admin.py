# articles/admin.py

from django.contrib import admin
from .models import Makale, DergiSayisi, Yazar, DergiIcerigi # Yeni model de import edin

# YENİ: Yazar modelini admin paneline kaydedelim
@admin.register(Yazar)
class YazarAdmin(admin.ModelAdmin):
    list_display = ('isim_soyisim', 'user_hesabi')
    search_fields = ('isim_soyisim', 'user_hesabi__username', 'user_hesabi__email')
    autocomplete_fields = ['user_hesabi'] # Kullanıcı seçimi için daha kullanışlı bir arayüz sağlar


@admin.register(Makale)
class MakaleAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'get_yazarlar_display', 'dergi_sayisi', 'goster_makaleler_sayfasinda', 'olusturulma_tarihi')
    list_filter = ('goster_makaleler_sayfasinda', 'dergi_sayisi', 'olusturulma_tarihi')
    
    # --- ARAMA ALANLARINI GÜNCELLEYİN ---
    # Artık yazarın ismi ve kullanıcı hesabının detayları üzerinden arama yapıyoruz.
    search_fields = ('baslik', 'anahtar_kelimeler', 'yazarlar__isim_soyisim', 'yazarlar__user_hesabi__username')
    
    prepopulated_fields = {'slug': ('baslik',)}
    
    # ManyToMany alanını daha kullanışlı hale getirir.
    # Yazar sayısı çok artarsa bu satırı yoruma alıp autocomplete_fields kullanmak daha performanslı olabilir.
    filter_horizontal = ('yazarlar',) 
    # Alternatif: autocomplete_fields = ['yazarlar']


@admin.register(DergiSayisi)
class DergiSayisiAdmin(admin.ModelAdmin):
    list_display = ('get_tarih_format', 'get_cilt_sayi_format', 'yayinlanma_secimi', 'yayinlandi_mi', 'makale_sayisi', 'ordering_actions')
    search_fields = ('yil', 'cilt', 'sayi_no')
    list_filter = ('yil', 'ay', 'cilt', 'yayinlandi_mi', 'yayinlanma_secimi')
    readonly_fields = ('yayinlandi_mi',)
    ordering = ['-yil', '-ay', '-sayi_no']
    
    fieldsets = (
        ('Dergi Bilgileri', {
            'fields': ('yil', 'ay', 'cilt', 'sayi_no', 'kapak_gorseli')
        }),
        ('Yayınlanma', {
            'fields': ('yayinlanma_secimi', 'yayinlandi_mi'),
            'classes': ('collapse',)
        })
    )
    
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
    ordering_actions.allow_tags = True


@admin.register(DergiIcerigi)
class DergiIcerigiAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'dergi_sayisi', 'yayinda_mi', 'olusturan_admin', 'olusturulma_tarihi')
    list_filter = ('yayinda_mi', 'dergi_sayisi', 'olusturan_admin', 'olusturulma_tarihi')
    search_fields = ('baslik',)
    prepopulated_fields = {'slug': ('baslik',)}
    readonly_fields = ('olusturan_admin', 'goruntulenme_sayisi', 'olusturulma_tarihi', 'guncellenme_tarihi')
    
    def save_model(self, request, obj, form, change):
        """İçerik kaydedilirken otomatik olarak admin kullanıcısını ata"""
        if not change:  # Yeni oluşturuluyorsa
            obj.olusturan_admin = request.user
        super().save_model(request, obj, form, change)
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('baslik', 'slug', 'dergi_sayisi')
        }),
        ('İçerik', {
            'fields': ('aciklama', 'pdf_dosyasi')
        }),
        ('Yayın Durumu', {
            'fields': ('yayinda_mi',)
        }),
        ('Sistem Bilgileri', {
            'fields': ('olusturan_admin', 'goruntulenme_sayisi'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
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
