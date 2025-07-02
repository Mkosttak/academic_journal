# articles/admin.py

from django.contrib import admin
from .models import Makale, DergiSayisi, Yazar # Yazar modelini import edin

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
    list_display = ('sayi', 'olusturulma_tarihi')
    search_fields = ('sayi',)