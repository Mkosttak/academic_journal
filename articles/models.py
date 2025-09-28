import os
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from uuid import uuid4

# Benzersiz dosya yolu için yardımcı fonksiyon
def unique_file_path(instance, filename, subfolder):
    ext = filename.split('.')[-1]
    filename = f"{uuid4()}.{ext}"
    return os.path.join(subfolder, filename)

def article_pdf_path(instance, filename):
    return unique_file_path(instance, filename, 'article_pdfs')

def journal_cover_path(instance, filename):
    return unique_file_path(instance, filename, 'journal_covers')

def journal_pdf_path(instance, filename):
    return unique_file_path(instance, filename, 'journal_pdfs')

def content_pdf_path(instance, filename):
    return unique_file_path(instance, filename, 'content_pdfs')

class DergiSayisi(models.Model):
    AYLAR = [
        (1, 'Ocak'), (2, 'Şubat'), (3, 'Mart'), (4, 'Nisan'),
        (5, 'Mayıs'), (6, 'Haziran'), (7, 'Temmuz'), (8, 'Ağustos'),
        (9, 'Eylül'), (10, 'Ekim'), (11, 'Kasım'), (12, 'Aralık')
    ]
    
    YAYINLANMA_SECENEKLERI = [
        ('yayinlanmasin', 'Yayınlanmasın'),
        ('simdi', 'Şimdi Yayınlansın')
    ]
    
    yil = models.PositiveIntegerField(verbose_name="Yıl", help_text="Örn: 2025", default=2025)
    ay = models.PositiveSmallIntegerField(choices=AYLAR, verbose_name="Ay", default=1)
    cilt = models.PositiveIntegerField(verbose_name="Cilt", help_text="Örn: 1", default=1)
    sayi_no = models.PositiveIntegerField(verbose_name="Sayı No", help_text="Örn: 1", default=1)
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="Bu alan otomatik oluşturulur.")
    kapak_gorseli = models.ImageField(upload_to=journal_cover_path, verbose_name="Kapak Görseli", null=True, blank=True, help_text="Yüklenmezse varsayılan kapak kullanılır")
    pdf_dosyasi = models.FileField(upload_to=journal_pdf_path, verbose_name="Dergi PDF Dosyası", null=True, blank=True, help_text="Derginin tam halini içeren PDF dosyası (isteğe bağlı)")
    yayinlandi_mi = models.BooleanField(default=False, verbose_name="Yayınlandı mı?")
    yayinlanma_secimi = models.CharField(max_length=20, choices=YAYINLANMA_SECENEKLERI, default='yayinlanmasin', verbose_name="Yayınlanma Seçimi")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dergi Sayısı"
        verbose_name_plural = "Dergi Sayıları"
        ordering = ['-yil', '-ay', '-sayi_no']
        unique_together = ['yil', 'ay', 'sayi_no']  # Aynı yıl, ay ve sayı no'ya sahip iki dergi olamaz

    def save(self, *args, **kwargs):
        from django.utils import timezone
        from django.utils.text import slugify
        
        # Slug oluştur: 2025-Eylul formatında (Türkçe karakterleri dönüştür)
        if not self.slug:
            ay_adi = self.get_ay_display()
            # Türkçe karakterleri İngilizce karşılıklarına dönüştür
            turkce_karakterler = {
                'ü': 'u', 'Ü': 'U',
                'ö': 'o', 'Ö': 'O',
                'ç': 'c', 'Ç': 'C',
                'ş': 's', 'Ş': 'S',
                'ı': 'i', 'İ': 'I',
                'ğ': 'g', 'Ğ': 'G'
            }
            
            for tr, en in turkce_karakterler.items():
                ay_adi = ay_adi.replace(tr, en)
            
            self.slug = f"{self.yil}-{ay_adi}"
        
        # Eğer yayınlanmasın seçeneği seçilmişse yayınlanmadı olarak işaretle
        if self.yayinlanma_secimi == 'yayinlanmasin':
            self.yayinlandi_mi = False
            self.zamanli_yayinlanma_tarihi = None
        
        # Eğer şimdi seçeneği seçilmişse direkt yayınla
        elif self.yayinlanma_secimi == 'simdi':
            self.yayinlandi_mi = True
            self.zamanli_yayinlanma_tarihi = None
        
        # "İleri tarih" seçeneği kaldırıldı
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.yil} - {self.get_ay_display()}, Cilt {self.cilt} Sayı {self.sayi_no}"
    
    def get_tarih_format(self):
        return f"{self.yil} - {self.get_ay_display()}"
    
    def get_cilt_sayi_format(self):
        return f"Cilt {self.cilt}, Sayı {self.sayi_no}"
        
    def get_kapak_url(self):
        """Kapak görseli varsa onun URL'ini, yoksa varsayılan kapak URL'ini döndürür"""
        if self.kapak_gorseli:
            return self.kapak_gorseli.url
        return '/static/images/default-journal-cover.png'  # Varsayılan kapak
        
    @property 
    def makale_sayisi(self):
        """Bu dergi sayısındaki makale sayısını döndürür"""
        return self.makaleler.filter(goster_makaleler_sayfasinda=True).count()

