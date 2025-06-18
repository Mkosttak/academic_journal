from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_editor', 'goster_editorler_sayfasinda')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'is_editor', 'goster_editorler_sayfasinda')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    # UserAdmin'deki fieldsets'i genişletiyoruz
    fieldsets = UserAdmin.fieldsets + (
        ('Ek Profil Bilgileri', {'fields': ('biyografi', 'profile_resmi', 'resume')}),
        ('Yetki ve Görünürlük', {'fields': ('is_editor', 'goster_editorler_sayfasinda')}),
    )
