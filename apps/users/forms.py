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
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'biyografi', 'profile_resmi', 'resume')
        widgets = {
            'biyografi': forms.Textarea(attrs={'rows': 4}),
            'resume': forms.ClearableFileInput(attrs={
                'accept': 'application/pdf',
            }),
        }
        labels = {
            'resume': 'Özgeçmiş (PDF)',
        }
        help_texts = {
            'resume': None,
        }
