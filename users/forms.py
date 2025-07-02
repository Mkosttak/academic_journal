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
        fields = ('username', 'first_name', 'last_name', 'email', 'biyografi', 'profile_resmi', 'resume')
        widgets = {
            'biyografi': forms.Textarea(attrs={'rows': 4}),
            'resume': forms.ClearableFileInput(attrs={'accept': 'application/pdf'}),
            'profile_resmi': forms.ClearableFileInput(attrs={'accept': 'image/*'})
        }
        labels = {
            'resume': 'Özgeçmiş (PDF)',
        }
        help_texts = {
            'resume': None,
        }
