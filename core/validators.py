# core/validators.py
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import re
import os
from PIL import Image

# Windows için magic modülü alternatifi
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    print("Warning: python-magic not available. File type validation will be limited.")

class CustomValidators:
    """Özel validasyon sınıfları"""
    
    @staticmethod
    def validate_turkish_phone(value):
        """Türk telefon numarası validasyonu"""
        phone_regex = r'^(\+90|0)?[5][0-9]{9}$'
        if not re.match(phone_regex, value):
            raise ValidationError(_('Geçerli bir Türk telefon numarası giriniz. (Örn: 05551234567)'))
    
    @staticmethod
    def validate_turkish_tc(value):
        """Türk TC kimlik numarası validasyonu"""
        if not value.isdigit() or len(value) != 11:
            raise ValidationError(_('TC kimlik numarası 11 haneli olmalıdır.'))
        
        # TC kimlik algoritması
        digits = [int(d) for d in value]
        
        # İlk 10 hanenin toplamı
        sum_odd = sum(digits[i] for i in range(0, 9, 2))
        sum_even = sum(digits[i] for i in range(1, 9, 2))
        
        check1 = (sum_odd * 7 - sum_even) % 10
        check2 = (sum_odd + sum_even + check1) % 10
        
        if check1 != digits[9] or check2 != digits[10]:
            raise ValidationError(_('Geçersiz TC kimlik numarası.'))
    
    @staticmethod
    def validate_password_strength(value):
        """Güçlü şifre validasyonu"""
        if len(value) < 8:
            raise ValidationError(_('Şifre en az 8 karakter olmalıdır.'))
        
        if not re.search(r'[A-Z]', value):
            raise ValidationError(_('Şifre en az bir büyük harf içermelidir.'))
        
        if not re.search(r'[a-z]', value):
            raise ValidationError(_('Şifre en az bir küçük harf içermelidir.'))
        
        if not re.search(r'\d', value):
            raise ValidationError(_('Şifre en az bir rakam içermelidir.'))
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError(_('Şifre en az bir özel karakter içermelidir.'))
    
    @staticmethod
    def validate_file_size(file, max_size_mb=10):
        """Dosya boyutu validasyonu"""
        max_size_bytes = max_size_mb * 1024 * 1024
        if file.size > max_size_bytes:
            raise ValidationError(_(f'Dosya boyutu {max_size_mb}MB\'dan büyük olamaz.'))
    
    @staticmethod
    def validate_image_file(file):
        """Resim dosyası validasyonu"""
        # Dosya boyutu kontrolü
        CustomValidators.validate_file_size(file, 5)  # 5MB limit
        
        # Dosya uzantısı kontrolü
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(_('Sadece JPG, PNG, GIF ve WebP dosyaları kabul edilir.'))
        
        # MIME type kontrolü
        if MAGIC_AVAILABLE:
            try:
                file.seek(0)
                mime = magic.from_buffer(file.read(1024), mime=True)
                allowed_mimes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if mime not in allowed_mimes:
                    raise ValidationError(_('Geçersiz dosya türü.'))
            except Exception:
                raise ValidationError(_('Dosya türü belirlenemedi.'))
        else:
            # Fallback: sadece dosya uzantısı kontrolü
            print("Warning: Using file extension validation only (magic not available)")
        
        # Resim boyutları kontrolü
        try:
            file.seek(0)
            with Image.open(file) as img:
                width, height = img.size
                if width > 5000 or height > 5000:
                    raise ValidationError(_('Resim boyutu çok büyük. Maksimum 5000x5000 piksel.'))
                if width < 100 or height < 100:
                    raise ValidationError(_('Resim boyutu çok küçük. Minimum 100x100 piksel.'))
        except Exception as e:
            raise ValidationError(_('Geçersiz resim dosyası.'))
    
    @staticmethod
    def validate_pdf_file(file):
        """PDF dosyası validasyonu"""
        # Dosya boyutu kontrolü
        CustomValidators.validate_file_size(file, 50)  # 50MB limit
        
        # Dosya uzantısı kontrolü
        if not file.name.lower().endswith('.pdf'):
            raise ValidationError(_('Sadece PDF dosyaları kabul edilir.'))
        
        # MIME type kontrolü
        if MAGIC_AVAILABLE:
            try:
                file.seek(0)
                mime = magic.from_buffer(file.read(1024), mime=True)
                if mime != 'application/pdf':
                    raise ValidationError(_('Geçersiz PDF dosyası.'))
            except Exception:
                raise ValidationError(_('Dosya türü belirlenemedi.'))
        else:
            # Fallback: sadece dosya uzantısı kontrolü
            print("Warning: Using file extension validation only (magic not available)")
    
    @staticmethod
    def validate_username(value):
        """Kullanıcı adı validasyonu"""
        if len(value) < 3:
            raise ValidationError(_('Kullanıcı adı en az 3 karakter olmalıdır.'))
        
        if len(value) > 30:
            raise ValidationError(_('Kullanıcı adı en fazla 30 karakter olabilir.'))
        
        if not re.match(r'^[a-zA-Z0-9_.-]+$', value):
            raise ValidationError(_('Kullanıcı adı sadece harf, rakam, nokta, tire ve alt çizgi içerebilir.'))
        
        # Yaygın kullanıcı adları kontrolü
        forbidden_usernames = [
            'admin', 'administrator', 'root', 'user', 'test', 'guest',
            'api', 'www', 'mail', 'ftp', 'support', 'help', 'info',
            'contact', 'about', 'privacy', 'terms', 'login', 'register',
            'dashboard', 'profile', 'settings', 'account', 'system'
        ]
        
        if value.lower() in forbidden_usernames:
            raise ValidationError(_('Bu kullanıcı adı kullanılamaz.'))
    
    @staticmethod
    def validate_name(value):
        """İsim validasyonu"""
        if len(value.strip()) < 2:
            raise ValidationError(_('İsim en az 2 karakter olmalıdır.'))
        
        if len(value) > 50:
            raise ValidationError(_('İsim en fazla 50 karakter olabilir.'))
        
        if not re.match(r'^[a-zA-ZğüşıöçĞÜŞİÖÇ\s]+$', value):
            raise ValidationError(_('İsim sadece harf ve boşluk içerebilir.'))
    
    @staticmethod
    def validate_content_safety(value):
        """İçerik güvenliği validasyonu"""
        # Zararlı içerik kontrolü
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'data:text/html',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<form[^>]*>',
            r'<input[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'<style[^>]*>',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
                raise ValidationError(_('İçerik güvenlik politikalarına aykırı.'))
        
        # Spam kontrolü
        spam_keywords = [
            'viagra', 'casino', 'lottery', 'winner', 'congratulations',
            'click here', 'free money', 'earn money', 'work from home'
        ]
        
        value_lower = value.lower()
        spam_count = sum(1 for keyword in spam_keywords if keyword in value_lower)
        if spam_count >= 3:
            raise ValidationError(_('İçerik spam olarak algılandı.'))
    
    @staticmethod
    def validate_url(value):
        """URL validasyonu"""
        url_pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        if not re.match(url_pattern, value):
            raise ValidationError(_('Geçerli bir URL giriniz.'))
    
    @staticmethod
    def validate_slug(value):
        """Slug validasyonu"""
        if not re.match(r'^[a-z0-9-]+$', value):
            raise ValidationError(_('Slug sadece küçük harf, rakam ve tire içerebilir.'))
        
        if value.startswith('-') or value.endswith('-'):
            raise ValidationError(_('Slug tire ile başlayamaz veya bitemez.'))
        
        if '--' in value:
            raise ValidationError(_('Slug ardışık tire içeremez.'))

# Regex validators
phone_validator = RegexValidator(
    regex=r'^(\+90|0)?[5][0-9]{9}$',
    message='Geçerli bir Türk telefon numarası giriniz.'
)

tc_validator = RegexValidator(
    regex=r'^[0-9]{11}$',
    message='TC kimlik numarası 11 haneli olmalıdır.'
)

username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_.-]{3,30}$',
    message='Kullanıcı adı 3-30 karakter arası olmalı ve sadece harf, rakam, nokta, tire ve alt çizgi içermelidir.'
)

# Custom field validators
def validate_file_extension(value):
    """Dosya uzantısı validasyonu"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx', '.txt']
    if ext not in valid_extensions:
        raise ValidationError(_('Bu dosya türü desteklenmiyor.'))

def validate_image_extension(value):
    """Resim uzantısı validasyonu"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if ext not in valid_extensions:
        raise ValidationError(_('Bu resim türü desteklenmiyor.'))

def validate_max_file_size(max_size_mb):
    """Maksimum dosya boyutu validasyonu"""
    def validator(value):
        CustomValidators.validate_file_size(value, max_size_mb)
    return validator
