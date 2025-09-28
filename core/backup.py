# core/backup.py
import os
import shutil
import zipfile
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.core.management import call_command
from django.core.mail import send_mail
import subprocess
import logging

logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Veritabanı yedekleme sınıfı"""
    
    def __init__(self):
        self.backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Backup dizinini oluştur"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_database_backup(self):
        """Veritabanı yedeği oluştur"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
            return self._backup_sqlite(timestamp)
        else:
            return self._backup_postgresql(timestamp)
    
    def _backup_sqlite(self, timestamp):
        """SQLite veritabanı yedeği"""
        db_path = settings.DATABASES['default']['NAME']
        backup_filename = f'db_backup_{timestamp}.sqlite3'
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            shutil.copy2(db_path, backup_path)
            logger.info(f"SQLite backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"SQLite backup failed: {e}")
            raise
    
    def _backup_postgresql(self, timestamp):
        """PostgreSQL veritabanı yedeği"""
        db_config = settings.DATABASES['default']
        backup_filename = f'db_backup_{timestamp}.sql'
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            cmd = [
                'pg_dump',
                '-h', db_config['HOST'],
                '-U', db_config['USER'],
                '-d', db_config['NAME'],
                '-f', backup_path
            ]
            
            # Şifre için environment variable kullan
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['PASSWORD']
            
            subprocess.run(cmd, env=env, check=True)
            logger.info(f"PostgreSQL backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"PostgreSQL backup failed: {e}")
            raise

class MediaBackup:
    """Medya dosyaları yedekleme sınıfı"""
    
    def __init__(self):
        self.backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        self.media_dir = settings.MEDIA_ROOT
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Backup dizinini oluştur"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_media_backup(self):
        """Medya dosyaları yedeği oluştur"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'media_backup_{timestamp}.zip'
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.media_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.media_dir)
                        zipf.write(file_path, arcname)
            
            logger.info(f"Media backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Media backup failed: {e}")
            raise

class FullBackup:
    """Tam sistem yedekleme sınıfı"""
    
    def __init__(self):
        self.backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Backup dizinini oluştur"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_full_backup(self):
        """Tam sistem yedeği oluştur"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'full_backup_{timestamp}.zip'
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            # Veritabanı yedeği
            db_backup = DatabaseBackup()
            db_backup_path = db_backup.create_database_backup()
            
            # Medya yedeği
            media_backup = MediaBackup()
            media_backup_path = media_backup.create_media_backup()
            
            # Tam yedek oluştur
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Veritabanı yedeğini ekle
                zipf.write(db_backup_path, os.path.basename(db_backup_path))
                
                # Medya yedeğini ekle
                zipf.write(media_backup_path, os.path.basename(media_backup_path))
                
                # Static dosyaları ekle
                if os.path.exists(settings.STATIC_ROOT):
                    for root, dirs, files in os.walk(settings.STATIC_ROOT):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.join('static', os.path.relpath(file_path, settings.STATIC_ROOT))
                            zipf.write(file_path, arcname)
                
                # Settings ve requirements dosyalarını ekle
                zipf.write(os.path.join(settings.BASE_DIR, 'requirements.txt'), 'requirements.txt')
                zipf.write(os.path.join(settings.BASE_DIR, 'academic_journal', 'settings.py'), 'settings.py')
            
            # Geçici dosyaları temizle
            os.remove(db_backup_path)
            os.remove(media_backup_path)
            
            logger.info(f"Full backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Full backup failed: {e}")
            raise
    
    def cleanup_old_backups(self, days_to_keep=30):
        """Eski yedekleri temizle"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            for filename in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        logger.info(f"Old backup removed: {filename}")
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")

class BackupManager:
    """Yedekleme yöneticisi"""
    
    def __init__(self):
        self.db_backup = DatabaseBackup()
        self.media_backup = MediaBackup()
        self.full_backup = FullBackup()
    
    def run_scheduled_backup(self):
        """Zamanlanmış yedekleme çalıştır"""
        try:
            # Tam yedek oluştur
            backup_path = self.full_backup.create_full_backup()
            
            # Eski yedekleri temizle
            self.full_backup.cleanup_old_backups()
            
            # Başarılı yedekleme bildirimi
            self.send_backup_notification(backup_path, success=True)
            
            return backup_path
        except Exception as e:
            # Hata bildirimi
            self.send_backup_notification(None, success=False, error=str(e))
            raise
    
    def send_backup_notification(self, backup_path, success=True, error=None):
        """Yedekleme bildirimi gönder"""
        if not settings.ADMINS:
            return
        
        try:
            if success:
                subject = "✅ Yedekleme Başarılı"
                message = f"""
                Yedekleme başarıyla tamamlandı.
                
                Yedek Dosyası: {os.path.basename(backup_path) if backup_path else 'N/A'}
                Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                Boyut: {os.path.getsize(backup_path) / (1024*1024):.2f} MB
                """
            else:
                subject = "❌ Yedekleme Hatası"
                message = f"""
                Yedekleme sırasında hata oluştu.
                
                Hata: {error}
                Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin[1] for admin in settings.ADMINS],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Failed to send backup notification: {e}")
    
    def restore_from_backup(self, backup_path):
        """Yedekten geri yükleme"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Veritabanı yedeğini çıkar
                for file_info in zipf.filelist:
                    if file_info.filename.endswith('.sqlite3'):
                        zipf.extract(file_info, self.full_backup.backup_dir)
                        db_backup_path = os.path.join(self.full_backup.backup_dir, file_info.filename)
                        
                        # SQLite veritabanını geri yükle
                        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
                            shutil.copy2(db_backup_path, settings.DATABASES['default']['NAME'])
                            logger.info("Database restored successfully")
                        
                        os.remove(db_backup_path)
                        break
            
            logger.info(f"Restore completed from: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
