# Logo Dosyaları

Bu klasör web sitesi logo dosyalarını içerir.

## Önerilen Dosya Yapısı:

### Ana Logo Dosyaları:
- `logo.png` - Ana logo (renkli versiyon) - 200x60px önerilen
- `logo-white.png` - Beyaz/açık tema için logo - 200x60px 
- `logo-dark.png` - Koyu tema için logo - 200x60px
- `logo-small.png` - Küçük logo (navbar için) - 40x40px

### Favicon:
- `favicon.ico` - Tarayıcı sekmesi ikonu - 32x32px
- `favicon.png` - PNG format favicon - 32x32px

### Farklı Boyutlar:
- `logo-large.png` - Büyük logo (anasayfa için) - 400x120px
- `logo-medium.png` - Orta logo - 300x90px

## Template'te Kullanım:

```html
<!-- Ana logo -->
<img src="{% static 'images/logos/logo.png' %}" alt="Akademik Dergi">

<!-- Navbar küçük logo -->
<img src="{% static 'images/logos/logo-small.png' %}" alt="Logo">

<!-- Koyu tema logo -->
<img src="{% static 'images/logos/logo-white.png' %}" alt="Akademik Dergi">
```

## Favicon Kullanımı:

```html
<!-- base.html head bölümünde -->
<link rel="icon" type="image/x-icon" href="{% static 'images/logos/favicon.ico' %}">
<link rel="icon" type="image/png" href="{% static 'images/logos/favicon.png' %}">
```

## Logo Özellikleri:
- Format: PNG (şeffaflık için)
- Kalite: Yüksek çözünürlük
- Boyut: Web optimizasyonu için küçük dosya boyutu
- Renk: Web sitesi teması ile uyumlu