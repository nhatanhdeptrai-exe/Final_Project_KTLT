"""
GuestWindow — Cửa sổ chính cho Khách thuê (Guest).
Load giao diện từ UI đã sinh, gắn sidebar navigation + sub-pages.
"""
from PyQt6.QtWidgets import QMainWindow, QButtonGroup, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.UI_Guest.generated.ui_guest_main_window import Ui_GuestMainWindow


class GuestWindow(QMainWindow):
    """Cửa sổ chính giao diện Guest (shell)."""

    # (sidebar button attr, page title, custom_builder or None)
    PAGE_DEFS = [
        ("btnNavMyRoom",   "Phòng của tôi",         "my_room"),
        ("btnNavInvoices", "Hóa đơn / Thanh toán",  None),
        ("btnNavNotif",    "Thông báo",              None),
        ("btnNavAccount",  "Quản lý tài khoản",     "guest_account"),
    ]

    def __init__(self, user=None, container=None):
        super().__init__()
        self.user = user
        self.container = container

        # Load generated UI
        self.ui = Ui_GuestMainWindow()
        self.ui.setupUi(self)

        # Load sub-pages into stack
        self._pages = []
        self._load_pages()

        # Setup sidebar navigation
        self._setup_navigation()

        # Default page
        self._navigate(0)

    # ── Load Pages ──────────────────────────────────────────
    def _load_pages(self):
        """Dynamically import and add each sub-page to stackGuestMain."""
        stack = self.ui.stackGuestMain

        # Remove the default empty page(s)
        while stack.count() > 0:
            w = stack.widget(0)
            stack.removeWidget(w)
            w.deleteLater()

        for btn_name, title, builder in self.PAGE_DEFS:
            if builder:
                page_widget = self._create_custom_page(builder, title)
            else:
                page_widget = self._create_placeholder(title)
            stack.addWidget(page_widget)
            self._pages.append(page_widget)

    def _create_custom_page(self, builder: str, title: str) -> QWidget:
        if builder == "my_room":
            from ui.UI_Guest.views.my_room_view import MyRoomView
            return MyRoomView(
                user=self.user,
                contract_service=self.container.contract_service if self.container else None,
                room_service=self.container.room_service if self.container else None,
                repair_service=self.container.repair_request_service if self.container else None,
                guest_service=self.container.guest_service if self.container else None,
            )
        if builder == "guest_account":
            from ui.UI_Guest.views.guest_account_view import GuestAccountView
            view = GuestAccountView(
                user=self.user,
                auth_service=self.container.auth_service if self.container else None,
                guest_service=self.container.guest_service if self.container else None,
            )
            view.logout_requested.connect(self._do_logout)
            return view
        return self._create_placeholder(title)

    def _create_placeholder(self, title: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        lbl = QLabel(f"🚧 {title} — Đang xây dựng")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #a0aec0; font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl)
        return page

    # ── Navigation ──────────────────────────────────────────
    def _setup_navigation(self):
        """Gắn signal cho từng nút sidebar."""
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        for idx, (btn_name, _title, _builder) in enumerate(self.PAGE_DEFS):
            btn = getattr(self.ui, btn_name, None)
            if btn is None:
                continue
            self._nav_group.addButton(btn, idx)
            btn.clicked.connect(lambda checked, i=idx: self._navigate(i))

        for btn in self._nav_group.buttons():
            btn.setChecked(False)

    def _navigate(self, index: int):
        """Chuyển trang trong stackGuestMain."""
        if index < 0 or index >= len(self.PAGE_DEFS):
            return

        btn_name, title, _builder = self.PAGE_DEFS[index]

        # Update header title
        self.ui.lblPageTitle.setText(title)

        # Update checked state
        for btn in self._nav_group.buttons():
            btn.setChecked(False)
        btn = getattr(self.ui, btn_name, None)
        if btn:
            btn.setChecked(True)

        # Switch page
        self.ui.stackGuestMain.setCurrentIndex(index)

    def _do_logout(self):
        """Đăng xuất → quay lại trang đăng nhập."""
        from ui.UI_Common.views.auth_window import AuthWindow
        self._auth = AuthWindow(self.container)
        self._auth.show()
        self.close()
