"""
GuestWindow — Cửa sổ chính cho Khách thuê (Guest).
Load giao diện từ UI đã sinh, gắn sidebar navigation.
"""
from PyQt6.QtWidgets import QMainWindow, QButtonGroup
from ui.UI_Guest.generated.ui_guest_main_window import Ui_GuestMainWindow


class GuestWindow(QMainWindow):
    """Cửa sổ chính giao diện Guest (shell)."""

    # Mapping: (sidebar button attr, page title, stack index)
    NAV_ITEMS = [
        ("btnNavMyRoom",   "Phòng của tôi",         0),
        ("btnNavInvoices", "Hóa đơn / Thanh toán",  1),
        ("btnNavNotif",    "Thông báo",              2),
        ("btnNavAccount",  "Quản lý tài khoản",     3),
    ]

    def __init__(self, user=None, container=None):
        super().__init__()
        self.user = user
        self.container = container

        # Load generated UI
        self.ui = Ui_GuestMainWindow()
        self.ui.setupUi(self)

        # Setup sidebar navigation
        self._setup_navigation()

        # Default page
        self._navigate(0)

    # ── Navigation ──────────────────────────────────────────
    def _setup_navigation(self):
        """Gắn signal cho từng nút sidebar."""
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        for idx, (btn_name, _title, _page_idx) in enumerate(self.NAV_ITEMS):
            btn = getattr(self.ui, btn_name, None)
            if btn is None:
                continue
            self._nav_group.addButton(btn, idx)
            btn.clicked.connect(lambda checked, i=idx: self._navigate(i))

        # Uncheck all first, then check default
        for btn in self._nav_group.buttons():
            btn.setChecked(False)

    def _navigate(self, index: int):
        """Chuyển trang trong stackGuestMain."""
        if index < 0 or index >= len(self.NAV_ITEMS):
            return

        btn_name, title, page_idx = self.NAV_ITEMS[index]

        # Update header title
        self.ui.lblPageTitle.setText(title)

        # Update checked state
        for btn in self._nav_group.buttons():
            btn.setChecked(False)
        btn = getattr(self.ui, btn_name, None)
        if btn:
            btn.setChecked(True)

        # Switch page (currently only pageRong at index 0)
        stack = self.ui.stackGuestMain
        if page_idx < stack.count():
            stack.setCurrentIndex(page_idx)
        else:
            # Page chưa được thêm vào stack → giữ trang rỗng
            stack.setCurrentIndex(0)
