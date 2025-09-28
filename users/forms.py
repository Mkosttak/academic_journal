from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from core.validators import CustomValidators

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='İsim',
        error_messages={'required': 'İsim alanı zorunludur.'}
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Soyisim',
        error_messages={'required': 'Soyisim alanı zorunludur.'}
    )
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        help_texts = {
            'username': None,
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            CustomValidators.validate_username(username)
        return username
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            CustomValidators.validate_name(first_name)
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            CustomValidators.validate_name(last_name)
        return last_name
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            CustomValidators.validate_password_strength(password1)
        return password1

class CustomUserChangeForm(forms.ModelForm):
    # Parolayı bu formda gösterme
    password = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True
        self.fields['username'].disabled = True
        self.fields['first_name'].required = True
        self.fields['first_name'].error_messages = {'required': 'Ad alanı zorunludur.'}
        self.fields['last_name'].required = True
        self.fields['last_name'].error_messages = {'required': 'Soyad alanı zorunludur.'}
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'biyografi', 'profile_resmi', 'resume', 'email_paylasim_izni', 'ozgecmis_paylasim_izni')
        widgets = {
            'biyografi': forms.Textarea(attrs={'rows': 4}),
            'resume': forms.ClearableFileInput(attrs={'accept': 'application/pdf'}),
            'profile_resmi': forms.ClearableFileInput(attrs={'accept': 'image/*'})
        }
        labels = {
            'resume': 'Özgeçmiş (PDF)',
            'email_paylasim_izni': 'E-posta Adresimi Diğer Kullanıcılarla Paylaş',
            'ozgecmis_paylasim_izni': 'Özgeçmişimi Diğer Kullanıcılarla Paylaş',
        }
        help_texts = {
            'resume': None,
            'email_paylasim_izni': 'Bu seçeneği işaretlerseniz, diğer kullanıcılar sizin e-posta adresinizi görebilir.',
            'ozgecmis_paylasim_izni': 'Bu seçeneği işaretlerseniz, diğer kullanıcılar sizin özgeçmişinizi indirebilir.',
        }

    def clean_profile_resmi(self):
        img = self.cleaned_data.get('profile_resmi')
        if img:
            # Gelişmiş resim validasyonu
            CustomValidators.validate_image_file(img)
        return img

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Gelişmiş PDF validasyonu
            CustomValidators.validate_pdf_file(resume)
        return resume
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            CustomValidators.validate_name(first_name)
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            CustomValidators.validate_name(last_name)
        return last_name
    
    def clean_biyografi(self):
        biyografi = self.cleaned_data.get('biyografi')
        if biyografi:
            # İçerik güvenliği kontrolü
            CustomValidators.validate_content_safety(biyografi)
        return biyografi
