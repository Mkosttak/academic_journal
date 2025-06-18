from django import forms
from apps.users.models import User
from apps.articles.models import DergiSayisi

class AdminUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['is_editor', 'goster_editorler_sayfasinda', 'is_staff', 'is_superuser']
        widgets = {
            'is_editor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'goster_editorler_sayfasinda': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DergiSayisiForm(forms.ModelForm):
    class Meta:
        model = DergiSayisi
        fields = ['sayi']
        widgets = {
            'sayi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Örn: Cilt 1, Sayı 2, 2025'})
        } 