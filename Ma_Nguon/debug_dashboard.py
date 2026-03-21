"""Debug: Test DashboardView in isolation."""
import sys
sys.path.insert(0, r'd:\Documents\Do_AN\Ma_Nguon')

from PyQt6.QtWidgets import QApplication, QMainWindow

app = QApplication(sys.argv)

# Test 1: Import
print("[DEBUG] Importing DashboardView...")
try:
    from ui.UI_Admin.views.dashboard_view import DashboardView
    print("[DEBUG] Import OK")
except Exception as e:
    print(f"[DEBUG] Import FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# Test 2: Create container
print("[DEBUG] Creating ServiceContainer...")
try:
    from config.container import ServiceContainer
    container = ServiceContainer()
    print("[DEBUG] Container OK")
except Exception as e:
    print(f"[DEBUG] Container FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# Test 3: Create DashboardView
print("[DEBUG] Creating DashboardView...")
try:
    win = QMainWindow()
    dashboard = DashboardView(container=container)
    win.setCentralWidget(dashboard)
    print("[DEBUG] DashboardView created OK")
    win.setWindowTitle("Debug Dashboard")
    win.resize(1000, 700)
    win.show()
    print("[DEBUG] Window shown OK")
except Exception as e:
    print(f"[DEBUG] DashboardView FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

sys.exit(app.exec())
