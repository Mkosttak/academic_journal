from django import forms
from .models import Makale, DergiSayisi
from apps.users.models import User

class MakaleForm(forms.ModelForm):
    # Anahtar kelimeleri kullanıcıdan metin olarak alacağız
    anahtar_kelimeler_input = forms.CharField(
        label="Anahtar Kelimeler",
        help_text="Kelimeleri virgül (,) ile ayırınız.",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Makale
        fields = ['baslik', 'aciklama', 'pdf_dosyasi', 'yazarlar', 'anahtar_kelimeler_input']
        
        widgets = {
            'baslik': forms.TextInput(attrs={'class': 'form-control'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'pdf_dosyasi': forms.FileInput(attrs={'class': 'form-control'}),
            'yazarlar': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        }

    def __init__(self, *args, **kwargs):
        # Formu başlatan kullanıcıyı alalım
        self.request = kwargs.pop('request', None)
        super(MakaleForm, self).__init__(*args, **kwargs)
        
        # Yazar listesini tüm kullanıcılar olarak ayarla
        self.fields['yazarlar'].queryset = User.objects.all().order_by('first_name')

        # Eğer form düzenleme için açılıyorsa (instance varsa), anahtar kelimeleri doldur
        if self.instance and self.instance.pk:
            self.fields['anahtar_kelimeler_input'].initial = self.instance.anahtar_kelimeler

    def save(self, commit=True):
        instance = super(MakaleForm, self).save(commit=False)
        
        # anahtar_kelimeler_input'tan gelen veriyi işle ve modele kaydet
        keywords = self.cleaned_data.get('anahtar_kelimeler_input', '')
        instance.anahtar_kelimeler = ", ".join([word.strip() for word in keywords.split(',') if word.strip()])

        if commit:
            instance.save()
            # ManyToMany alanı save() sonrası kaydedilir
            self.save_m2m() 
            
        return instance

# YENİ FORM: Editör ve Admin için
class EditorMakaleForm(forms.ModelForm):
    class Meta:
        model = Makale
        fields = [
            'baslik', 'aciklama', 'pdf_dosyasi', 'anahtar_kelimeler', 
            'yazarlar', 'dergi_sayisi', 'admin_notu', 'goster_makaleler_sayfasinda'
        ]
        widgets = {
            'baslik': forms.TextInput(attrs={'class': 'form-control'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'pdf_dosyasi': forms.FileInput(attrs={'class': 'form-control'}),
            'anahtar_kelimeler': forms.TextInput(attrs={'class': 'form-control'}),
            'yazarlar': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'dergi_sayisi': forms.Select(attrs={'class': 'form-select'}),
            'admin_notu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'goster_makaleler_sayfasinda': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['yazarlar'].queryset = User.objects.all().order_by('first_name')
        self.fields['dergi_sayisi'].queryset = DergiSayisi.objects.all()
