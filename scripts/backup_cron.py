#!/usr/bin/env python
"""
Otomatik yedekleme scripti
Cron job olarak çalıştırılabilir: 0 2 * * * python /path/to/scripts/backup_cron.py
"""

import os
import sys
import django
from pathlib import Path

# Django projesini ayarla
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academic_journal.settings')
django.setup()

from core.backup import BackupManager

if __name__ == '__main__':
    try:
        backup_manager = BackupManager()
        backup_path = backup_manager.run_scheduled_backup()
        print(f"Backup completed successfully: {backup_path}")
    except Exception as e:
        print(f"Backup failed: {e}")
        sys.exit(1)
