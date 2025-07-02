from django import forms
from users.models import User
from articles.models import DergiSayisi

class AdminUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name', 'last_name', 'email', 'biyografi', 
            'profile_resmi', 'resume', 
            'is_editor', 'goster_editorler_sayfasinda'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'biyografi': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'profile_resmi': forms.FileInput(attrs={'class': 'form-control'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
            'is_editor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'goster_editorler_sayfasinda': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DergiSayisiForm(forms.ModelForm):
    class Meta:
        model = DergiSayisi
        fields = ['sayi']
        widgets = {
            'sayi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Örn: Cilt 1, Sayı 2, 2025'})
        } 