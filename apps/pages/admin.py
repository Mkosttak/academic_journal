from django.contrib import admin
from .models import IletisimFormu

@admin.register(IletisimFormu)
class IletisimFormuAdmin(admin.ModelAdmin):
    list_display = ('isim_soyisim', 'email', 'konu', 'cevaplandi', 'olusturulma_tarihi')
    list_filter = ('cevaplandi', 'olusturulma_tarihi')
    search_fields = ('isim_soyisim', 'email', 'konu', 'mesaj')
    list_editable = ('cevaplandi',)
