import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from uuid import uuid4

# Dosya isimlerini benzersiz hale getiren yardımcı fonksiyon
def unique_file_path(instance, filename, subfolder):
    ext = filename.split('.')[-1]
    filename = f"{uuid4()}.{ext}"
    return os.path.join(subfolder, filename)

def profile_pic_path(instance, filename):
    return unique_file_path(instance, filename, 'profile_pics')

def resume_path(instance, filename):
    return unique_file_path(instance, filename, 'resumes')

class User(AbstractUser):
    # AbstractUser'daki first_name, last_name, email alanları zaten mevcut.
    email = models.EmailField(unique=True, verbose_name="E-posta Adresi")
    biyografi = models.TextField(blank=True, null=True, verbose_name="Biyografi")
    profile_resmi = models.ImageField(
        upload_to=profile_pic_path,
        verbose_name="Profil Resmi",
        null=True,
        blank=True
    )
    resume = models.FileField(
        upload_to=resume_path,
        blank=True,
        null=True,
        verbose_name="Özgeçmiş (PDF)"
    )
    is_editor = models.BooleanField(default=False, verbose_name="Editör Yetkisi")
    is_chief_editor = models.BooleanField(default=False, verbose_name="Baş Editör")
    goster_editorler_sayfasinda = models.BooleanField(
        default=False,
        verbose_name="Editörler Sayfasında Gösterilsin mi?"
    )
    
    # Paylaşım İzinleri
    email_paylasim_izni = models.BooleanField(
        default=False,
        verbose_name="E-posta Adresimi Diğer Kullanıcılarla Paylaş"
    )
    ozgecmis_paylasim_izni = models.BooleanField(
        default=False,
        verbose_name="Özgeçmişimi Diğer Kullanıcılarla Paylaş"
    )

    # Django'nun User modelinde 'date_joined' (oluşturulma tarihi) ve
    # 'last_login' (en son giriş tarihi) zaten mevcut.

    def __str__(self):
        return self.get_full_name() or self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
