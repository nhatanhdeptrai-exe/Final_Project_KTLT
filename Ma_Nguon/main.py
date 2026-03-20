"""
Hệ Thống Quản Lý Phòng Trọ - Main Entry Point
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from config.container import ServiceContainer
from ui.auth_window import AuthWindow

def main():
    """Khởi động ứng dụng."""
    app = QApplication(sys.argv)

    # Khởi tạo toàn bộ dependency thông qua Container (Mọi config đều nằm ở backend)
    # Không còn config_email ở đây nữa !!!
    container = ServiceContainer()

    # Hiển thị màn hình đăng nhập
    auth_window = AuthWindow(container.auth_service)
    auth_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
