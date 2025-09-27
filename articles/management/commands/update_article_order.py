from django.core.management.base import BaseCommand
from articles.models import Makale, DergiSayisi

class Command(BaseCommand):
    help = 'Mevcut makalelere sıralama değerleri atar'

    def handle(self, *args, **options):
        # Tüm dergi sayılarını al
        dergi_sayilari = DergiSayisi.objects.all()
        
        for dergi in dergi_sayilari:
            # Bu dergi sayısındaki makaleleri al
            makaleler = Makale.objects.filter(dergi_sayisi=dergi).order_by('-olusturulma_tarihi')
            
            # Her makaleye sıralama değeri ata
            for index, makale in enumerate(makaleler):
                makale.siralama = index
                makale.save(update_fields=['siralama'])
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Makale "{makale.baslik}" sıralaması güncellendi: {index}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS('Tüm makalelerin sıralaması başarıyla güncellendi!')
        )
