
import json
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from config.constants import BASE_DIR

GUEST_NOTIF_FILE = os.path.join(BASE_DIR, 'data', 'guest_notifications.json')


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


# ══════════════════════════════════════════════════════
# Notification Row
# ══════════════════════════════════════════════════════
class GuestNotifRow(QFrame):
    def __init__(self, notif: dict, parent=None):
        super().__init__(parent)
        self.notif = notif
        self.setMinimumHeight(70)
        is_read = notif.get('read', False)
        self.setStyleSheet(
            "QFrame { border-bottom: 1px solid #edf2f7; "
            f"background-color: {'white' if is_read else '#f0fffe'}; }}"
            "QFrame:hover { background-color: #f7fafc; }")

        lo = QHBoxLayout(self)
        lo.setContentsMargins(25, 10, 25, 10)
        lo.setSpacing(15)

        # Icon circle
        icon = QLabel(notif.get('icon', 'ⓘ'))
        icon.setFixedSize(36, 36)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"background-color: {notif.get('icon_bg', '#edf2f7')}; "
            f"color: {notif.get('icon_color', '#718096')}; "
            f"border-radius: 18px; font-size: 16px; font-weight: bold; border: none;")
        lo.addWidget(icon)

        # Text
        text_lbl = QLabel(notif.get('text', ''))
        text_lbl.setWordWrap(True)
        if not is_read:
            text_lbl.setStyleSheet(
                "font-size: 13px; font-weight: bold; color: #2d3748; border: none;")
        else:
            text_lbl.setStyleSheet(
                "font-size: 13px; color: #4a5568; border: none;")
        lo.addWidget(text_lbl, 1)

        # Time
        time_lbl = QLabel(_time_ago(notif.get('time', '')))
        if not is_read:
            time_lbl.setStyleSheet(
                "font-size: 11px; color: #0b8480; font-weight: bold; border: none;")
        else:
            time_lbl.setStyleSheet(
                "font-size: 11px; color: #a0aec0; border: none;")
        lo.addWidget(time_lbl)

        # Unread dot
        if not is_read:
            dot = QLabel()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet(
                "background-color: #e53e3e; border-radius: 5px; border: none;")
            lo.addWidget(dot)


