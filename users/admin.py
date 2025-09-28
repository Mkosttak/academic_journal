from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
import csv
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'get_full_name', 'status_badge', 'is_editor', 'is_chief_editor', 'goster_editorler_sayfasinda', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_editor', 'is_chief_editor', 'goster_editorler_sayfasinda', 'groups', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_editable = ('is_editor', 'is_chief_editor', 'goster_editorler_sayfasinda')
    ordering = ['-date_joined']
    
    # UserAdmin'deki fieldsets'i genişletiyoruz
    fieldsets = UserAdmin.fieldsets + (
        ('Ek Profil Bilgileri', {
            'fields': ('biyografi', 'profile_resmi', 'resume'),
            'classes': ('wide',)
        }),
        ('Yetki ve Görünürlük', {
            'fields': ('is_editor', 'is_chief_editor', 'goster_editorler_sayfasinda')
        }),
        ('Gizlilik Ayarları', {
            'fields': ('email_paylasim_izni', 'ozgecmis_paylasim_izni'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_editor', 'remove_editor', 'make_chief_editor', 'remove_chief_editor', 'export_users_to_csv', 'send_welcome_email']
    
    def status_badge(self, obj):
        from django.utils.html import format_html
        if obj.is_active:
            if obj.is_superuser:
                return format_html('<span style="color: red; font-weight: bold;">🔴 Süper Admin</span>')
            elif obj.is_staff:
                return format_html('<span style="color: blue; font-weight: bold;">🔵 Admin</span>')
            else:
                return format_html('<span style="color: green; font-weight: bold;">🟢 Aktif</span>')
        else:
            return format_html('<span style="color: gray; font-weight: bold;">⚫ Pasif</span>')
    status_badge.short_description = 'Durum'
    
    def make_editor(self, request, queryset):
        updated = queryset.update(is_editor=True)
        self.message_user(request, f'{updated} kullanıcı editör yapıldı.')
    make_editor.short_description = 'Seçili kullanıcıları editör yap'
    
    def remove_editor(self, request, queryset):
        updated = queryset.update(is_editor=False, is_chief_editor=False)
        self.message_user(request, f'{updated} kullanıcının editör yetkisi kaldırıldı.')
    remove_editor.short_description = 'Seçili kullanıcıların editör yetkisini kaldır'
    
    def make_chief_editor(self, request, queryset):
        updated = queryset.update(is_editor=True, is_chief_editor=True)
        self.message_user(request, f'{updated} kullanıcı baş editör yapıldı.')
    make_chief_editor.short_description = 'Seçili kullanıcıları baş editör yap'
    
    def remove_chief_editor(self, request, queryset):
        updated = queryset.update(is_chief_editor=False)
        self.message_user(request, f'{updated} kullanıcının baş editör yetkisi kaldırıldı.')
    remove_chief_editor.short_description = 'Seçili kullanıcıların baş editör yetkisini kaldır'
    
    def export_users_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="kullanicilar.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Kullanıcı Adı', 'E-posta', 'Ad Soyad', 'Durum', 'Editör', 'Baş Editör', 'Kayıt Tarihi'])
        
        for user in queryset:
            durum = 'Aktif' if user.is_active else 'Pasif'
            editor = 'Evet' if user.is_editor else 'Hayır'
            chief_editor = 'Evet' if user.is_chief_editor else 'Hayır'
            writer.writerow([
                user.username,
                user.email,
                user.get_full_name(),
                durum,
                editor,
                chief_editor,
                user.date_joined.strftime('%d.%m.%Y %H:%M')
            ])
        
        return response
    export_users_to_csv.short_description = 'Seçili kullanıcıları CSV olarak dışa aktar'
    
    def send_welcome_email(self, request, queryset):
        """Seçili kullanıcılara hoş geldin e-postası gönder"""
        count = 0
        for user in queryset:
            if user.email:
                try:
                    send_mail(
                        'Akademik Dergi Sistemine Hoş Geldiniz!',
                        f'Merhaba {user.get_full_name() or user.username},\n\nAkademik dergi sistemimize hoş geldiniz! Artık makalelerinizi yükleyebilir ve dergi içeriklerini takip edebilirsiniz.\n\nİyi çalışmalar!',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    count += 1
                except Exception as e:
                    self.message_user(request, f'E-posta gönderilirken hata oluştu: {e}', level='ERROR')
        
        self.message_user(request, f'{count} kullanıcıya hoş geldin e-postası gönderildi.')
    send_welcome_email.short_description = 'Seçili kullanıcılara hoş geldin e-postası gönder'
    
    class Media:
        js = ('admin/js/user_admin.js',)
