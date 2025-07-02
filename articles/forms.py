import re
import json
from django import forms
from .models import Makale, DergiSayisi, Yazar
from users.models import User

# --- YENİ MİXİN ---
class YazarFormMixin:
    """Yazar ekleme/düzenleme mantığını içeren ortak mixin."""
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Alanı her durumda ekle
        self.fields['yazarlar_json'] = forms.CharField(widget=forms.HiddenInput(), required=False)

        # Yazarlar JSON initial değerini set et
        yazar_listesi = []
        if self.instance and self.instance.pk:
            # Düzenleme: mevcut yazarları ekle
            for yazar in self.instance.yazarlar.all():
                yazar_listesi.append({
                    'isim_soyisim': yazar.isim_soyisim,
                    'username': yazar.user_hesabi.username if yazar.user_hesabi else None
                })
        elif self.request and self.request.user.is_authenticated:
            # Yeni ekleme: giriş yapan kullanıcıyı otomatik ekle
            user = self.request.user
            yazar_listesi.append({
                'isim_soyisim': user.get_full_name() or user.username,
                'username': user.username
            })

        self.fields['yazarlar_json'].initial = json.dumps(yazar_listesi)

    def clean_yazarlar_json(self):
        yazarlar_str = self.cleaned_data.get('yazarlar_json')
        if not yazarlar_str:
            raise forms.ValidationError("En az bir yazar eklemelisiniz.")
        try:
            yazarlar_list = json.loads(yazarlar_str)
            if not isinstance(yazarlar_list, list) or not yazarlar_list:
                raise forms.ValidationError("Geçersiz yazar formatı.")
        except json.JSONDecodeError:
            raise forms.ValidationError("Geçersiz yazar formatı.")
        return yazarlar_list

    def _save_yazarlar(self, instance):
        """JSON verisinden yazarları işleyip makaleye ekler."""
        processed_yazarlar = self.cleaned_data.get('yazarlar_json')
        instance.yazarlar.clear()
        eklenen_yazarlar = set()
        for yazar_data in processed_yazarlar:
            username = yazar_data.get('username')
            isim = yazar_data.get('isim_soyisim')
            yazar_key = (isim, username or '')
            if yazar_key in eklenen_yazarlar:
                continue
            eklenen_yazarlar.add(yazar_key)
            if username:
                user = User.objects.get(username=username)
                yazar_obj, created = Yazar.objects.get_or_create(
                    user_hesabi=user, defaults={'isim_soyisim': isim}
                )
                if not created and yazar_obj.isim_soyisim != isim:
                    yazar_obj.isim_soyisim = isim
                    yazar_obj.save()
            else:
                yazar_obj = Yazar.objects.create(isim_soyisim=isim, user_hesabi=None)
            instance.yazarlar.add(yazar_obj)

# --- MAKALE FORMU (DÜZELTİLMİŞ HALİ) ---
class MakaleForm(YazarFormMixin, forms.ModelForm):
    anahtar_kelimeler_input = forms.CharField(
        label="Anahtar Kelimeler (İsteğe Bağlı)",
        help_text="Kelimeleri virgül (,) ile ayırınız.",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'max_length': 'En fazla 255 karakter girebilirsiniz.'
        }
    )

    class Meta:
        model = Makale
        fields = ['baslik', 'aciklama', 'pdf_dosyasi', 'anahtar_kelimeler_input']
        widgets = {
            'pdf_dosyasi': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }
        error_messages = {
            'baslik': {
                'required': 'Başlık alanı zorunludur.',
                'max_length': 'En fazla 255 karakter girebilirsiniz.'
            },
            'aciklama': {
                'required': 'Açıklama alanı zorunludur.'
            },
            'pdf_dosyasi': {
                'required': 'PDF dosyası yüklemek zorunludur.',
                'invalid': 'Geçerli bir PDF dosyası yükleyiniz.'
            },
        }
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if not (self.instance and self.instance.pk) and self.request and self.request.user.is_authenticated:
            user = self.request.user
            yazar_listesi = [{'isim_soyisim': user.get_full_name() or user.username, 'username': user.username}]
            self.fields['yazarlar_json'].initial = json.dumps(yazar_listesi)
        if self.instance and self.instance.pk:
            self.fields['anahtar_kelimeler_input'].initial = self.instance.anahtar_kelimeler

    def save(self, commit=True):
        instance = super().save(commit=False)
        keywords = self.cleaned_data.get('anahtar_kelimeler_input', '')
        instance.anahtar_kelimeler = ", ".join([word.strip() for word in keywords.split(',') if word.strip()])

        if commit:
            instance.save()
            self._save_yazarlar(instance)
            
        return instance

# --- EDİTÖR MAKALE FORMU ---
class EditorMakaleForm(YazarFormMixin, forms.ModelForm):
    class Meta:
        model = Makale
        fields = [
            'baslik', 'aciklama', 'pdf_dosyasi', 'anahtar_kelimeler',
            'dergi_sayisi', 'admin_notu', 'goster_makaleler_sayfasinda'
        ]
        widgets = {
            'baslik': forms.TextInput(attrs={'class': 'form-control'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'pdf_dosyasi': forms.FileInput(attrs={'class': 'form-control'}),
            'anahtar_kelimeler': forms.TextInput(attrs={'class': 'form-control'}),
            'dergi_sayisi': forms.Select(attrs={'class': 'form-select'}),
            'admin_notu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'goster_makaleler_sayfasinda': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        error_messages = {
            'baslik': {
                'required': 'Başlık alanı zorunludur.',
                'max_length': 'En fazla 255 karakter girebilirsiniz.'
            },
            'aciklama': {
                'required': 'Açıklama alanı zorunludur.'
            },
            'pdf_dosyasi': {
                'required': 'PDF dosyası yüklemek zorunludur.',
                'invalid': 'Geçerli bir PDF dosyası yükleyiniz.'
            },
            'anahtar_kelimeler': {
                'max_length': 'En fazla 255 karakter girebilirsiniz.'
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['anahtar_kelimeler'].required = False

    def save(self, commit=True):
        instance = super().save(commit=True)
        self._save_yazarlar(instance)
        return instance
