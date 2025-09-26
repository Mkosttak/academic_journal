from django.db import models

# Create your models here.

class IletisimFormu(models.Model):
    isim_soyisim = models.CharField(max_length=150, verbose_name="İsim Soyisim", blank=False, null=False)
    email = models.EmailField(verbose_name="E-posta")
    konu = models.CharField(max_length=200, verbose_name="Konu")
    mesaj = models.TextField(verbose_name="Mesaj")
    cevaplandi = models.BooleanField(default=False, verbose_name="Cevaplandı mı?")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "İletişim Mesajı"
        verbose_name_plural = "İletişim Mesajları"
        ordering = ['-olusturulma_tarihi']

    def __str__(self):
        return f"{self.isim_soyisim} - {self.konu}"
