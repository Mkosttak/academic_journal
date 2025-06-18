from django import forms
from .models import IletisimFormu

class IletisimModelForm(forms.ModelForm):
    class Meta:
        model = IletisimFormu
        fields = ['isim_soyisim', 'email', 'konu', 'mesaj']
        widgets = {
            'mesaj': forms.Textarea(attrs={'rows': 5}),
        }
