# core/management/commands/backup.py
from django.core.management.base import BaseCommand
from core.backup import BackupManager, DatabaseBackup, MediaBackup, FullBackup
import os

class Command(BaseCommand):
    help = 'Sistem yedekleme işlemlerini yönetir'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['db', 'media', 'full'],
            default='full',
            help='Yedekleme tipi (db, media, full)',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Eski yedekleri temizle',
        )
        parser.add_argument(
            '--restore',
            type=str,
            help='Belirtilen yedekten geri yükleme yap',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='Mevcut yedekleri listele',
        )
    
    def handle(self, *args, **options):
        if options['list']:
            self.list_backups()
        elif options['restore']:
            self.restore_backup(options['restore'])
        elif options['cleanup']:
            self.cleanup_backups()
        else:
            self.create_backup(options['type'])
    
    def create_backup(self, backup_type):
        """Yedekleme oluştur"""
        self.stdout.write(f'{backup_type.upper()} yedekleme başlatılıyor...')
        
        try:
            if backup_type == 'db':
                backup = DatabaseBackup()
                backup_path = backup.create_database_backup()
            elif backup_type == 'media':
                backup = MediaBackup()
                backup_path = backup.create_media_backup()
            else:  # full
                backup = FullBackup()
                backup_path = backup.create_full_backup()
            
            file_size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'OK - {backup_type.upper()} yedekleme tamamlandi!\n'
                    f'Dosya: {os.path.basename(backup_path)}\n'
                    f'Boyut: {file_size:.2f} MB'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'HATA - Yedekleme hatasi: {e}')
            )
    
    def list_backups(self):
        """Mevcut yedekleri listele"""
        backup_dir = os.path.join(os.getcwd(), 'backups')
        
        if not os.path.exists(backup_dir):
            self.stdout.write('Yedek dizini bulunamadi.')
            return
        
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.endswith(('.zip', '.sqlite3', '.sql')):
                file_path = os.path.join(backup_dir, filename)
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                file_time = os.path.getctime(file_path)
                
                backups.append({
                    'filename': filename,
                    'size': file_size,
                    'time': file_time
                })
        
        if not backups:
            self.stdout.write('Hic yedek bulunamadi.')
            return
        
        # Zaman sırasına göre sırala (en yeni önce)
        backups.sort(key=lambda x: x['time'], reverse=True)
        
        self.stdout.write('\n=== MEVCUT YEDEKLER ===')
        for backup in backups:
            self.stdout.write(
                f"FILE: {backup['filename']} "
                f"({backup['size']:.2f} MB) - "
                f"{self._format_time(backup['time'])}"
            )
    
    def restore_backup(self, backup_filename):
        """Yedekten geri yükleme"""
        backup_path = os.path.join(os.getcwd(), 'backups', backup_filename)
        
        if not os.path.exists(backup_path):
            self.stdout.write(
                self.style.ERROR(f'HATA - Yedek dosyasi bulunamadi: {backup_filename}')
            )
            return
        
        self.stdout.write(f'Geri yükleme başlatılıyor: {backup_filename}')
        
        try:
            backup_manager = BackupManager()
            success = backup_manager.restore_from_backup(backup_path)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('OK - Geri yukleme tamamlandi!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('HATA - Geri yukleme basarisiz!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'HATA - Geri yukleme hatasi: {e}')
            )
    
    def cleanup_backups(self):
        """Eski yedekleri temizle"""
        self.stdout.write('Eski yedekler temizleniyor...')
        
        try:
            full_backup = FullBackup()
            full_backup.cleanup_old_backups()
            
            self.stdout.write(
                self.style.SUCCESS('OK - Eski yedekler temizlendi!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'HATA - Temizleme hatasi: {e}')
            )
    
    def _format_time(self, timestamp):
        """Zaman damgasını formatla"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
