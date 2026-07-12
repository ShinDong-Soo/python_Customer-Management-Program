import os
import shutil
from datetime import datetime

from database import DATABASE_FILE

BACKUP_DIR = "backup"


def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def create_backup():
    if not os.path.exists(DATABASE_FILE):
        raise FileNotFoundError("DB 파일이 없습니다.")

    ensure_backup_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"skin_shop_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, filename)
    shutil.copy2(DATABASE_FILE, backup_path)
    return backup_path


def list_backups():
    ensure_backup_dir()
    files = [
        filename
        for filename in os.listdir(BACKUP_DIR)
        if filename.endswith(".db")
    ]
    return sorted(files, reverse=True)


def restore_backup(filename):
    backup_path = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(backup_path):
        raise FileNotFoundError("백업 파일을 찾을 수 없습니다.")

    shutil.copy2(backup_path, DATABASE_FILE)
