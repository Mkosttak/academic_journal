import os
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image
import uuid

def validate_file_type(file, allowed_types):
    """
    Dosya tipini güvenli bir şekilde kontrol eder
    """
    # Dosya boyutu kontrolü (10MB limit)
    if file.size > 10 * 1024 * 1024:
        raise ValidationError('Dosya boyutu 10MB\'dan büyük olamaz.')
    
    # Dosya uzantısı kontrolü
    file_extension = os.path.splitext(file.name)[1].lower()
    allowed_extensions = {
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
        'image/gif': ['.gif'],
        'image/webp': ['.webp'],
        'application/pdf': ['.pdf']
    }
    
    # MIME type'a göre uzantı kontrolü
    for mime_type, extensions in allowed_extensions.items():
        if mime_type in allowed_types and file_extension in extensions:
            return True
    
    raise ValidationError(f'Bu dosya tipi desteklenmiyor. İzin verilen tipler: {", ".join(allowed_types)}')

def validate_image_file(file):
    """
    Resim dosyası güvenlik kontrolü
    """
    allowed_image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    validate_file_type(file, allowed_image_types)
    
    # PIL ile resim doğrulama
    try:
        with Image.open(file) as img:
            img.verify()
        file.seek(0)
    except Exception:
        raise ValidationError('Geçersiz resim dosyası.')
    
    return True

def validate_pdf_file(file):
    """
    PDF dosyası güvenlik kontrolü
    """
    allowed_pdf_types = ['application/pdf']
    validate_file_type(file, allowed_pdf_types)
    
    # PDF başlık kontrolü
    file.seek(0)
    header = file.read(4)
    if not header.startswith(b'%PDF'):
        raise ValidationError('Geçersiz PDF dosyası.')
    
    file.seek(0)
    return True

def secure_filename(filename):
    """
    Güvenli dosya adı oluşturur
    """
    # Tehlikeli karakterleri temizle
    filename = os.path.basename(filename)
    filename = filename.replace('..', '')
    filename = filename.replace('/', '')
    filename = filename.replace('\\', '')
    
    # UUID ile benzersiz isim oluştur
    name, ext = os.path.splitext(filename)
    return f"{uuid.uuid4()}{ext.lower()}"

def scan_file_for_malware(file_path):
    """
    Dosya zararlı yazılım taraması (basit kontrol)
    """
    dangerous_patterns = [
        b'<script',
        b'javascript:',
        b'vbscript:',
        b'data:text/html',
        b'<iframe',
        b'<object',
        b'<embed'
    ]
    
    with open(file_path, 'rb') as f:
        content = f.read(1024)  # İlk 1KB'ı kontrol et
        for pattern in dangerous_patterns:
            if pattern in content.lower():
                raise ValidationError('Dosya güvenlik riski içeriyor.')
    
    return True