# --- YENİ MODEL: YAZAR ---
class Yazar(models.Model):
    """
    Hem sisteme kayıtlı kullanıcıları (User) hem de harici yazarları
    temsil eden model.
    """
    isim_soyisim = models.CharField(max_length=255, verbose_name="Yazarın Adı Soyadı")
    user_hesabi = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='yazar_profili'
    )

    class Meta:
        verbose_name = "Yazar"
        verbose_name_plural = "Yazarlar"
        ordering = ['isim_soyisim']

    def __str__(self):
        return self.isim_soyisim

class Makale(models.Model):
    baslik = models.CharField(max_length=255, verbose_name="Başlık")
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="Bu alan otomatik oluşturulur.")
    aciklama = models.TextField(verbose_name="Açıklama/Özet")
    pdf_dosyasi = models.FileField(upload_to=article_pdf_path, verbose_name="PDF Dosyası")
    anahtar_kelimeler = models.CharField(max_length=255, verbose_name="Anahtar Kelimeler", help_text="Kelimeleri virgül (,) ile ayırınız.", blank=True)
    yazarlar = models.ManyToManyField(Yazar, related_name='makaleler', verbose_name="Yazarlar")
    dergi_sayisi = models.ForeignKey(DergiSayisi, on_delete=models.SET_NULL, null=True, blank=True, related_name='makaleler', verbose_name="Dergi Sayısı")
    admin_notu = models.TextField(blank=True, null=True, verbose_name="Editör/Admin Notu")
    goruntulenme_sayisi = models.PositiveIntegerField(default=0, verbose_name="Görüntülenme Sayısı")
    goster_makaleler_sayfasinda = models.BooleanField(default=False, verbose_name="Yayında mı?")
    siralama = models.PositiveIntegerField(default=0, verbose_name="Sıralama", help_text="Dergi sayısındaki makale sıralaması (0 = en üstte)")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)
    admin_notu_okundu = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Makale"
        verbose_name_plural = "Makaleler"
        ordering = ['siralama', '-olusturulma_tarihi']

    def __str__(self):
        return self.baslik

    def save(self, *args, **kwargs):
        # Eğer slug boş ise, başlıktan otomatik oluştur
        if not self.slug:
            self.slug = slugify(self.baslik)
            # Slug'ın benzersiz olmasını sağla
            original_slug = self.slug
            queryset = Makale.objects.filter(slug=self.slug).exists()
            counter = 1
            while queryset:
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                queryset = Makale.objects.filter(slug=self.slug).exists()
        
        # Eğer admin notu değiştiyse, notu okunmadı olarak işaretle
        if self.pk: # Eğer obje veritabanında varsa (güncelleme işlemi)
            try:
                eski_kayit = Makale.objects.get(pk=self.pk)
                if eski_kayit.admin_notu != self.admin_notu and self.admin_notu:
                    self.admin_notu_okundu = False
            except Makale.DoesNotExist:
                pass # Yeni obje, sorun yok

        super().save(*args, **kwargs)

    def get_keywords_list(self):
        if self.anahtar_kelimeler:
            return [keyword.strip() for keyword in self.anahtar_kelimeler.split(',')]
        return []

    def get_yazarlar_display(self):
        return ", ".join([yazar.isim_soyisim for yazar in self.yazarlar.all()])


