from django.contrib import admin
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
import csv
from .models import IletisimFormu

@admin.register(IletisimFormu)
class IletisimFormuAdmin(admin.ModelAdmin):
    list_display = ('isim_soyisim', 'email', 'konu', 'cevaplandi', 'status_badge', 'olusturulma_tarihi')
    list_filter = ('cevaplandi', 'olusturulma_tarihi')
    search_fields = ('isim_soyisim', 'email', 'konu', 'mesaj')
    list_editable = ('cevaplandi',)
    readonly_fields = ('olusturulma_tarihi',)
    ordering = ['-olusturulma_tarihi']
    
    fieldsets = (
        ('İletişim Bilgileri', {
            'fields': ('isim_soyisim', 'email', 'telefon')
        }),
        ('Mesaj', {
            'fields': ('konu', 'mesaj')
        }),
        ('Durum', {
            'fields': ('cevaplandi', 'olusturulma_tarihi')
        })
    )
    
    actions = ['mark_as_answered', 'mark_as_unanswered', 'export_messages_to_csv', 'send_reply_email']
    
    def status_badge(self, obj):
        from django.utils.html import format_html
        if obj.cevaplandi:
            return format_html('<span style="color: green; font-weight: bold;">✓ Cevaplandı</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">⏳ Bekliyor</span>')
    status_badge.short_description = 'Durum'
    
    def mark_as_answered(self, request, queryset):
        updated = queryset.update(cevaplandi=True)
        self.message_user(request, f'{updated} mesaj cevaplandı olarak işaretlendi.')
    mark_as_answered.short_description = 'Seçili mesajları cevaplandı olarak işaretle'
    
    def mark_as_unanswered(self, request, queryset):
        updated = queryset.update(cevaplandi=False)
        self.message_user(request, f'{updated} mesaj cevaplanmadı olarak işaretlendi.')
    mark_as_unanswered.short_description = 'Seçili mesajları cevaplanmadı olarak işaretle'
    
    def export_messages_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="iletisim_mesajlari.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['İsim Soyisim', 'E-posta', 'Konu', 'Mesaj', 'Cevaplandı', 'Oluşturulma Tarihi'])
        
        for mesaj in queryset:
            cevaplandi = 'Evet' if mesaj.cevaplandi else 'Hayır'
            writer.writerow([
                mesaj.isim_soyisim,
                mesaj.email,
                mesaj.konu,
                mesaj.mesaj[:100] + '...' if len(mesaj.mesaj) > 100 else mesaj.mesaj,
                cevaplandi,
                mesaj.olusturulma_tarihi.strftime('%d.%m.%Y %H:%M')
            ])
        
        return response
    export_messages_to_csv.short_description = 'Seçili mesajları CSV olarak dışa aktar'
    
    def send_reply_email(self, request, queryset):
        """Seçili mesajlara toplu yanıt gönder"""
        count = 0
        for mesaj in queryset:
            if mesaj.email:
                try:
                    send_mail(
                        f'Re: {mesaj.konu}',
                        f'Merhaba {mesaj.isim_soyisim},\n\nMesajınızı aldık ve en kısa sürede size dönüş yapacağız.\n\nTeşekkürler!',
                        settings.DEFAULT_FROM_EMAIL,
                        [mesaj.email],
                        fail_silently=False,
                    )
                    count += 1
                except Exception as e:
                    self.message_user(request, f'E-posta gönderilirken hata oluştu: {e}', level='ERROR')
        
        self.message_user(request, f'{count} mesaja yanıt e-postası gönderildi.')
    send_reply_email.short_description = 'Seçili mesajlara yanıt e-postası gönder'
