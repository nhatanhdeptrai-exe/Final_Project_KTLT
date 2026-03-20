"""
NotificationView — Quản lý thông báo (trang Admin).
Hiển thị danh sách thông báo với tabs Tất cả / Chưa đọc / Đã đọc.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta


# ── Sample notification data ─────────────────────────────
def _generate_sample_notifications():
    now = datetime.now()
    return [
        {'id': 1, 'icon': '💰', 'icon_bg': '#e6fffa', 'icon_color': '#38a169',
         'text': 'Phòng P101 đã thanh toán tiền', 'time': now - timedelta(minutes=2),
         'read': False, 'target': 'invoice'},
        {'id': 2, 'icon': '🔧', 'icon_bg': '#fffaf0', 'icon_color': '#dd6b20',
         'text': 'Phòng P202 yêu cầu sửa vòi nước', 'time': now - timedelta(hours=1),
         'read': False, 'target': 'repair'},
        {'id': 3, 'icon': '📄', 'icon_bg': '#ebf8ff', 'icon_color': '#3182ce',
         'text': 'Hợp đồng phòng P303 sắp hết hạn', 'time': now - timedelta(days=1),
         'read': True, 'target': 'guest'},
        {'id': 4, 'icon': 'ⓘ', 'icon_bg': '#edf2f7', 'icon_color': '#718096',
         'text': 'Có người mới chuyển vào phòng P401', 'time': now - timedelta(days=1),
         'read': True, 'target': 'room'},
        {'id': 5, 'icon': '💰', 'icon_bg': '#e6fffa', 'icon_color': '#38a169',
         'text': 'Phòng P201 chưa thanh toán tiền điện tháng này', 'time': now - timedelta(days=2),
         'read': True, 'target': 'invoice'},
        {'id': 6, 'icon': '🔧', 'icon_bg': '#fffaf0', 'icon_color': '#dd6b20',
         'text': 'Đã hoàn tất sửa chữa điều hòa phòng P103', 'time': now - timedelta(days=3),
         'read': True, 'target': 'repair'},
    ]


def _time_ago(dt: datetime) -> str:
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


# ── Notification Row Widget ──────────────────────────────
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

        # Icon
        icon = QLabel(notif['icon'])
        icon.setFixedSize(36, 36)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"background-color: {notif['icon_bg']}; color: {notif['icon_color']}; "
            f"border-radius: 18px; font-size: 16px; font-weight: bold; border: none;")
        lo.addWidget(icon)

        # Text
        text_lbl = QLabel(notif['text'])
        if not notif['read']:
            text_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #2d3748; border: none;")
        else:
            text_lbl.setStyleSheet("font-size: 14px; color: #4a5568; border: none;")
        lo.addWidget(text_lbl)
        lo.addStretch()

        # Time
        time_lbl = QLabel(_time_ago(notif['time']))
        if not notif['read']:
            time_lbl.setStyleSheet("font-size: 12px; color: #0b8480; font-weight: bold; border: none;")
        else:
            time_lbl.setStyleSheet("font-size: 12px; color: #a0aec0; border: none;")
        lo.addWidget(time_lbl)

        # Red dot for unread
        if not notif['read']:
            dot = QLabel()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet("background-color: #e53e3e; border-radius: 5px; border: none;")
            lo.addWidget(dot)

    def mousePressEvent(self, ev):
        self.clicked.emit(self.notif)
        super().mousePressEvent(ev)


# ── Main View ────────────────────────────────────────────
class NotificationView(QWidget):
    """Widget thông báo — nhúng AdminWindow."""
    navigate_requested = pyqtSignal(str)  # target: 'invoice', 'repair', 'room', 'guest'

    TAB_STYLE = (
        "QPushButton { background-color: transparent; border: none; font-size: 14px; "
        "color: #718096; font-weight: bold; padding-bottom: 8px; }"
        "QPushButton:hover { color: #4a5568; }")
    TAB_ACTIVE = (
        "QPushButton { background-color: transparent; border: none; font-size: 14px; "
        "color: #0b8480; font-weight: bold; padding-bottom: 8px; "
        "border-bottom: 2px solid #0b8480; }")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._notifications = _generate_sample_notifications()
        self._active_tab = 'all'
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(40, 40, 40, 40)
        main.setSpacing(0)

        # Card
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

        # Tabs row
        tabs = QHBoxLayout(); tabs.setSpacing(20)
        self._tab_buttons = []
        for text, key in [("Tất cả", "all"), ("Chưa đọc", "unread"), ("Đã đọc", "read")]:
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

        # Filter
        if self._active_tab == 'unread':
            filtered = [n for n in self._notifications if not n['read']]
        elif self._active_tab == 'read':
            filtered = [n for n in self._notifications if n['read']]
        else:
            filtered = self._notifications

        if not filtered:
            empty = QLabel("Không có thông báo nào")
            empty.setStyleSheet("color: #a0aec0; font-size: 14px; padding: 40px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.addWidget(empty)
        else:
            for notif in filtered:
                row = NotifRow(notif)
                row.clicked.connect(self._on_click)
                self.list_layout.addWidget(row)

        self.list_layout.addStretch()

    def _mark_all_read(self):
        for n in self._notifications:
            n['read'] = True
        self._refresh()

    def _on_click(self, notif):
        notif['read'] = True
        self._refresh()
        self.navigate_requested.emit(notif.get('target', ''))

    def get_unread_count(self) -> int:
        return sum(1 for n in self._notifications if not n['read'])