class DergiIcerigi(models.Model):
    """
    Dergi içindeki farklı içerik türleri için model (söyleşiler, mezun hikayeler, vb.)
    Sadece admin kullanıcıları tarafından eklenebilir.
    """
    ICERIK_TURLERI = [
        ('soylesi', 'Söyleşi'),
        ('mezun_hikayesi', 'Mezun Hikayesi'),
        ('etkinlik', 'Etkinlik'),
        ('haber', 'Haber'),
        ('editorden', 'Editörden'),
        ('diger', 'Diğer'),
    ]
    
    baslik = models.CharField(max_length=255, verbose_name="Başlık")
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="Bu alan otomatik oluşturulur.")
    icerik_turu = models.CharField(max_length=20, choices=ICERIK_TURLERI, verbose_name="İçerik Türü")
    aciklama = models.TextField(verbose_name="Açıklama/Özet", blank=True, null=True)
    icerik = models.TextField(verbose_name="İçerik", help_text="Ana içerik metni")
    pdf_dosyasi = models.FileField(upload_to=content_pdf_path, verbose_name="PDF Dosyası", null=True, blank=True)
    anahtar_kelimeler = models.CharField(max_length=255, verbose_name="Anahtar Kelimeler", help_text="Kelimeleri virgül (,) ile ayırınız.", blank=True)
    yazarlar = models.ManyToManyField(Yazar, related_name='dergi_icerikleri', verbose_name="Yazarlar", blank=True)
    dergi_sayisi = models.ForeignKey(DergiSayisi, on_delete=models.SET_NULL, null=True, blank=True, related_name='icerikler', verbose_name="Dergi Sayısı")
    goruntulenme_sayisi = models.PositiveIntegerField(default=0, verbose_name="Görüntülenme Sayısı")
    yayinda_mi = models.BooleanField(default=False, verbose_name="Yayında mı?")
    siralama = models.PositiveIntegerField(default=0, verbose_name="Sıralama", help_text="Dergi sayısındaki içerik sıralaması (0 = en üstte)")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)
    olusturan_admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='olusturulan_icerikler', verbose_name="Oluşturan Admin")

    class Meta:
        verbose_name = "Dergi İçeriği"
        verbose_name_plural = "Dergi İçerikleri"
        ordering = ['siralama', '-olusturulma_tarihi']

    def __str__(self):
        return f"{self.get_icerik_turu_display()} - {self.baslik}"

    def save(self, *args, **kwargs):
        # Eğer slug boş ise, başlıktan otomatik oluştur
        if not self.slug:
            self.slug = slugify(self.baslik)
            # Slug'ın benzersiz olmasını sağla
            original_slug = self.slug
            queryset = DergiIcerigi.objects.filter(slug=self.slug).exists()
            counter = 1
            while queryset:
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                queryset = DergiIcerigi.objects.filter(slug=self.slug).exists()
        
        super().save(*args, **kwargs)

    def get_keywords_list(self):
        if self.anahtar_kelimeler:
            return [keyword.strip() for keyword in self.anahtar_kelimeler.split(',')]
        return []

    def get_yazarlar_display(self):
        return ", ".join([yazar.isim_soyisim for yazar in self.yazarlar.all()])
