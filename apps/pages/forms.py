from django import forms
from .models import IletisimFormu

class IletisimModelForm(forms.ModelForm):
    class Meta:
        model = IletisimFormu
        fields = ['isim_soyisim', 'email', 'konu', 'mesaj']
        widgets = {
            'mesaj': forms.Textarea(attrs={'rows': 5}),
        }
        error_messages = {
            'isim_soyisim': {
                'required': 'İsim soyisim alanı zorunludur.',
                'max_length': 'En fazla 150 karakter girebilirsiniz.'
            },
            'email': {
                'required': 'E-posta adresi zorunludur.',
                'invalid': 'Geçerli bir e-posta adresi giriniz.'
            },
            'konu': {
                'required': 'Konu alanı zorunludur.',
                'max_length': 'En fazla 200 karakter girebilirsiniz.'
            },
            'mesaj': {
                'required': 'Mesaj alanı zorunludur.'
            },
        }
