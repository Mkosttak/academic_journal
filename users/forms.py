from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

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
        if img and hasattr(img, 'content_type'):
            if not img.content_type.startswith('image/'):
                raise forms.ValidationError('Sadece resim dosyası yükleyebilirsiniz.')
            if img.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Profil resmi en fazla 5MB olabilir.')
        return img

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if not resume.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Sadece PDF dosyası yükleyebilirsiniz.')
            if resume.size > 10 * 1024 * 1024:
                raise forms.ValidationError('Özgeçmiş dosyası en fazla 10MB olabilir.')
        return resume
