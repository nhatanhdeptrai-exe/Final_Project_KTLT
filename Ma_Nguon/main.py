import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from config.container import ServiceContainer
from ui.UI_Common.Ext.auth_window_Ext import AuthWindow

def main():
    app = QApplication(sys.argv)
    container = ServiceContainer()

    auth_window = AuthWindow(container)
    auth_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
