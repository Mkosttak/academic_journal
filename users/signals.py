import os
import logging
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from .models import User
from articles.models import Makale, Yazar

def delete_file_if_changed(instance, field_name):
    if not instance.pk:
        return

    try:
        old_instance = instance.__class__.objects.get(pk=instance.pk)
        old_file = getattr(old_instance, field_name)
        new_file = getattr(instance, field_name)

        if old_file and old_file != new_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)
    except instance.__class__.DoesNotExist:
        pass # Obje yeni oluşturuluyor, eski dosya yok.

@receiver(pre_save, sender=User)
def user_file_cleanup(sender, instance, **kwargs):
    delete_file_if_changed(instance, 'profile_resmi')
    delete_file_if_changed(instance, 'resume')

@receiver(pre_save, sender=Makale)
def article_file_cleanup(sender, instance, **kwargs):
    delete_file_if_changed(instance, 'pdf_dosyasi')

@receiver(post_delete, sender=User)
def on_delete_user_cleanup(sender, instance, **kwargs):
    if instance.profile_resmi:
        try:
            if os.path.isfile(instance.profile_resmi.path):
                os.remove(instance.profile_resmi.path)
        except Exception as e:
            logging.error(f"Profil resmi silinemedi: {e}")
    if instance.resume:
        try:
            if os.path.isfile(instance.resume.path):
                os.remove(instance.resume.path)
        except Exception as e:
            logging.error(f"Özgeçmiş dosyası silinemedi: {e}")

@receiver(post_delete, sender=Makale)
def on_delete_article_cleanup(sender, instance, **kwargs):
    if instance.pdf_dosyasi:
        try:
            if os.path.isfile(instance.pdf_dosyasi.path):
                os.remove(instance.pdf_dosyasi.path)
        except Exception as e:
            logging.error(f"Makale PDF dosyası silinemedi: {e}")

@receiver(post_save, sender=User)
def create_or_update_yazar_profile(sender, instance, created, **kwargs):
    """
    Kullanıcı kaydedildiğinde ilişkili Yazar profilini oluşturur veya günceller.
    Yazar profili sadece kullanıcı bir makalenin yazarıysa oluşturulur/güncellenir.
    """
    yazar_profili, yazar_created = Yazar.objects.get_or_create(user_hesabi=instance)
    yeni_isim = instance.get_full_name() or instance.username
    if yazar_created or yazar_profili.isim_soyisim != yeni_isim:
        yazar_profili.isim_soyisim = yeni_isim
        yazar_profili.save() 