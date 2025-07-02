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

class DergiSayisi(models.Model):
    sayi = models.CharField(max_length=100, unique=True, verbose_name="Dergi Sayısı/Adı")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dergi Sayısı"
        verbose_name_plural = "Dergi Sayıları"
        ordering = ['-olusturulma_tarihi']

    def __str__(self):
        return self.sayi

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
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)
    admin_notu_okundu = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Makale"
        verbose_name_plural = "Makaleler"
        ordering = ['-olusturulma_tarihi']

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
