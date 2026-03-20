"""
NotificationView — Quản lý thông báo (trang Admin).
Hiển thị thông báo hệ thống + yêu cầu đăng ký phòng (pending contracts).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta


def _time_ago(dt) -> str:
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except Exception:
            return dt
    diff = datetime.now() - dt
    if diff.total_seconds() < 60:
        return "Vừa xong"
    elif diff.total_seconds() < 3600:
        return f"{int(diff.total_seconds()//60)} phút trước"
    elif diff.total_seconds() < 86400:
        return f"{int(diff.total_seconds()//3600)} giờ trước"
    elif diff.days == 1:
        return "Hôm qua"
    else:
        return f"{diff.days} ngày trước"


# ── Notification Row (thông báo thường) ───────────────────
class NotifRow(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, notif: dict, parent=None):
        super().__init__(parent)
        self.notif = notif
        self.setMinimumHeight(70)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            "QFrame { border-bottom: 1px solid #edf2f7; background-color: white; }"
            "QFrame:hover { background-color: #f7fafc; }")

        lo = QHBoxLayout(self)
        lo.setContentsMargins(30, 0, 30, 0)
        lo.setSpacing(20)

        icon = QLabel(notif['icon'])
        icon.setFixedSize(36, 36)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"background-color: {notif['icon_bg']}; color: {notif['icon_color']}; "
            f"border-radius: 18px; font-size: 16px; font-weight: bold; border: none;")
        lo.addWidget(icon)

        text_lbl = QLabel(notif['text'])
        if not notif['read']:
            text_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #2d3748; border: none;")
        else:
            text_lbl.setStyleSheet("font-size: 14px; color: #4a5568; border: none;")
        lo.addWidget(text_lbl)
        lo.addStretch()

        time_lbl = QLabel(_time_ago(notif['time']))
        if not notif['read']:
            time_lbl.setStyleSheet("font-size: 12px; color: #0b8480; font-weight: bold; border: none;")
        else:
            time_lbl.setStyleSheet("font-size: 12px; color: #a0aec0; border: none;")
        lo.addWidget(time_lbl)

        if not notif['read']:
            dot = QLabel()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet("background-color: #e53e3e; border-radius: 5px; border: none;")
            lo.addWidget(dot)

    def mousePressEvent(self, ev):
        self.clicked.emit(self.notif)
        super().mousePressEvent(ev)


# ── Pending Contract Row (yêu cầu đăng ký phòng) ────────
class PendingContractRow(QFrame):
    """Hiển thị 1 yêu cầu đăng ký phòng chờ duyệt."""
    approved = pyqtSignal(object)   # contract
    rejected = pyqtSignal(object)   # contract

    def __init__(self, contract, room_number: str, guest_name: str, parent=None):
        super().__init__(parent)
        self.contract = contract
        self.setMinimumHeight(90)
        self.setStyleSheet(
            "QFrame { border-bottom: 1px solid #edf2f7; background-color: #fffcf0; }"
            "QFrame:hover { background-color: #fefce8; }")

        lo = QHBoxLayout(self)
        lo.setContentsMargins(30, 10, 30, 10)
        lo.setSpacing(15)

        # Icon
        icon = QLabel("📋")
        icon.setFixedSize(40, 40)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            "background-color: #fef3c7; border-radius: 20px; font-size: 18px; border: none;")
        lo.addWidget(icon)

        # Info column
        info = QVBoxLayout()
        info.setSpacing(2)

        title = QLabel(f"Yêu cầu đăng ký phòng {room_number}")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #92400e; border: none;")
        info.addWidget(title)

        detail = QLabel(f"Khách: {guest_name}  •  HĐ: {contract.contract_number}  •  "
                        f"Giá: {contract.monthly_rent:,.0f} VNĐ/tháng")
        detail.setStyleSheet("font-size: 12px; color: #78716c; border: none;")
        detail.setWordWrap(True)
        info.addWidget(detail)

        time_text = _time_ago(contract.created_at) if contract.created_at else ""
        time_lbl = QLabel(time_text)
        time_lbl.setStyleSheet("font-size: 11px; color: #a8a29e; border: none;")
        info.addWidget(time_lbl)

        lo.addLayout(info, 1)

        # Action buttons
        btn_approve = QPushButton("✅ Duyệt")
        btn_approve.setMinimumHeight(36)
        btn_approve.setStyleSheet(
            "QPushButton { background-color: #059669; color: white; border: none; "
            "border-radius: 6px; padding: 6px 16px; font-weight: bold; font-size: 12px; }"
            "QPushButton:hover { background-color: #047857; }")
        btn_approve.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_approve.clicked.connect(lambda: self.approved.emit(self.contract))
        lo.addWidget(btn_approve)

        btn_reject = QPushButton("❌ Từ chối")
        btn_reject.setMinimumHeight(36)
        btn_reject.setStyleSheet(
            "QPushButton { background-color: #f7fafc; color: #e53e3e; border: 1px solid #fecaca; "
            "border-radius: 6px; padding: 6px 16px; font-weight: bold; font-size: 12px; }"
            "QPushButton:hover { background-color: #fef2f2; }")
        btn_reject.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reject.clicked.connect(lambda: self.rejected.emit(self.contract))
        lo.addWidget(btn_reject)


# ── Main View ────────────────────────────────────────────
class NotificationView(QWidget):
    """Widget thông báo — nhúng AdminWindow."""
    navigate_requested = pyqtSignal(str)

    TAB_STYLE = (
        "QPushButton { background-color: transparent; border: none; font-size: 14px; "
        "color: #718096; font-weight: bold; padding-bottom: 8px; }"
        "QPushButton:hover { color: #4a5568; }")
    TAB_ACTIVE = (
        "QPushButton { background-color: transparent; border: none; font-size: 14px; "
        "color: #0b8480; font-weight: bold; padding-bottom: 8px; "
        "border-bottom: 2px solid #0b8480; }")

    def __init__(self, contract_service=None, room_service=None, guest_service=None, parent=None):
        super().__init__(parent)
        self.contract_service = contract_service
        self.room_service = room_service
        self.guest_service = guest_service
        self._notifications = self._generate_system_notifications()
        self._active_tab = 'all'
        self._build_ui()
        self._refresh()

    def _generate_system_notifications(self):
        """Tạo thông báo hệ thống từ dữ liệu thật."""
        notifs = []
        now = datetime.now()

        # Hợp đồng sắp hết hạn
        if self.contract_service:
            expiring = self.contract_service.get_expiring_soon(30)
            for c in expiring:
                room_num = self._get_room_number(c.room_id)
                notifs.append({
                    'id': f'exp_{c.id}', 'icon': '📄', 'icon_bg': '#ebf8ff', 'icon_color': '#3182ce',
                    'text': f'Hợp đồng phòng {room_num} sắp hết hạn ({c.days_until_expiry()} ngày)',
                    'time': now - timedelta(hours=1), 'read': False, 'target': 'guest',
                })

        # Thêm vài thông báo mẫu nếu chưa có gì
        if not notifs:
            notifs.append({
                'id': 'sys_1', 'icon': 'ⓘ', 'icon_bg': '#edf2f7', 'icon_color': '#718096',
                'text': 'Hệ thống hoạt động bình thường', 'time': now - timedelta(hours=2),
                'read': True, 'target': '',
            })

        return notifs

    def _get_room_number(self, room_id):
        if self.room_service:
            room = self.room_service.get_room_by_id(room_id)
            if room:
                return room.room_number
        return f"#{room_id}"

    def _get_guest_name(self, guest_id):
        if self.guest_service:
            guest = self.guest_service.get_guest_by_id(guest_id)
            if guest:
                return guest.full_name
        return f"Khách #{guest_id}"

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(40, 40, 40, 40)
        main.setSpacing(0)

        card = QFrame()
        card.setStyleSheet(
            "QFrame#CardThongBao { background-color: white; border-radius: 12px; "
            "border: 1px solid #e2e8f0; }")
        card.setObjectName("CardThongBao")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(0, 0, 0, 0)
        card_lay.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet(
            "background-color: #ebf4f4; border-top-left-radius: 12px; "
            "border-top-right-radius: 12px;")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(30, 25, 30, 0)
        h_lay.setSpacing(20)

        title = QLabel("Thông báo")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2d3748; border: none; background: transparent;")
        h_lay.addWidget(title)

        tabs = QHBoxLayout()
        tabs.setSpacing(20)
        self._tab_buttons = []
        for text, key in [("Tất cả", "all"), ("Yêu cầu duyệt", "pending"), ("Đã đọc", "read")]:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._switch_tab(k))
            self._tab_buttons.append((btn, key))
            tabs.addWidget(btn)
        tabs.addStretch()

        self.btn_mark_all = QPushButton("Đã đọc tất cả")
        self.btn_mark_all.setStyleSheet(
            "QPushButton { background-color: #0b8480; color: white; border-radius: 6px; "
            "padding: 6px 15px; font-weight: bold; font-size: 12px; border: none; }"
            "QPushButton:hover { background-color: #096c69; }")
        self.btn_mark_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mark_all.clicked.connect(self._mark_all_read)
        tabs.addWidget(self.btn_mark_all)
        h_lay.addLayout(tabs)

        card_lay.addWidget(header)

        # Scrollable list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.list_container = QWidget()
        self.list_container.setStyleSheet("background-color: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)
        scroll.setWidget(self.list_container)
        card_lay.addWidget(scroll)

        main.addWidget(card)
        self._update_tab_styles()

    def _switch_tab(self, key):
        self._active_tab = key
        self._update_tab_styles()
        self._refresh()

    def _update_tab_styles(self):
        for btn, key in self._tab_buttons:
            btn.setStyleSheet(self.TAB_ACTIVE if key == self._active_tab else self.TAB_STYLE)

    def _refresh(self):
        # Clear
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # ── Pending contracts section ──
        pending_contracts = []
        if self.contract_service:
            all_contracts = self.contract_service.get_all()
            pending_contracts = [c for c in all_contracts if c.status == 'pending']

        # Show pending contracts
        if self._active_tab in ('all', 'pending') and pending_contracts:
            # Section header
            sec_header = QLabel(f"  📋  Yêu cầu đăng ký phòng ({len(pending_contracts)})")
            sec_header.setFixedHeight(40)
            sec_header.setStyleSheet(
                "background-color: #fef3c7; color: #92400e; font-weight: bold; "
                "font-size: 13px; padding-left: 20px; border: none;")
            self.list_layout.addWidget(sec_header)

            for contract in pending_contracts:
                room_num = self._get_room_number(contract.room_id)
                guest_name = self._get_guest_name(contract.guest_id)
                row = PendingContractRow(contract, room_num, guest_name)
                row.approved.connect(self._on_approve)
                row.rejected.connect(self._on_reject)
                self.list_layout.addWidget(row)

        # ── Regular notifications ──
        if self._active_tab != 'pending':
            if self._active_tab == 'read':
                filtered = [n for n in self._notifications if n['read']]
            else:
                filtered = self._notifications

            for notif in filtered:
                row = NotifRow(notif)
                row.clicked.connect(self._on_click)
                self.list_layout.addWidget(row)

        # Empty state
        if self.list_layout.count() == 0:
            empty = QLabel("Không có thông báo nào")
            empty.setStyleSheet("color: #a0aec0; font-size: 14px; padding: 40px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.addWidget(empty)

        self.list_layout.addStretch()

    # ── Approve / Reject ──
    def _on_approve(self, contract):
        room_num = self._get_room_number(contract.room_id)
        guest_name = self._get_guest_name(contract.guest_id)

        # Custom confirm dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Xác nhận duyệt")
        dlg.setFixedSize(420, 280)
        dlg.setStyleSheet("QDialog { background-color: white; }")
        lay = QVBoxLayout(dlg)
        lay.setSpacing(12)
        lay.setContentsMargins(30, 25, 30, 25)

        icon = QLabel("📋")
        icon.setStyleSheet("font-size: 40px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(icon)

        title = QLabel("Duyệt yêu cầu đăng ký phòng?")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a202c;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        info = QLabel(
            f"Phòng: <b>{room_num}</b><br>"
            f"Khách thuê: <b>{guest_name}</b><br>"
            f"Hợp đồng: <b>{contract.contract_number}</b><br>"
            f"Giá thuê: <b>{contract.monthly_rent:,.0f} VNĐ/tháng</b>"
        )
        info.setStyleSheet("color: #4a5568; font-size: 13px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        lay.addWidget(info)
        lay.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_cancel = QPushButton("Hủy bỏ")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setStyleSheet(
            "QPushButton { background-color: #f7fafc; color: #4a5568; border: 1px solid #cbd5e0; "
            "border-radius: 8px; padding: 8px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #edf2f7; }")
        btn_cancel.clicked.connect(dlg.reject)

        btn_ok = QPushButton("✅  Duyệt yêu cầu")
        btn_ok.setMinimumHeight(40)
        btn_ok.setStyleSheet(
            "QPushButton { background-color: #059669; color: white; border: none; "
            "border-radius: 8px; padding: 8px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #047857; }")
        btn_ok.clicked.connect(dlg.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        lay.addLayout(btn_row)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        # Cập nhật contract → active
        contract.status = 'active'
        self.contract_service.contract_repo.update(contract)

        # Cập nhật room → occupied
        if self.room_service:
            room = self.room_service.get_room_by_id(contract.room_id)
            if room:
                room.status = 'occupied'
                self.room_service.update_room(room)

        # Thêm thông báo đã duyệt
        self._notifications.insert(0, {
            'id': f'approved_{contract.id}', 'icon': '✅', 'icon_bg': '#e6fffa', 'icon_color': '#38a169',
            'text': f'Đã duyệt đăng ký phòng {room_num} — HĐ {contract.contract_number}',
            'time': datetime.now(), 'read': False, 'target': 'guest',
        })

        # Success dialog
        self._show_result_dialog(
            "✅", "#059669", "Duyệt thành công!",
            f"Phòng: <b>{room_num}</b><br>"
            f"Khách: <b>{guest_name}</b><br>"
            f"Hợp đồng <b>{contract.contract_number}</b> đã được kích hoạt."
        )
        self._refresh()

    def _on_reject(self, contract):
        room_num = self._get_room_number(contract.room_id)
        guest_name = self._get_guest_name(contract.guest_id)

        # Custom confirm dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Xác nhận từ chối")
        dlg.setFixedSize(420, 250)
        dlg.setStyleSheet("QDialog { background-color: white; }")
        lay = QVBoxLayout(dlg)
        lay.setSpacing(12)
        lay.setContentsMargins(30, 25, 30, 25)

        icon = QLabel("⚠️")
        icon.setStyleSheet("font-size: 40px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(icon)

        title = QLabel("Từ chối yêu cầu đăng ký?")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a202c;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        info = QLabel(
            f"Phòng: <b>{room_num}</b>  •  Khách: <b>{guest_name}</b><br>"
            f"Hợp đồng: <b>{contract.contract_number}</b>"
        )
        info.setStyleSheet("color: #4a5568; font-size: 13px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        lay.addWidget(info)
        lay.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_cancel = QPushButton("Hủy bỏ")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setStyleSheet(
            "QPushButton { background-color: #f7fafc; color: #4a5568; border: 1px solid #cbd5e0; "
            "border-radius: 8px; padding: 8px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #edf2f7; }")
        btn_cancel.clicked.connect(dlg.reject)

        btn_ok = QPushButton("❌  Từ chối")
        btn_ok.setMinimumHeight(40)
        btn_ok.setStyleSheet(
            "QPushButton { background-color: #dc2626; color: white; border: none; "
            "border-radius: 8px; padding: 8px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #b91c1c; }")
        btn_ok.clicked.connect(dlg.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        lay.addLayout(btn_row)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        # Cập nhật contract → rejected
        contract.status = 'rejected'
        self.contract_service.contract_repo.update(contract)

        # Thêm thông báo đã từ chối
        self._notifications.insert(0, {
            'id': f'rejected_{contract.id}', 'icon': '❌', 'icon_bg': '#fff5f5', 'icon_color': '#e53e3e',
            'text': f'Đã từ chối yêu cầu phòng {room_num} — HĐ {contract.contract_number}',
            'time': datetime.now(), 'read': False, 'target': '',
        })

        self._show_result_dialog(
            "❌", "#dc2626", "Đã từ chối",
            f"Yêu cầu đăng ký phòng <b>{room_num}</b> đã bị từ chối."
        )
        self._refresh()

    def _show_result_dialog(self, emoji, color, title_text, body_html):
        dlg = QDialog(self)
        dlg.setWindowTitle(title_text)
        dlg.setFixedSize(400, 230)
        dlg.setStyleSheet("QDialog { background-color: white; }")
        lay = QVBoxLayout(dlg)
        lay.setSpacing(10)
        lay.setContentsMargins(30, 25, 30, 25)

        icon = QLabel(emoji)
        icon.setStyleSheet("font-size: 44px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(icon)

        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {color};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        body = QLabel(body_html)
        body.setStyleSheet("color: #4a5568; font-size: 13px;")
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body.setWordWrap(True)
        lay.addWidget(body)
        lay.addStretch()

        btn = QPushButton("Đã hiểu")
        btn.setMinimumHeight(40)
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {color}; color: white; border: none; "
            f"border-radius: 8px; padding: 8px; font-weight: bold; font-size: 13px; }}"
            f"QPushButton:hover {{ opacity: 0.9; }}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)
        dlg.exec()

    def _mark_all_read(self):
        for n in self._notifications:
            n['read'] = True
        self._refresh()

    def _on_click(self, notif):
        notif['read'] = True
        self._refresh()
        self.navigate_requested.emit(notif.get('target', ''))

    def get_unread_count(self) -> int:
        count = sum(1 for n in self._notifications if not n['read'])
        # Count pending contracts too
        if self.contract_service:
            pending = [c for c in self.contract_service.get_all() if c.status == 'pending']
            count += len(pending)
        return count
