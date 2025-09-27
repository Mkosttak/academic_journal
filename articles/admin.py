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
    list_display = ('get_tarih_format', 'get_cilt_sayi_format', 'yayinlanma_secimi', 'yayinlandi_mi')
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


@admin.register(DergiIcerigi)
class DergiIcerigiAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'dergi_sayisi', 'yayinda_mi', 'olusturulma_tarihi')
    list_filter = ('yayinda_mi', 'dergi_sayisi', 'olusturulma_tarihi')
    search_fields = ('baslik',)
    prepopulated_fields = {'slug': ('baslik',)}
    readonly_fields = ('olusturan_admin', 'goruntulenme_sayisi')
    
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
