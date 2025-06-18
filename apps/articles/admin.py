from django.contrib import admin
from .models import Makale, DergiSayisi

@admin.register(Makale)
class MakaleAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'get_yazarlar_display', 'dergi_sayisi', 'goster_makaleler_sayfasinda', 'olusturulma_tarihi')
    list_filter = ('goster_makaleler_sayfasinda', 'dergi_sayisi', 'olusturulma_tarihi')
    search_fields = ('baslik', 'anahtar_kelimeler', 'yazarlar__first_name', 'yazarlar__last_name')
    prepopulated_fields = {'slug': ('baslik',)} # slug'ı başlığa göre otomatik doldur
    filter_horizontal = ('yazarlar',) # ManyToMany alanını daha kullanışlı hale getirir

@admin.register(DergiSayisi)
class DergiSayisiAdmin(admin.ModelAdmin):
    list_display = ('sayi', 'olusturulma_tarihi')
    search_fields = ('sayi',)
