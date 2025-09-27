from django.core.management.base import BaseCommand
from articles.models import DergiIcerigi, DergiSayisi

class Command(BaseCommand):
    help = 'Mevcut dergi içeriklerine sıralama değerleri atar'

    def handle(self, *args, **options):
        # Tüm dergi sayılarını al
        dergi_sayilari = DergiSayisi.objects.all()
        
        for dergi in dergi_sayilari:
            # Bu dergi sayısındaki içerikleri al
            icerikler = DergiIcerigi.objects.filter(dergi_sayisi=dergi).order_by('-olusturulma_tarihi')
            
            # Her içeriğe sıralama değeri ata
            for index, icerik in enumerate(icerikler):
                icerik.siralama = index
                icerik.save(update_fields=['siralama'])
                self.stdout.write(
                    self.style.SUCCESS(
                        f'İçerik "{icerik.baslik}" sıralaması güncellendi: {index}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS('Tüm dergi içeriklerinin sıralaması başarıyla güncellendi!')
        )
