"""
GuestWindow — Cửa sổ chính cho Khách thuê (Guest).
Load giao diện từ UI đã sinh, gắn sidebar navigation + sub-pages.
"""
import json
import os
from PyQt6.QtWidgets import (
    QMainWindow, QButtonGroup, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QMenu, QWidgetAction
)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QFont, QCursor
from ui.UI_Guest.generated.ui_guest_main_window import Ui_GuestMainWindow
from config.constants import BASE_DIR


class GuestWindow(QMainWindow):
    """Cửa sổ chính giao diện Guest (shell)."""

    # (sidebar button attr, page title, custom_builder or None)
    PAGE_DEFS = [
        ("btnNavMyRoom",   "Phòng của tôi",         "my_room"),
        ("btnNavInvoices", "Hóa đơn / Thanh toán",  "guest_invoice"),
        ("btnNavNotif",    "Thông báo",              "guest_notif"),
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

        # Setup header icons
        self._setup_header_icons()

        # Default page
        self._navigate(0)

    # ── Load Pages ──────────────────────────────────────────
    def _load_pages(self):
        stack = self.ui.stackGuestMain
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
        if builder == "guest_invoice":
            from ui.UI_Guest.views.guest_invoice_view import GuestInvoiceView
            return GuestInvoiceView(
                user=self.user,
                invoice_service=self.container.invoice_service if self.container else None,
                contract_service=self.container.contract_service if self.container else None,
                room_service=self.container.room_service if self.container else None,
                guest_service=self.container.guest_service if self.container else None,
            )
        if builder == "guest_notif":
            from ui.UI_Guest.views.guest_notif_view import GuestNotifView
            return GuestNotifView(
                user=self.user,
                contract_service=self.container.contract_service if self.container else None,
                invoice_service=self.container.invoice_service if self.container else None,
                room_service=self.container.room_service if self.container else None,
                guest_service=self.container.guest_service if self.container else None,
                repair_service=self.container.repair_request_service if self.container else None,
            )
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

    # ── Header Icons (Bell + Avatar) ─────────────────────
    def _setup_header_icons(self):
        self.ui.btnBell.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.ui.btnBell.clicked.connect(self._show_notif_popup)
        self.ui.lblAvatar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.ui.lblAvatar.mousePressEvent = lambda ev: self._show_avatar_popup()

    def _show_notif_popup(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: white; border: 1px solid #e2e8f0; "
            "border-radius: 8px; padding: 8px 0; min-width: 340px; }"
            "QMenu::item { padding: 0; }")

        # Header
        header_w = QWidget()
        header_lay = QHBoxLayout(header_w)
        header_lay.setContentsMargins(16, 10, 16, 6)
        lbl_title = QLabel("Thông báo")
        lbl_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #1a202c;")
        header_lay.addWidget(lbl_title)
        header_lay.addStretch()
        btn_all = QPushButton("Xem tất cả ›")
        btn_all.setStyleSheet(
            "QPushButton { color: #0b8480; border: none; font-size: 12px; "
            "font-weight: bold; } QPushButton:hover { text-decoration: underline; }")
        btn_all.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_all.clicked.connect(lambda: (menu.close(), self._navigate(2)))
        header_lay.addWidget(btn_all)
        wa_header = QWidgetAction(menu)
        wa_header.setDefaultWidget(header_w)
        menu.addAction(wa_header)

        # Load recent notifications
        notifs = self._load_recent_notifs(5)
        if notifs:
            for n in notifs:
                row_w = self._build_notif_row(n)
                row_w.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                row_w.mousePressEvent = lambda ev, m=menu: (
                    QTimer.singleShot(0, lambda: (m.close(), self._navigate(2)))
                )
                wa = QWidgetAction(menu)
                wa.setDefaultWidget(row_w)
                menu.addAction(wa)
        else:
            empty_w = QLabel("  Không có thông báo mới")
            empty_w.setStyleSheet("color: #a0aec0; font-size: 13px; padding: 15px;")
            empty_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
            wa = QWidgetAction(menu)
            wa.setDefaultWidget(empty_w)
            menu.addAction(wa)

        pos = self.ui.btnBell.mapToGlobal(
            QPoint(self.ui.btnBell.width() - 340, self.ui.btnBell.height() + 5))
        menu.exec(pos)

    def _build_notif_row(self, notif):
        row = QFrame()
        is_read = notif.get('read', False)
        row.setStyleSheet(
            f"QFrame {{ background-color: {'white' if is_read else '#f0fffe'}; "
            f"border-bottom: 1px solid #f0f0f0; }} "
            f"QFrame:hover {{ background-color: #f7fafc; }}")
        lo = QHBoxLayout(row)
        lo.setContentsMargins(16, 8, 16, 8)
        lo.setSpacing(10)

        icon = QLabel(notif.get('icon', 'ⓘ'))
        icon.setFixedSize(30, 30)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"background-color: {notif.get('icon_bg', '#edf2f7')}; "
            f"border-radius: 15px; font-size: 14px; border: none;")
        lo.addWidget(icon)

        text = QLabel(notif.get('text', ''))
        text.setWordWrap(True)
        text.setStyleSheet(
            f"font-size: 12px; color: {'#2d3748' if not is_read else '#718096'}; "
            f"{'font-weight: bold;' if not is_read else ''} border: none;")
        lo.addWidget(text, 1)

        if not is_read:
            dot = QLabel()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(
                "background-color: #e53e3e; border-radius: 4px; border: none;")
            lo.addWidget(dot)
        return row

    def _load_recent_notifs(self, limit=5):
        nf = os.path.join(BASE_DIR, 'data', 'guest_notifications.json')
        user_id = int(getattr(self.user, 'id', 0) or 0)
        if not os.path.exists(nf):
            return []
        try:
            with open(nf, 'r', encoding='utf-8') as f:
                data = json.load(f)
            mine = [n for n in data if n.get('user_id') == user_id]
            mine.sort(key=lambda n: n.get('time', ''), reverse=True)
            return mine[:limit]
        except Exception:
            return []

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
        user_name = getattr(self.user, 'full_name', 'Khách thuê') or 'Khách thuê'
        lbl_name = QLabel(user_name)
        lbl_name.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_name.setStyleSheet("color: #1a202c;")
        info_lay.addWidget(lbl_name)
        lbl_role = QLabel("🏠 Khách thuê")
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

        # Menu items
        for text, cb in [("👤  Quản lý tài khoản", lambda: self._navigate(3))]:
            btn = QPushButton(text)
            btn.setStyleSheet(
                "QPushButton { text-align: left; padding: 10px 16px; border: none; "
                "font-size: 13px; color: #2d3748; background: transparent; }"
                "QPushButton:hover { background-color: #f7fafc; }")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda _, c=cb: (menu.close(), c()))
            wa = QWidgetAction(menu)
            wa.setDefaultWidget(btn)
            menu.addAction(wa)

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
        btn_logout.clicked.connect(lambda: (menu.close(), self._confirm_and_logout()))
        wa_logout = QWidgetAction(menu)
        wa_logout.setDefaultWidget(btn_logout)
        menu.addAction(wa_logout)

        pos = self.ui.lblAvatar.mapToGlobal(
            QPoint(self.ui.lblAvatar.width() - 220, self.ui.lblAvatar.height() + 5))
        menu.exec(pos)

    def _confirm_and_logout(self):
        """Đăng xuất với xác nhận (từ avatar dropdown)."""
        from PyQt6.QtWidgets import QDialog
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
        self._do_logout()

    def _do_logout(self):
        """Đăng xuất → quay lại trang đăng nhập."""
        from ui.UI_Common.views.auth_window import AuthWindow
        self._auth = AuthWindow(self.container)
        self._auth.show()
        self.close()


