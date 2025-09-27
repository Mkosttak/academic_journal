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
        fields = ['yil', 'ay', 'cilt', 'sayi_no', 'kapak_gorseli', 'pdf_dosyasi', 'yayinlanma_secimi']
        widgets = {
            'yil': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '2025',
                'min': '2000',
                'max': '2050'
            }),
            'ay': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cilt': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '48',
                'min': '1'
            }),
            'sayi_no': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '15',
                'min': '1'
            }),
            'kapak_gorseli': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'pdf_dosyasi': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'yayinlanma_secimi': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Varsayılan değerler
        from datetime import datetime
        current_year = datetime.now().year
        
        if not self.instance.pk:  # Yeni kayıt için
            self.fields['yil'].initial = current_year
            self.fields['ay'].initial = 1
            # Cilt numarası 1'den başlasın
            self.fields['cilt'].initial = 1
            self.fields['yayinlanma_secimi'].initial = 'yayinlanmasin'
        
        # Yardım metinleri
        self.fields['kapak_gorseli'].help_text = "Yüklenmezse varsayılan dergi kapağı kullanılır"
        self.fields['pdf_dosyasi'].help_text = "Derginin tam halini içeren PDF dosyası (isteğe bağlı)"
        # Zamanlı yayın alanı kaldırıldı
        
    def clean(self):
        cleaned_data = super().clean()
        yil = cleaned_data.get('yil')
        ay = cleaned_data.get('ay')
        sayi_no = cleaned_data.get('sayi_no')
        yayinlanma_secimi = cleaned_data.get('yayinlanma_secimi')
        
        # Aynı yıl, ay ve sayı no kombinasyonunun benzersiz olduğunu kontrol et
        if yil and ay and sayi_no:
            existing = DergiSayisi.objects.filter(yil=yil, ay=ay, sayi_no=sayi_no)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(
                    f"{yil} yılı {ay}. ay {sayi_no}. sayı kombinasyonu zaten mevcut."
                )
        
        # "İleri tarih" seçeneği kaldırıldı
        
        return cleaned_data
