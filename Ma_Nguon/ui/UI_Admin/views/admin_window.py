"""
AdminWindow — Cửa sổ chính cho Admin.
Load giao diện từ UI đã sinh, gắn sidebar navigation + sub-pages.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QButtonGroup, QLabel, QVBoxLayout,
    QFrame, QHBoxLayout, QPushButton, QMenu, QWidgetAction, QDialog
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QCursor
from ui.UI_Admin.generated.ui_admin_main_window import Ui_MainWindow


class AdminWindow(QMainWindow):
    """Cửa sổ chính giao diện Admin (shell)."""

    # (sidebar button attr, page title, generated module or None for custom)
    PAGE_DEFS = [
        ("navTrangChu",       "Trang chủ",            None),            # DashboardView (live data)
        ("navQuanLyPhong",    "Quản lý phòng",        None),            # Custom view
        ("navQuanLyKhachThu", "Quản lý khách thuê",   None),            # Custom view
        ("navHoaDon",         "Hóa đơn / Thanh toán", None),            # Custom view
        ("navSuaChua",        "Yêu cầu sửa chữa",    None),            # Custom view
        ("navThongBao",       "Thông báo",            None),            # Custom view
        ("navTaiKhoan",       "Quản lý tài khoản",   None),            # Custom view
    ]

    # Map notification targets to page indices
    TARGET_PAGE_MAP = {
        'invoice': 3,  # navHoaDon
        'repair': 4,   # navSuaChua
        'room': 1,     # navQuanLyPhong
        'guest': 2,    # navQuanLyKhachThu
    }

    def __init__(self, user=None, container=None):
        super().__init__()
        self.user = user
        self.container = container
        self._notif_view = None

        # Load generated UI shell
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Load sub-pages into stack
        self._pages = []
        self._load_pages()

        # Setup sidebar navigation
        self._setup_navigation()

        # Setup header buttons (bell + avatar)
        self._setup_header()

        # Default: first page
        self._navigate(0)

    # ── Load Pages ──────────────────────────────────────────
    def _load_pages(self):
        """Dynamically import and add each sub-page to mainContentStack."""
        stack = self.ui.mainContentStack

        # Remove the default empty page
        while stack.count() > 0:
            w = stack.widget(0)
            stack.removeWidget(w)
            w.deleteLater()

        for btn_name, title, module_name in self.PAGE_DEFS:
            if module_name is None:
                page_widget = self._create_custom_page(btn_name, title)
            else:
                page_widget = self._create_generated_page(module_name, title)
            stack.addWidget(page_widget)
            self._pages.append(page_widget)

    def _create_custom_page(self, btn_name: str, title: str) -> QWidget:
        """Tạo trang tùy chỉnh (có logic CRUD)."""
        if btn_name == "navTrangChu":
            try:
                from ui.UI_Admin.views.dashboard_view import DashboardView
                return DashboardView(container=self.container)
            except Exception as e:
                print(f"[AdminWindow] DashboardView error: {e}")
                import traceback; traceback.print_exc()
                return self._create_placeholder(title, str(e))
        if btn_name == "navQuanLyPhong":
            from ui.UI_Admin.views.room_management_view import RoomManagementView
            room_service = self.container.room_service if self.container else None
            return RoomManagementView(room_service=room_service)
        if btn_name == "navQuanLyKhachThu":
            from ui.UI_Admin.views.guest_management_view import GuestManagementView
            return GuestManagementView(
                guest_service=self.container.guest_service if self.container else None,
                contract_service=self.container.contract_service if self.container else None,
                room_service=self.container.room_service if self.container else None,
            )
        if btn_name == "navHoaDon":
            from ui.UI_Admin.views.invoice_management_view import InvoiceManagementView
            return InvoiceManagementView(
                invoice_service=self.container.invoice_service if self.container else None,
                contract_service=self.container.contract_service if self.container else None,
                guest_service=self.container.guest_service if self.container else None,
                room_service=self.container.room_service if self.container else None,
            )
        if btn_name == "navSuaChua":
            from ui.UI_Admin.views.repair_management_view import RepairManagementView
            return RepairManagementView(
                repair_service=self.container.repair_request_service if self.container else None,
                guest_service=self.container.guest_service if self.container else None,
                room_service=self.container.room_service if self.container else None,
                contract_service=self.container.contract_service if self.container else None,
            )
        if btn_name == "navThongBao":
            from ui.UI_Admin.views.notification_view import NotificationView
            self._notif_view = NotificationView(
                contract_service=self.container.contract_service if self.container else None,
                room_service=self.container.room_service if self.container else None,
                guest_service=self.container.guest_service if self.container else None,
                repair_service=self.container.repair_request_service if self.container else None,
            )
            self._notif_view.navigate_requested.connect(self._on_notif_navigate)
            return self._notif_view
        if btn_name == "navTaiKhoan":
            from ui.UI_Admin.views.account_management_view import AccountManagementView
            view = AccountManagementView(
                user=self.user,
                auth_service=self.container.auth_service if self.container else None,
            )
            view.logout_requested.connect(self._do_logout)
            return view
        # Fallback
        return self._create_placeholder(title)

    def _create_generated_page(self, module_name: str, title: str) -> QWidget:
        """Import a generated UI module and build a QWidget page from it."""
        try:
            import importlib
            mod = importlib.import_module(
                f"ui.UI_Admin.generated.{module_name}"
            )
            ui_class = mod.Ui_MainWindow
            page = QWidget()
            ui = ui_class()
            ui.setupUi(page)
            page._ui = ui
            return page
        except Exception as e:
            return self._create_placeholder(title, str(e))

    def _create_placeholder(self, title: str, error: str = None) -> QWidget:
        """Tạo trang placeholder khi chưa implement hoặc lỗi."""
        page = QWidget()
        layout = QVBoxLayout(page)
        msg = f"⚠️ Không thể tải trang: {title}\n{error}" if error else f"🚧 {title} — Đang xây dựng"
        lbl = QLabel(msg)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #e53e3e; font-size: 14px;")
        layout.addWidget(lbl)
        return page

    # ── Header Buttons ──────────────────────────────────────
    def _setup_header(self):
        """Wire bell + avatar buttons in header."""
        bell = getattr(self.ui, 'btnBell', None)
        if bell:
            bell.clicked.connect(self._on_bell_clicked)

        avatar = getattr(self.ui, 'lblAvatar', None)
        if avatar:
            avatar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            avatar.mousePressEvent = lambda ev: self._show_avatar_popup()

    def _on_bell_clicked(self):
        """Show notification popup below bell button."""
        import time
        from ui.UI_Admin.views.notification_view import _time_ago

        # Toggle: if popup just closed (within 300ms), don't reopen
        now = time.time()
        if hasattr(self, '_bell_closed_at') and (now - self._bell_closed_at) < 0.3:
            return

        # Close existing popup if any
        if hasattr(self, '_bell_popup') and self._bell_popup and self._bell_popup.isVisible():
            self._bell_popup.close()
            self._bell_popup = None
            return

        bell = self.ui.btnBell

        popup = QFrame(self, Qt.WindowType.Popup)
        popup.setStyleSheet("""
            QFrame { background: white; border: 1px solid #e2e8f0; border-radius: 10px; }
        """)
        popup.setFixedWidth(400)
        self._bell_popup = popup

        p_lay = QVBoxLayout(popup)
        p_lay.setContentsMargins(0, 8, 0, 8)
        p_lay.setSpacing(0)

        # Header
        header_w = QWidget()
        header_w.setFixedHeight(40)
        h_lay = QHBoxLayout(header_w)
        h_lay.setContentsMargins(16, 8, 16, 8)
        t = QLabel("🔔 Thông báo")
        t.setStyleSheet("font-weight: bold; font-size: 14px; color: #2d3748;")
        h_lay.addWidget(t)
        h_lay.addStretch()
        from PyQt6.QtWidgets import QPushButton
        btn_all = QPushButton("Xem tất cả →")
        btn_all.setStyleSheet(
            "QPushButton { color: #0b8480; font-size: 12px; font-weight: bold; "
            "border: none; background: transparent; }"
            "QPushButton:hover { color: #065e5b; }")
        btn_all.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_all.clicked.connect(lambda: (popup.close(), self._navigate(5)))
        h_lay.addWidget(btn_all)
        p_lay.addWidget(header_w)

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background-color: #edf2f7;")
        p_lay.addWidget(div)

        # ── Pending contracts ──
        pending_contracts = []
        if self.container and self.container.contract_service:
            all_c = self.container.contract_service.get_all()
            pending_contracts = [c for c in all_c if c.status == 'pending']

        for contract in pending_contracts[:3]:
            row_w = QWidget()
            row_w.setFixedHeight(55)
            row_w.setStyleSheet("background-color: #fffcf0; border-bottom: 1px solid #fef3c7;")
            rl = QHBoxLayout(row_w)
            rl.setContentsMargins(16, 4, 16, 4)
            rl.setSpacing(10)

            icon = QLabel("📋")
            icon.setFixedSize(30, 30)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon.setStyleSheet("background-color: #fef3c7; border-radius: 15px; font-size: 14px; border: none;")
            rl.addWidget(icon)

            room_num = f"#{contract.room_id}"
            if self._notif_view:
                room_num = self._notif_view._get_room_number(contract.room_id)
            txt = QLabel(f"Yêu cầu đăng ký phòng {room_num}")
            txt.setStyleSheet("font-size: 12px; font-weight: bold; color: #92400e; border: none;")
            txt.setWordWrap(True)
            rl.addWidget(txt, 1)

            badge = QLabel("Chờ duyệt")
            badge.setStyleSheet(
                "font-size: 10px; color: #d97706; background-color: #fef3c7; "
                "border-radius: 4px; padding: 2px 6px; font-weight: bold; border: none;")
            rl.addWidget(badge)

            p_lay.addWidget(row_w)

        # ── Regular notifications ──
        notifs = self._notif_view._notifications[:5] if self._notif_view else []
        for notif in notifs:
            row_w = QPushButton()
            row_w.setFixedHeight(55)
            row_w.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            row_w.setStyleSheet(
                "QPushButton { border: none; background: white; border-bottom: 1px solid #f0f0f0; "
                "text-align: left; padding: 0; }"
                "QPushButton:hover { background-color: #f7fafc; }")

            rl = QHBoxLayout(row_w)
            rl.setContentsMargins(16, 4, 16, 4)
            rl.setSpacing(12)

            icon = QLabel(notif['icon'])
            icon.setFixedSize(30, 30)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon.setStyleSheet(
                f"background-color: {notif['icon_bg']}; color: {notif['icon_color']}; "
                f"border-radius: 15px; font-size: 14px; border: none;")
            rl.addWidget(icon)

            txt = QLabel(notif['text'])
            txt.setStyleSheet(
                f"font-size: 12px; border: none; "
                f"{'font-weight:bold;color:#2d3748;' if not notif['read'] else 'color:#4a5568;'}")
            txt.setWordWrap(True)
            rl.addWidget(txt, 1)

            time_l = QLabel(_time_ago(notif['time']))
            time_l.setStyleSheet(
                f"font-size: 10px; border: none; "
                f"color: {'#0b8480' if not notif['read'] else '#a0aec0'};")
            rl.addWidget(time_l)

            if not notif['read']:
                dot = QLabel()
                dot.setFixedSize(8, 8)
                dot.setStyleSheet("background-color: #e53e3e; border-radius: 4px; border: none;")
                rl.addWidget(dot)

            target = notif.get('target', '')
            row_w.clicked.connect(lambda _, t=target: (popup.close(), self._on_notif_navigate(t)))
            p_lay.addWidget(row_w)

        # Show below bell
        pos = bell.mapToGlobal(bell.rect().bottomRight())
        pos.setX(pos.x() - 400)
        popup.move(pos)

        # Track close time for toggle behavior
        import time as _time
        _orig_close = popup.closeEvent
        def _on_popup_close(ev):
            self._bell_closed_at = _time.time()
            self._bell_popup = None
            if _orig_close:
                _orig_close(ev)
        popup.closeEvent = _on_popup_close

        popup.show()

    def _on_notif_navigate(self, target: str):
        """Navigate to target page based on notification."""
        idx = self.TARGET_PAGE_MAP.get(target, 5)  # default to notification page
        self._navigate(idx)

    # ── Navigation ──────────────────────────────────────────
    def _setup_navigation(self):
        """Gắn signal cho từng nút sidebar."""
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        for idx, (btn_name, _title, _mod) in enumerate(self.PAGE_DEFS):
            btn = getattr(self.ui, btn_name, None)
            if btn is None:
                continue
            self._nav_group.addButton(btn, idx)
            btn.clicked.connect(lambda checked, i=idx: self._navigate(i))

        for btn in self._nav_group.buttons():
            btn.setChecked(False)

    def _navigate(self, index: int):
        """Chuyển trang trong mainContentStack."""
        if index < 0 or index >= len(self.PAGE_DEFS):
            return

        btn_name, title, _mod = self.PAGE_DEFS[index]

        # Update header title
        self.ui.lblPageTitle.setText(title)

        # Update checked state
        for btn in self._nav_group.buttons():
            btn.setChecked(False)
        btn = getattr(self.ui, btn_name, None)
        if btn:
            btn.setChecked(True)

        # Switch page
        self.ui.mainContentStack.setCurrentIndex(index)

    def _show_avatar_popup(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: white; border: 1px solid #e2e8f0; "
            "border-radius: 8px; padding: 6px 0; min-width: 220px; }"
            "QMenu::item { padding: 0; }")

        # User info
        info_w = QWidget()
        info_lay = QVBoxLayout(info_w)
        info_lay.setContentsMargins(16, 12, 16, 8)
        info_lay.setSpacing(4)
        user_name = getattr(self.user, 'full_name', 'Admin') or 'Admin'
        lbl_name = QLabel(user_name)
        lbl_name.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_name.setStyleSheet("color: #1a202c;")
        info_lay.addWidget(lbl_name)
        lbl_role = QLabel("🛡️ Quản trị viên")
        lbl_role.setStyleSheet("color: #718096; font-size: 12px;")
        info_lay.addWidget(lbl_role)
        wa_info = QWidgetAction(menu)
        wa_info.setDefaultWidget(info_w)
        menu.addAction(wa_info)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #e2e8f0;")
        wa_sep = QWidgetAction(menu)
        wa_sep.setDefaultWidget(sep)
        menu.addAction(wa_sep)

        # Account
        btn_acc = QPushButton("👤  Quản lý tài khoản")
        btn_acc.setStyleSheet(
            "QPushButton { text-align: left; padding: 10px 16px; border: none; "
            "font-size: 13px; color: #2d3748; background: transparent; }"
            "QPushButton:hover { background-color: #f7fafc; }")
        btn_acc.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_acc.clicked.connect(lambda: (menu.close(), self._navigate(6)))
        wa_acc = QWidgetAction(menu)
        wa_acc.setDefaultWidget(btn_acc)
        menu.addAction(wa_acc)

        # Separator + Logout
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background-color: #e2e8f0;")
        wa_sep2 = QWidgetAction(menu)
        wa_sep2.setDefaultWidget(sep2)
        menu.addAction(wa_sep2)

        btn_logout = QPushButton("🚪  Đăng xuất")
        btn_logout.setStyleSheet(
            "QPushButton { text-align: left; padding: 10px 16px; border: none; "
            "font-size: 13px; color: #e53e3e; font-weight: bold; background: transparent; }"
            "QPushButton:hover { background-color: #fff5f5; }")
        btn_logout.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_logout.clicked.connect(lambda: (menu.close(), self._on_logout()))
        wa_logout = QWidgetAction(menu)
        wa_logout.setDefaultWidget(btn_logout)
        menu.addAction(wa_logout)

        pos = self.ui.lblAvatar.mapToGlobal(
            QPoint(self.ui.lblAvatar.width() - 220, self.ui.lblAvatar.height() + 5))
        menu.exec(pos)

    def _on_logout(self):
        """Đăng xuất với xác nhận."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Đăng xuất")
        dlg.setFixedSize(380, 220)
        dlg.setStyleSheet("QDialog { background-color: white; }")
        lay = QVBoxLayout(dlg)
        lay.setSpacing(10)
        lay.setContentsMargins(30, 25, 30, 25)

        icon = QLabel("🚪")
        icon.setStyleSheet("font-size: 40px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(icon)

        title = QLabel("Bạn có chắc muốn đăng xuất?")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a202c;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        sub = QLabel("Bạn sẽ quay lại trang đăng nhập")
        sub.setStyleSheet("color: #718096; font-size: 13px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(sub)
        lay.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_cancel = QPushButton("Hủy bỏ")
        btn_cancel.setMinimumHeight(42)
        btn_cancel.setStyleSheet(
            "QPushButton { background-color: #f7fafc; color: #4a5568; border: 1px solid #cbd5e0; "
            "border-radius: 8px; padding: 8px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #edf2f7; }")
        btn_cancel.clicked.connect(dlg.reject)

        btn_ok = QPushButton("🚪  Đăng xuất")
        btn_ok.setMinimumHeight(42)
        btn_ok.setStyleSheet(
            "QPushButton { background-color: #e53e3e; color: white; border: none; "
            "border-radius: 8px; padding: 8px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #c53030; }")
        btn_ok.clicked.connect(dlg.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        lay.addLayout(btn_row)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        from ui.UI_Common.views.auth_window import AuthWindow
        self._auth = AuthWindow(self.container)
        self._auth.show()
        self.close()

    def _do_logout(self):
        """Đăng xuất trực tiếp (đã xác nhận từ account view)."""
        from ui.UI_Common.views.auth_window import AuthWindow
        self._auth = AuthWindow(self.container)
        self._auth.show()
        self.close()
