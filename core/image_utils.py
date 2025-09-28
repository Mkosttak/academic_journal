from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.cache import cache
import os
import hashlib
from io import BytesIO
from django.conf import settings

def optimize_image(image_field, max_width=1200, max_height=1200, quality=85):
    """
    Resmi optimize eder ve boyutlandırır
    """
    if not image_field:
        return None
    
    try:
        # Resmi aç
        with Image.open(image_field) as img:
            # EXIF verilerini düzelt (otomatik rotasyon)
            img = ImageOps.exif_transpose(img)
            
            # Renk modunu RGB'ye çevir (RGBA ise)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Transparent arka plan için beyaz arka plan
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Boyutlandırma
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Optimize edilmiş resmi kaydet
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            return ContentFile(output.getvalue())
    except Exception as e:
        print(f"Image optimization error: {e}")
        return None

def create_thumbnail(image_field, size=(300, 300), quality=80):
    """
    Küçük resim oluşturur
    """
    if not image_field:
        return None
    
    try:
        with Image.open(image_field) as img:
            # EXIF verilerini düzelt
            img = ImageOps.exif_transpose(img)
            
            # Renk modunu düzelt
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Kare thumbnail oluştur
            img = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
            
            # Optimize et
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            return ContentFile(output.getvalue())
    except Exception as e:
        print(f"Thumbnail creation error: {e}")
        return None

def get_image_info(image_field):
    """
    Resim bilgilerini döndürür
    """
    if not image_field:
        return None
    
    try:
        with Image.open(image_field) as img:
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_kb': round(image_field.size / 1024, 2)
            }
    except Exception as e:
        print(f"Image info error: {e}")
        return None

def create_multiple_thumbnails(image_field, sizes=None, quality=80):
    """
    Birden fazla boyutta thumbnail oluşturur
    """
    if not image_field:
        return {}
    
    if sizes is None:
        sizes = {
            'small': (150, 150),
            'medium': (300, 300),
            'large': (600, 600),
            'xl': (900, 900)
        }
    
    thumbnails = {}
    
    for name, size in sizes.items():
        try:
            # Cache key oluştur
            cache_key = f"thumbnail_{image_field.name}_{name}_{size[0]}x{size[1]}"
            
            # Cache'den kontrol et
            cached_thumbnail = cache.get(cache_key)
            if cached_thumbnail:
                thumbnails[name] = cached_thumbnail
                continue
            
            with Image.open(image_field) as img:
                # EXIF verilerini düzelt
                img = ImageOps.exif_transpose(img)
                
                # RGB'ye çevir
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Thumbnail oluştur
                thumbnail = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
                
                # Dosyayı kaydet
                output = BytesIO()
                thumbnail.save(output, format='JPEG', quality=quality, optimize=True)
                output.seek(0)
                
                # Local storage'a kaydet
                filename = f"thumbnails/{name}_{hashlib.md5(output.getvalue()).hexdigest()[:8]}.jpg"
                path = default_storage.save(filename, ContentFile(output.getvalue()))
                thumbnails[name] = default_storage.url(path)
                
                # Cache'e kaydet
                cache.set(cache_key, thumbnails[name], 86400)  # 24 saat
                
        except Exception as e:
            print(f"Thumbnail creation error for {name}: {e}")
            continue
    
    return thumbnails

def create_webp_version(image_field, quality=85):
    """
    WebP formatında optimize edilmiş versiyon oluşturur
    """
    if not image_field:
        return None
    
    try:
        with Image.open(image_field) as img:
            # EXIF verilerini düzelt
            img = ImageOps.exif_transpose(img)
            
            # RGB'ye çevir
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # WebP olarak kaydet
            output = BytesIO()
            img.save(output, format='WEBP', quality=quality, optimize=True)
            output.seek(0)
            
            return ContentFile(output.getvalue())
    
    except Exception as e:
        print(f"WebP conversion error: {e}")
        return None

def create_placeholder_image(width=300, height=300, text="No Image", color=(240, 240, 240)):
    """
    Placeholder resim oluşturur
    """
    try:
        # Boş resim oluştur
        image = Image.new('RGB', (width, height), color)
        
        # Text ekle
        draw = ImageDraw.Draw(image)
        
        # Font boyutunu hesapla
        font_size = min(width, height) // 10
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Text'i ortala
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill=(100, 100, 100), font=font)
        
        # Dosyayı kaydet
        output = BytesIO()
        image.save(output, format='JPEG', quality=80)
        output.seek(0)
        
        return ContentFile(output.getvalue())
    
    except Exception as e:
        print(f"Placeholder creation error: {e}")
        return None

def get_image_dimensions(image_field):
    """
    Resim boyutlarını döndürür
    """
    if not image_field:
        return None, None
    
    try:
        with Image.open(image_field) as image:
            return image.size
    except Exception as e:
        print(f"Image dimension error: {e}")
        return None, None
