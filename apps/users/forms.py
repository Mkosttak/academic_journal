from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
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
        }
