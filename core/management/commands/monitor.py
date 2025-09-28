# core/management/commands/monitor.py
from django.core.management.base import BaseCommand
from core.monitoring import PerformanceMonitor, ErrorMonitor, SecurityMonitor
import json

class Command(BaseCommand):
    help = 'Sistem performansını ve sağlığını kontrol eder'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--report',
            action='store_true',
            help='Detaylı performans raporu oluştur',
        )
        parser.add_argument(
            '--check-db',
            action='store_true',
            help='Veritabanı sağlığını kontrol et',
        )
        parser.add_argument(
            '--check-cache',
            action='store_true',
            help='Cache sağlığını kontrol et',
        )
    
    def handle(self, *args, **options):
        if options['report']:
            self.generate_report()
        elif options['check_db']:
            self.check_database()
        elif options['check_cache']:
            self.check_cache()
        else:
            self.quick_check()
    
    def generate_report(self):
        """Detaylı performans raporu oluştur"""
        self.stdout.write(self.style.SUCCESS('Performans raporu oluşturuluyor...'))
        
        report = PerformanceMonitor.generate_performance_report()
        
        self.stdout.write(f"""
=== PERFORMANS RAPORU ===
Zaman: {report['timestamp']}
Durum: {report['status'].upper()}

Sistem Metrikleri:
- CPU Kullanımı: {report['system_metrics']['cpu_percent']:.1f}%
- Bellek Kullanımı: {report['system_metrics']['memory_percent']:.1f}%
- Disk Kullanımı: {report['system_metrics']['disk_percent']:.1f}%

Sağlık Kontrolleri:
- Veritabanı: {'✅ Sağlıklı' if report['database_health'] else '❌ Sorunlu'}
- Cache: {'✅ Sağlıklı' if report['cache_health'] else '❌ Sorunlu'}
        """)
    
    def check_database(self):
        """Veritabanı sağlığını kontrol et"""
        self.stdout.write('Veritabanı sağlığı kontrol ediliyor...')
        
        if PerformanceMonitor.check_database_health():
            self.stdout.write(self.style.SUCCESS('OK - Veritabani saglikli'))
        else:
            self.stdout.write(self.style.ERROR('HATA - Veritabani sorunlu'))
    
    def check_cache(self):
        """Cache sağlığını kontrol et"""
        self.stdout.write('Cache sağlığı kontrol ediliyor...')
        
        if PerformanceMonitor.check_cache_health():
            self.stdout.write(self.style.SUCCESS('OK - Cache saglikli'))
        else:
            self.stdout.write(self.style.ERROR('HATA - Cache sorunlu'))
    
    def quick_check(self):
        """Hızlı sağlık kontrolü"""
        self.stdout.write('Hızlı sağlık kontrolü yapılıyor...')
        
        db_ok = PerformanceMonitor.check_database_health()
        cache_ok = PerformanceMonitor.check_cache_health()
        metrics = PerformanceMonitor.get_system_metrics()
        
        self.stdout.write(f"""
=== HIZLI SAGLIK KONTROLU ===
Veritabani: {'OK' if db_ok else 'HATA'}
Cache: {'OK' if cache_ok else 'HATA'}
CPU: {metrics['cpu_percent']:.1f}%
Bellek: {metrics['memory_percent']:.1f}%
Disk: {metrics['disk_percent']:.1f}%
        """)