# ══════════════════════════════════════════════════════
# Main View
# ══════════════════════════════════════════════════════
class GuestNotifView(QWidget):
    TAB_STYLE = (
        "QPushButton { background-color: transparent; border: none; font-size: 13px; "
        "color: #718096; font-weight: bold; padding-bottom: 8px; }"
        "QPushButton:hover { color: #4a5568; }")
    TAB_ACTIVE = (
        "QPushButton { background-color: transparent; border: none; font-size: 13px; "
        "color: #0b8480; font-weight: bold; padding-bottom: 8px; "
        "border-bottom: 2px solid #0b8480; }")

    def __init__(self, user=None, contract_service=None, invoice_service=None,
                 room_service=None, guest_service=None, repair_service=None,
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.contract_service = contract_service
        self.invoice_service = invoice_service
        self.room_service = room_service
        self.guest_service = guest_service
        self.repair_service = repair_service

        self._active_tab = 'all'
        self._notifications = []
        self._build_ui()
        self._load_and_generate()

    # ── Build UI ──
    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(30, 30, 30, 30)
        main.setSpacing(0)

        card = QFrame()
        card.setObjectName("CardNotif")
        card.setStyleSheet(
            "QFrame#CardNotif { background-color: white; border-radius: 12px; "
            "border: 1px solid #e2e8f0; }")
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
        h_lay.setContentsMargins(25, 20, 25, 0)
        h_lay.setSpacing(15)

        title = QLabel("Thông báo")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(
            "color: #2d3748; border: none; background: transparent;")
        h_lay.addWidget(title)

        # Tabs
        tabs = QHBoxLayout()
        tabs.setSpacing(15)
        self._tab_buttons = []
        for text, key in [("Tất cả", "all"), ("Chưa đọc", "unread"),
                          ("Đã đọc", "read")]:
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
        scroll.setStyleSheet(
            "QScrollArea { border: none; background-color: transparent; }")
        self.list_container = QWidget()
        self.list_container.setStyleSheet("background-color: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)
        scroll.setWidget(self.list_container)
        card_lay.addWidget(scroll)

        main.addWidget(card)
        self._update_tab_styles()

    # ── Data Loading ──
    def _get_my_guest_ids(self):
        """Get all guest IDs belonging to this user."""
        user_id = int(getattr(self.user, 'id', 0) or 0)
        user_email = getattr(self.user, 'email', '') or ''
        ids = set()
        if self.guest_service:
            try:
                for g in self.guest_service.get_all_guests():
                    gid = int(getattr(g, 'user_id', 0) or 0)
                    g_email = getattr(g, 'email', '') or ''
                    if gid == user_id or (user_email and g_email and g_email.lower() == user_email.lower()):
                        ids.add(int(g.id))
            except Exception:
                pass
        return ids

    def _get_my_contracts(self, guest_ids):
        contracts = []
        if self.contract_service:
            try:
                for c in self.contract_service.contract_repo.get_all():
                    if int(getattr(c, 'guest_id', 0) or 0) in guest_ids:
                        contracts.append(c)
            except Exception:
                pass
        return contracts

    def _get_room_number(self, room_id):
        if self.room_service:
            try:
                room = self.room_service.get_room_by_id(int(room_id or 0))
                if room:
                    return room.room_number
            except Exception:
                pass
        return f"#{room_id}"

    def _load_and_generate(self):
        """Load saved + generate new notifications from live data."""
        saved = self._load_saved()
        generated = self._generate_notifications()

        existing_ids = {n['id'] for n in saved}
        for g in generated:
            if g['id'] not in existing_ids:
                saved.insert(0, g)

        # Sort by time desc
        def sort_key(n):
            try:
                return datetime.fromisoformat(n.get('time', ''))
            except Exception:
                return datetime.min
        saved.sort(key=sort_key, reverse=True)

        self._notifications = saved
        self._save_notifications()
        self._refresh()

    def _load_saved(self):
        if os.path.exists(GUEST_NOTIF_FILE):
            try:
                with open(GUEST_NOTIF_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Filter to only this user's notifications
                user_id = int(getattr(self.user, 'id', 0) or 0)
                return [n for n in data if n.get('user_id') == user_id]
            except Exception:
                pass
        return []

    def _save_notifications(self):
        user_id = int(getattr(self.user, 'id', 0) or 0)
        # Load all users' notifs, replace this user's
        all_notifs = []
        if os.path.exists(GUEST_NOTIF_FILE):
            try:
                with open(GUEST_NOTIF_FILE, 'r', encoding='utf-8') as f:
                    all_notifs = json.load(f)
            except Exception:
                all_notifs = []

        # Remove old notifs for this user
        all_notifs = [n for n in all_notifs if n.get('user_id') != user_id]

        # Add current user's notifs with user_id tag
        for n in self._notifications:
            item = dict(n)
            item['user_id'] = user_id
            if isinstance(item.get('time'), datetime):
                item['time'] = item['time'].isoformat()
            all_notifs.append(item)

        os.makedirs(os.path.dirname(GUEST_NOTIF_FILE), exist_ok=True)
        try:
            with open(GUEST_NOTIF_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_notifs, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _generate_notifications(self):
        notifs = []
        now = datetime.now()
        guest_ids = self._get_my_guest_ids()
        if not guest_ids:
            return notifs

        contracts = self._get_my_contracts(guest_ids)

        # ── Contract notifications ──
        for c in contracts:
            room_num = self._get_room_number(c.room_id)

            # Contract expiring soon
            if c.is_active() and c.end_date:
                days = c.days_until_expiry()
                if 0 < days <= 30:
                    notifs.append({
                        'id': f'g_exp_{c.id}',
                        'icon': '📄', 'icon_bg': '#ebf8ff', 'icon_color': '#3182ce',
                        'text': f'Hợp đồng phòng {room_num} của bạn sắp hết hạn ({days} ngày)',
                        'time': now.isoformat(), 'read': False,
                    })

            # Contract approved
            if c.status == 'active' and c.created_at:
                try:
                    created = datetime.fromisoformat(c.created_at)
                    if (now - created).days <= 7:
                        notifs.append({
                            'id': f'g_approved_{c.id}',
                            'icon': '✅', 'icon_bg': '#e6fffa', 'icon_color': '#38a169',
                            'text': f'Hợp đồng phòng {room_num} đã được duyệt',
                            'time': c.created_at, 'read': False,
                        })
                except Exception:
                    pass

            # Contract rejected
            if c.status == 'rejected':
                notifs.append({
                    'id': f'g_rejected_{c.id}',
                    'icon': '❌', 'icon_bg': '#fff5f5', 'icon_color': '#e53e3e',
                    'text': f'Yêu cầu đăng ký phòng {room_num} bị từ chối',
                    'time': c.updated_at or now.isoformat(), 'read': False,
                })

        # ── Invoice notifications ──
        if self.invoice_service and contracts:
            try:
                for ct in contracts:
                    ct_id = int(getattr(ct, 'id', 0) or 0)
                    invoices = self.invoice_service.get_by_contract(ct_id)
                    room_num = self._get_room_number(ct.room_id)

                    for inv in invoices:
                        # Unpaid invoice
                        if inv.status == 'unpaid':
                            notifs.append({
                                'id': f'g_inv_unpaid_{inv.id}',
                                'icon': '💰', 'icon_bg': '#fefcbf', 'icon_color': '#d69e2e',
                                'text': f'Hóa đơn tháng {inv.month}/{inv.year} phòng {room_num} chưa thanh toán',
                                'time': now.isoformat(), 'read': False,
                            })

                        # Overdue invoice
                        if inv.is_overdue():
                            notifs.append({
                                'id': f'g_inv_overdue_{inv.id}',
                                'icon': '⚠️', 'icon_bg': '#fed7d7', 'icon_color': '#c53030',
                                'text': f'Hóa đơn tháng {inv.month}/{inv.year} phòng {room_num} đã quá hạn!',
                                'time': now.isoformat(), 'read': False,
                            })

                        # Paid invoice (recent)
                        if inv.status == 'paid' and inv.payment_date:
                            try:
                                pd = datetime.fromisoformat(inv.payment_date)
                                if (now - pd).days <= 7:
                                    notifs.append({
                                        'id': f'g_inv_paid_{inv.id}',
                                        'icon': '💳', 'icon_bg': '#c6f6d5', 'icon_color': '#276749',
                                        'text': f'Phòng của bạn đã thanh toán tiền tháng {inv.month}/{inv.year}',
                                        'time': inv.payment_date, 'read': False,
                                    })
                            except Exception:
                                pass
            except Exception:
                pass

        # ── Repair request notifications ──
        if self.repair_service:
            try:
                all_repairs = self.repair_service.get_all()
                for r in all_repairs:
                    r_guest_id = int(getattr(r, 'guest_id', 0) or 0)
                    if r_guest_id not in guest_ids:
                        continue
                    room_num = self._get_room_number(r.room_id)

                    if r.status == 'in_progress':
                        notifs.append({
                            'id': f'g_repair_accept_{r.id}',
                            'icon': '🔧', 'icon_bg': '#ebf8ff', 'icon_color': '#2b6cb0',
                            'text': f'Yêu cầu sửa chữa "{r.title}" đã được tiếp nhận',
                            'time': r.updated_at or now.isoformat(), 'read': False,
                        })
                    elif r.status == 'completed':
                        notifs.append({
                            'id': f'g_repair_done_{r.id}',
                            'icon': '✅', 'icon_bg': '#c6f6d5', 'icon_color': '#276749',
                            'text': f'Sửa chữa "{r.title}" phòng {room_num} đã hoàn thành',
                            'time': r.completed_at or now.isoformat(), 'read': False,
                        })
                    elif r.status == 'rejected':
                        notifs.append({
                            'id': f'g_repair_reject_{r.id}',
                            'icon': '❌', 'icon_bg': '#fff5f5', 'icon_color': '#e53e3e',
                            'text': f'Yêu cầu sửa chữa "{r.title}" bị từ chối',
                            'time': r.updated_at or now.isoformat(), 'read': False,
                        })
            except Exception:
                pass

        return notifs

    # ── Tabs ──
    def _switch_tab(self, key):
        self._active_tab = key
        self._update_tab_styles()
        self._refresh()

    def _update_tab_styles(self):
        for btn, key in self._tab_buttons:
            btn.setStyleSheet(
                self.TAB_ACTIVE if key == self._active_tab else self.TAB_STYLE)

    def _mark_all_read(self):
        for n in self._notifications:
            n['read'] = True
        self._save_notifications()
        self._refresh()

    # ── Refresh ──
    def _refresh(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self._active_tab == 'unread':
            filtered = [n for n in self._notifications if not n.get('read')]
        elif self._active_tab == 'read':
            filtered = [n for n in self._notifications if n.get('read')]
        else:
            filtered = self._notifications

        for notif in filtered:
            row = GuestNotifRow(notif)
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            row.mousePressEvent = lambda ev, n=notif: self._on_click(n)
            self.list_layout.addWidget(row)

        if not filtered:
            empty = QLabel("Không có thông báo nào")
            empty.setStyleSheet(
                "color: #a0aec0; font-size: 14px; padding: 40px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.addWidget(empty)

        self.list_layout.addStretch()

    def _on_click(self, notif):
        notif['read'] = True
        self._save_notifications()
        QTimer.singleShot(0, self._refresh)
