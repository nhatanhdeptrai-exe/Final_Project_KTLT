"""BackupService — Sao lưu / khôi phục dữ liệu."""
import os
import shutil
from datetime import datetime
from typing import List, Tuple
from config.constants import DATA_DIR, BACKUPS_DIR, DEFAULT_BACKUP_RETENTION_DAYS


class BackupService:
    def __init__(self):
        self.backups_dir = str(BACKUPS_DIR)

    def create_backup(self) -> Tuple[bool, str]:
        """Sao lưu toàn bộ data/ vào backups/."""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_path = os.path.join(self.backups_dir, f'backup_{timestamp}')
        try:
            os.makedirs(backup_path, exist_ok=True)
            for folder in ['json', 'xml', 'excel']:
                src = os.path.join(str(DATA_DIR), folder)
                dst = os.path.join(backup_path, folder)
                if os.path.exists(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
            return True, f"Sao lưu thành công: {timestamp}"
        except Exception as e:
            return False, f"Lỗi sao lưu: {str(e)}"

    def restore_backup(self, backup_name: str) -> Tuple[bool, str]:
        """Khôi phục từ backup."""
        backup_path = os.path.join(self.backups_dir, backup_name)
        if not os.path.exists(backup_path):
            return False, "Không tìm thấy bản sao lưu"
        try:
            for folder in ['json', 'xml', 'excel']:
                src = os.path.join(backup_path, folder)
                dst = os.path.join(str(DATA_DIR), folder)
                if os.path.exists(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
            return True, "Khôi phục thành công"
        except Exception as e:
            return False, f"Lỗi khôi phục: {str(e)}"

    def list_backups(self) -> List[str]:
        if not os.path.exists(self.backups_dir): return []
        return sorted([d for d in os.listdir(self.backups_dir) if d.startswith('backup_')], reverse=True)

    def cleanup_old(self, retention_days: int = DEFAULT_BACKUP_RETENTION_DAYS) -> int:
        """Xóa backup quá hạn. Trả về số lượng đã xóa."""
        count = 0
        for name in self.list_backups():
            path = os.path.join(self.backups_dir, name)
            age = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(path))).days
            if age > retention_days:
                shutil.rmtree(path)
                count += 1
        return count
