from PyQt6.QtWidgets import QMainWindow, QButtonGroup, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.UI_Guest.generated.ui_guest_main_window_register_UI import Ui_GuestMainWindowRegister

class GuestRegisterWindow(QMainWindow):
    """Cửa sổ cho Khách thuê chưa có phòng (để đăng ký)."""

    PAGE_DEFS = [
        ("btnNavRegister", "Đăng ký phòng", "dang_ky_phong"),
        ("btnNavAccount",  "Quản lý tài khoản", "guest_account"),
    ]

    def __init__(self, user=None, container=None):
        super().__init__()
        self.user = user
        self.container = container

        self.ui = Ui_GuestMainWindowRegister()
        self.ui.setupUi(self)

        self._pages = []
        self._load_pages()
        self._setup_navigation()
        self._navigate(0)
        
        # Connect avatar
        if hasattr(self.ui, 'lblAvatar'):
            self.ui.lblAvatar.mousePressEvent = lambda e: self._navigate(1)

    def _load_pages(self):
        stack = self.ui.stackGuestMain
        while stack.count() > 0:
            w = stack.widget(0)
            stack.removeWidget(w)
            w.deleteLater()

        for btn_name, title, builder in self.PAGE_DEFS:
            if builder == "dang_ky_phong":
                from ui.UI_Guest.Ext.dang_ky_phong_view_Ext import DangKyPhongView
                page_widget = DangKyPhongView(user=self.user, container=self.container)
            elif builder == "guest_account":
                from ui.UI_Guest.Ext.guest_account_view_Ext import GuestAccountView
                page_widget = GuestAccountView(
                    user=self.user,
                    auth_service=self.container.auth_service if self.container else None,
                    guest_service=self.container.guest_service if self.container else None,
                )
                page_widget.logout_requested.connect(self._do_logout)
            else:
                page_widget = self._create_placeholder(title)
            stack.addWidget(page_widget)
            self._pages.append(page_widget)

    def _create_placeholder(self, title: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        lbl = QLabel(f"🚧 {title} — Đang xây dựng")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #a0aec0; font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl)
        return page

    def _setup_navigation(self):
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
        if index < 0 or index >= len(self.PAGE_DEFS):
            return

        btn_name, title, _builder = self.PAGE_DEFS[index]
        self.ui.lblPageTitle.setText(title)

        for btn in self._nav_group.buttons():
            btn.setChecked(False)
        btn = getattr(self.ui, btn_name, None)
        if btn:
            btn.setChecked(True)

        self.ui.stackGuestMain.setCurrentIndex(index)

    def _do_logout(self):
        """Đăng xuất → quay lại trang đăng nhập."""
        from ui.UI_Common.Ext.auth_window_Ext import AuthWindow
        self._auth = AuthWindow(self.container)
        self._auth.show()
        self.close()
