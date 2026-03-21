"""
DashboardView — Trang chủ Admin với dữ liệu thật từ backend services.
Hiển thị: 4 stat cards, biểu đồ doanh thu 6 tháng, phòng chưa đóng tiền,
hoạt động gần đây.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QScrollArea, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QCursor, QColor, QPainter, QPen, QBrush
from datetime import datetime, date
import traceback

# QtCharts removed — causes segfault on some systems.
# Using QPainter-based chart for maximum compatibility.

MONTH_NAMES = ['', 'Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
               'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12']


class DashboardView(QWidget):
    """Trang chủ Admin — hiển thị tổng quan dữ liệu thật."""

    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        self.setObjectName("pageTrangChu")
        self.setStyleSheet("""
            QWidget#pageTrangChu { background-color: #f0f4f7; }
        """)
        self._build_ui()
        try:
            self.load_data()
        except Exception as e:
            print(f"[Dashboard] Error during initial load: {e}")
            traceback.print_exc()

    # ══════════════════════════════════════════════════════════
    #  BUILD UI
    # ══════════════════════════════════════════════════════════
    def _build_ui(self):
        # Outer scroll area for entire page
        page_outer = QVBoxLayout(self)
        page_outer.setContentsMargins(0, 0, 0, 0)
        page_scroll = QScrollArea()
        page_scroll.setWidgetResizable(True)
        page_scroll.setStyleSheet("QScrollArea { border: none; background-color: #f0f4f7; }")
        page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        page_content = QWidget()
        page_content.setStyleSheet("background-color: #f0f4f7;")
        root = QVBoxLayout(page_content)
        root.setContentsMargins(30, 20, 30, 20)
        root.setSpacing(20)

        # ── Header row ──
        header = QHBoxLayout()
        left = QVBoxLayout(); left.setSpacing(2)
        t = QLabel("Tổng quan"); t.setStyleSheet("font-size: 18px; font-weight: bold; color: #2d3748;"); left.addWidget(t)
        s = QLabel("Theo dõi hoạt động và tình hình kinh doanh của phòng trọ."); s.setStyleSheet("color: #718096; font-size: 13px;"); left.addWidget(s)
        header.addLayout(left); header.addStretch()
        now = datetime.now()
        self.lblMonth = QPushButton(f"Tháng {now.month}, {now.year}")
        self.lblMonth.setStyleSheet("background-color: white; border: 1px solid #cbd5e0; border-radius: 15px; padding: 8px 15px; color: #4a5568;")
        header.addWidget(self.lblMonth)
        root.addLayout(header)

        # ── 4 Stat Cards ──
        cards_row = QHBoxLayout(); cards_row.setSpacing(20)
        self.card_revenue   = self._make_card("Doanh thu\ntháng này", "$", "#e6fffa", "#0b8480")
        self.card_rooms     = self._make_card("Phòng\nđang trống", "🚪", "#f7fafc", "#4a5568")
        self.card_contracts = self._make_card("Hợp đồng\nsắp hết hạn", "📜", "#fffaf0", "#dd6b20")
        self.card_repairs   = self._make_card("Yêu cầu sửa\nchữa mới", "⚠️", "#fff5f5", "#e53e3e")
        for card, _ in [self.card_revenue, self.card_rooms, self.card_contracts, self.card_repairs]:
            cards_row.addWidget(card)
        root.addLayout(cards_row)

        # ── Middle row: Chart + Unpaid ──
        mid_row = QHBoxLayout(); mid_row.setSpacing(20)

        # Chart frame
        self.chartFrame = self._make_frame()
        self.chartFrame.setMinimumSize(QSize(580, 350))
        chart_lay = QVBoxLayout(self.chartFrame)
        chart_lay.setContentsMargins(20, 20, 20, 15)
        lbl_chart_title = QLabel("Doanh thu 6 tháng gần nhất")
        lbl_chart_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d3748;")
        chart_lay.addWidget(lbl_chart_title)
        lbl_chart_unit = QLabel("Đơn vị: Triệu VNĐ")
        lbl_chart_unit.setStyleSheet("color: #718096; font-size: 12px;")
        chart_lay.addWidget(lbl_chart_unit)
        self.chartContainer = QWidget()
        self.chartContainer.setStyleSheet("background-color: transparent;")
        self.chartContainerLayout = QVBoxLayout(self.chartContainer)
        self.chartContainerLayout.setContentsMargins(0, 0, 0, 0)
        chart_lay.addWidget(self.chartContainer, 1)
        mid_row.addWidget(self.chartFrame, 6)

        # Unpaid frame
        self.unpaidFrame = self._make_frame()
        self.unpaidFrame.setMinimumSize(QSize(340, 350))
        unpaid_lay = QVBoxLayout(self.unpaidFrame)
        unpaid_lay.setContentsMargins(20, 20, 20, 10)
        unpaid_lay.setSpacing(10)
        self.lblUnpaidTitle = QLabel("Phòng chưa đóng tiền")
        self.lblUnpaidTitle.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d3748;")
        unpaid_lay.addWidget(self.lblUnpaidTitle)
        self.lblUnpaidSub = QLabel("0 phòng đang quá hạn")
        self.lblUnpaidSub.setStyleSheet("color: #718096; font-size: 12px;")
        unpaid_lay.addWidget(self.lblUnpaidSub)
        unpaid_scroll = QScrollArea()
        unpaid_scroll.setWidgetResizable(True)
        unpaid_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.unpaidListWidget = QWidget()
        self.unpaidListWidget.setStyleSheet("background-color: transparent;")
        self.unpaidListLayout = QVBoxLayout(self.unpaidListWidget)
        self.unpaidListLayout.setContentsMargins(0, 0, 5, 0)
        self.unpaidListLayout.setSpacing(10)
        unpaid_scroll.setWidget(self.unpaidListWidget)
        unpaid_lay.addWidget(unpaid_scroll, 1)
        mid_row.addWidget(self.unpaidFrame, 4)
        root.addLayout(mid_row)

        # ── Activities ──
        self.activitiesFrame = self._make_frame()
        act_lay = QVBoxLayout(self.activitiesFrame)
        act_lay.setContentsMargins(20, 20, 20, 15)
        act_lay.setSpacing(8)
        self.lblActTitle = QLabel("Hoạt động gần đây")
        self.lblActTitle.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d3748;")
        act_lay.addWidget(self.lblActTitle)
        self.lblActSub = QLabel("0 hoạt động trong tuần này")
        self.lblActSub.setStyleSheet("color: #718096; font-size: 12px;")
        act_lay.addWidget(self.lblActSub)
        self.activitiesContainer = QVBoxLayout()
        self.activitiesContainer.setSpacing(0)
        act_lay.addLayout(self.activitiesContainer)
        root.addWidget(self.activitiesFrame)

        # Set scroll content
        page_scroll.setWidget(page_content)
        page_outer.addWidget(page_scroll)

    # ══════════════════════════════════════════════════════════
    #  LOAD DATA
    # ══════════════════════════════════════════════════════════
    def load_data(self):
        """Load dữ liệu thật từ services và cập nhật UI."""
        if not self.container:
            return
        for loader_name, loader in [
            ('stat_cards', self._load_stat_cards),
            ('chart', self._load_chart),
            ('unpaid_rooms', self._load_unpaid_rooms),
            ('activities', self._load_activities),
        ]:
            try:
                loader()
            except Exception as e:
                print(f"[Dashboard] Error loading {loader_name}: {e}")
                traceback.print_exc()

    # ── Stat Cards ───────────────────────────────────────────
    def _load_stat_cards(self):
        now = datetime.now()
        month, year = now.month, now.year

        # 1. Doanh thu tháng này
        report_svc = self.container.report_service
        rev_data = report_svc.revenue_by_month(month, year)
        total_rev = rev_data.get('total_revenue', 0)

        # So sánh % với tháng trước
        prev_m, prev_y = (month - 1, year) if month > 1 else (12, year - 1)
        prev_data = report_svc.revenue_by_month(prev_m, prev_y)
        prev_rev = prev_data.get('total_revenue', 0)
        if prev_rev > 0:
            pct = ((total_rev - prev_rev) / prev_rev) * 100
            pct_text = f"+{pct:.0f}% so với tháng trước" if pct >= 0 else f"{pct:.0f}% so với tháng trước"
        else:
            pct_text = "Chưa có dữ liệu tháng trước"

        self._update_card(self.card_revenue, f"{total_rev:,.0f} đ".replace(",", "."), pct_text, is_teal=True)

        # 2. Phòng đang trống
        room_svc = self.container.room_service
        stats = room_svc.get_statistics()
        available = stats.get('available', 0)
        total = stats.get('total', 0)
        self._update_card(self.card_rooms, str(available), f"Trên tổng số {total} phòng")

        # 3. Hợp đồng sắp hết hạn
        contract_svc = self.container.contract_service
        expiring = contract_svc.get_expiring_soon(30)
        self._update_card(self.card_contracts, str(len(expiring)), "Trong vòng 30 ngày tới")

        # 4. Yêu cầu sửa chữa mới
        repair_svc = self.container.repair_request_service
        pending = repair_svc.get_pending()
        urgent = len([r for r in pending if getattr(r, 'priority', '') in ('urgent', 'high')])
        normal = len(pending) - urgent
        if urgent > 0 and normal > 0:
            sub = f"{urgent} khẩn cấp, {normal} bình thường"
        elif urgent > 0:
            sub = f"{urgent} khẩn cấp"
        elif normal > 0:
            sub = f"{normal} bình thường"
        else:
            sub = "Không có yêu cầu mới"
        self._update_card(self.card_repairs, str(len(pending)), sub)

    # ── Revenue Chart ────────────────────────────────────────
    def _load_chart(self):
        now = datetime.now()
        months_data = []
        for i in range(5, -1, -1):
            m = now.month - i
            y = now.year
            while m <= 0:
                m += 12; y -= 1
            # Get all invoices for this month/year
            all_inv = self.container.invoice_service.get_all()
            month_invs = [inv for inv in all_inv if int(inv.month) == m and int(inv.year) == y]

            rent_total = sum(int(inv.room_rent or 0) for inv in month_invs if inv.status == 'paid')
            utility_total = sum(int(inv.electricity_cost or 0) + int(inv.water_cost or 0) for inv in month_invs if inv.status == 'paid')
            months_data.append({
                'month': m, 'year': y,
                'label': MONTH_NAMES[m],
                'rent': rent_total / 1_000_000,       # → triệu VNĐ
                'utility': utility_total / 1_000_000,
            })

        # Clear existing chart
        while self.chartContainerLayout.count():
            item = self.chartContainerLayout.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()

        self._build_painter_chart(months_data)

    def _build_painter_chart(self, months_data):
        """Fallback: simple QPainter bar chart widget."""
        chart_widget = _PainterBarChart(months_data)
        self.chartContainerLayout.addWidget(chart_widget)

    # ── Unpaid Rooms ─────────────────────────────────────────
    def _load_unpaid_rooms(self):
        # Clear old items
        while self.unpaidListLayout.count():
            item = self.unpaidListLayout.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()

        invoice_svc = self.container.invoice_service
        overdue_invoices = invoice_svc.get_overdue()

        # Also include unpaid (not overdue yet)
        unpaid_invoices = invoice_svc.get_unpaid()
        # Merge: overdue first, then other unpaid
        overdue_ids = {inv.id for inv in overdue_invoices}
        all_unpaid = overdue_invoices + [inv for inv in unpaid_invoices if inv.id not in overdue_ids]

        self.lblUnpaidSub.setText(f"{len(overdue_invoices)} phòng đang quá hạn")

        contract_svc = self.container.contract_service
        room_svc = self.container.room_service

        for inv in all_unpaid[:10]:  # Show max 10
            contract = contract_svc.get_by_id(int(inv.contract_id))
            room_number = "?"
            if contract:
                room = room_svc.get_room_by_id(int(contract.room_id))
                if room:
                    room_number = room.room_number

            days = inv.days_overdue()
            row = self._make_unpaid_row(
                f"Phòng {room_number}",
                f"{int(inv.total_amount):,} đ".replace(",", "."),
                f"Trễ {days} ngày" if days > 0 else "Chưa đến hạn",
                inv
            )
            self.unpaidListLayout.addWidget(row)

        self.unpaidListLayout.addStretch()

    def _make_unpaid_row(self, room_name, amount, delay_text, invoice):
        frame = QFrame()
        frame.setStyleSheet("background-color: #f7fafc; border-radius: 8px; padding: 5px;")
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(12, 8, 12, 8)

        info_lay = QVBoxLayout()
        info_lay.setSpacing(2)
        lbl_room = QLabel(room_name)
        lbl_room.setStyleSheet("font-weight: bold; color: #2d3748; font-size: 13px;")
        info_lay.addWidget(lbl_room)

        detail_lay = QHBoxLayout()
        detail_lay.setSpacing(8)
        lbl_amount = QLabel(amount)
        lbl_amount.setStyleSheet("color: #e53e3e; font-weight: bold; font-size: 13px;")
        detail_lay.addWidget(lbl_amount)
        lbl_delay = QLabel(delay_text)
        lbl_delay.setStyleSheet("color: #a0aec0; font-size: 11px;")
        detail_lay.addWidget(lbl_delay)
        detail_lay.addStretch()
        info_lay.addLayout(detail_lay)
        lay.addLayout(info_lay, 1)

        btn = QPushButton("🔔 Nhắc nhở")
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet(
            "QPushButton { background-color: #e6fffa; color: #0b8480; border: none; "
            "border-radius: 6px; padding: 6px 12px; font-weight: bold; font-size: 12px; }"
            "QPushButton:hover { background-color: #b2f5ea; }")
        btn.clicked.connect(lambda _, i=invoice: self._on_remind(i))
        lay.addWidget(btn)
        return frame

    def _on_remind(self, invoice):
        """Gửi thông báo nhắc nhở thanh toán đến khách thuê."""
        import json
        import os
        from PyQt6.QtWidgets import QMessageBox
        from config.constants import BASE_DIR

        if not self.container:
            return

        try:
            # Trace: invoice → contract → guest → user_id
            contract = self.container.contract_service.get_by_id(int(invoice.contract_id))
            if not contract:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy hợp đồng liên quan.")
                return

            guest = self.container.guest_service.get_guest_by_id(int(contract.guest_id))
            if not guest:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy khách thuê liên quan.")
                return

            user_id = int(getattr(guest, 'user_id', 0) or 0)
            if user_id == 0:
                QMessageBox.warning(self, "Lỗi", "Khách thuê chưa liên kết tài khoản.")
                return

            room = self.container.room_service.get_room_by_id(int(contract.room_id))
            room_number = room.room_number if room else f"#{contract.room_id}"
            guest_name = getattr(guest, 'full_name', '') or f"Khách #{guest.id}"

            # Build notification
            now = datetime.now()
            notif = {
                'id': f'admin_remind_{invoice.id}_{int(now.timestamp())}',
                'user_id': user_id,
                'icon': '⚠️',
                'icon_bg': '#fed7d7',
                'icon_color': '#c53030',
                'text': (f'Nhắc nhở: Hóa đơn tháng {invoice.month}/{invoice.year} '
                         f'phòng {room_number} ({int(invoice.total_amount):,} đ) '
                         f'đã quá hạn. Vui lòng thanh toán sớm!').replace(',', '.'),
                'time': now.isoformat(),
                'read': False,
            }

            # Save to guest_notifications.json
            notif_file = os.path.join(BASE_DIR, 'data', 'guest_notifications.json')
            all_notifs = []
            if os.path.exists(notif_file):
                try:
                    with open(notif_file, 'r', encoding='utf-8') as f:
                        all_notifs = json.load(f)
                except Exception:
                    all_notifs = []

            all_notifs.insert(0, notif)

            os.makedirs(os.path.dirname(notif_file), exist_ok=True)
            with open(notif_file, 'w', encoding='utf-8') as f:
                json.dump(all_notifs, f, ensure_ascii=False, indent=2)

            QMessageBox.information(
                self, "Thành công",
                f"Đã gửi nhắc nhở đến {guest_name}\n"
                f"Phòng {room_number} — Hóa đơn tháng {invoice.month}/{invoice.year}"
            )

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể gửi nhắc nhở:\n{e}")

    # ── Activities ───────────────────────────────────────────
    def _load_activities(self):
        # Clear old
        while self.activitiesContainer.count():
            item = self.activitiesContainer.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()

        activities = []
        now = datetime.now()
        room_svc = self.container.room_service
        guest_svc = self.container.guest_service

        # Recent contracts
        try:
            contracts = self.container.contract_service.get_all()
            for c in contracts:
                created = self._parse_dt(c.created_at)
                if not created:
                    continue
                room = room_svc.get_room_by_id(int(c.room_id))
                guest = guest_svc.get_guest_by_id(int(c.guest_id))
                room_num = room.room_number if room else f"#{c.room_id}"
                guest_name = guest.full_name if guest else f"Khách #{c.guest_id}"

                if c.status == 'active':
                    activities.append({
                        'icon': '📋', 'icon_bg': '#e6fffa', 'icon_color': '#0b8480',
                        'title': 'Ký hợp đồng mới',
                        'detail': f"{guest_name} — Phòng {room_num}",
                        'time': created, 'type': 'contract'
                    })
                elif c.status == 'terminated':
                    activities.append({
                        'icon': '🚪', 'icon_bg': '#fff5f5', 'icon_color': '#e53e3e',
                        'title': 'Kết thúc hợp đồng',
                        'detail': f"Phòng {room_num} — {guest_name}",
                        'time': created, 'type': 'contract'
                    })
        except Exception:
            pass

        # Recent paid invoices
        try:
            invoices = self.container.invoice_service.get_all()
            for inv in invoices:
                if inv.status != 'paid' or not inv.payment_date:
                    continue
                paid_at = self._parse_dt(inv.payment_date)
                if not paid_at:
                    continue
                contract = self.container.contract_service.get_by_id(int(inv.contract_id))
                room_num = "?"
                if contract:
                    room = room_svc.get_room_by_id(int(contract.room_id))
                    room_num = room.room_number if room else f"#{contract.room_id}"
                activities.append({
                    'icon': '✅', 'icon_bg': '#f0fff4', 'icon_color': '#38a169',
                    'title': 'Thanh toán thành công',
                    'detail': f"Phòng {room_num} — hóa đơn tháng {inv.month}",
                    'time': paid_at, 'type': 'invoice'
                })
        except Exception:
            pass

        # Recent repair requests
        try:
            repairs = self.container.repair_request_service.get_all()
            for r in repairs:
                created = self._parse_dt(r.created_at)
                if not created:
                    continue
                room = room_svc.get_room_by_id(int(r.room_id))
                room_num = room.room_number if room else f"#{r.room_id}"
                activities.append({
                    'icon': '🔧', 'icon_bg': '#fffaf0', 'icon_color': '#dd6b20',
                    'title': 'Yêu cầu sửa chữa mới',
                    'detail': f"{r.title} — Phòng {room_num}",
                    'time': created, 'type': 'repair'
                })
        except Exception:
            pass

        # Sort by time descending, take 5
        activities.sort(key=lambda a: a['time'], reverse=True)
        activities = activities[:5]

        # Count this week
        week_start = now.replace(hour=0, minute=0, second=0) 
        from datetime import timedelta
        week_start = week_start - timedelta(days=now.weekday())
        week_count = sum(1 for a in activities if a['time'] >= week_start)
        self.lblActSub.setText(f"{week_count} hoạt động trong tuần này")

        if not activities:
            lbl = QLabel("Chưa có hoạt động nào.")
            lbl.setStyleSheet("color: #a0aec0; font-size: 13px; padding: 20px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.activitiesContainer.addWidget(lbl)
            return

        # Header row
        header = QWidget()
        header.setFixedHeight(36)
        header.setStyleSheet("background-color: transparent;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 0, 16, 0)
        for text, stretch in [("HOẠT ĐỘNG", 3), ("CHI TIẾT", 4), ("THỜI GIAN", 2)]:
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #a0aec0; font-size: 11px; font-weight: bold;")
            hl.addWidget(lbl, stretch)
        self.activitiesContainer.addWidget(header)

        # Divider
        div = QFrame(); div.setFixedHeight(1); div.setStyleSheet("background-color: #e2e8f0;")
        self.activitiesContainer.addWidget(div)

        for act in activities:
            row = self._make_activity_row(act)
            self.activitiesContainer.addWidget(row)

    def _make_activity_row(self, act):
        row = QFrame()
        row.setMinimumHeight(60)
        row.setStyleSheet(
            "QFrame { background-color: transparent; border-bottom: 1px solid #edf2f7; }")
        lay = QHBoxLayout(row)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(16)

        # Icon
        icon = QLabel(act['icon'])
        icon.setFixedSize(36, 36)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"background-color: {act['icon_bg']}; color: {act['icon_color']}; "
            f"border-radius: 18px; font-size: 16px; border: none;")
        lay.addWidget(icon)

        # Title + detail in a vertical layout
        info_lay = QVBoxLayout()
        info_lay.setSpacing(2)
        info_lay.setContentsMargins(0, 0, 0, 0)
        title = QLabel(act['title'])
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #2d3748; border: none;")
        info_lay.addWidget(title)
        detail = QLabel(act['detail'])
        detail.setStyleSheet("font-size: 12px; color: #718096; border: none;")
        detail.setWordWrap(True)
        info_lay.addWidget(detail)
        lay.addLayout(info_lay, 1)

        # Time ago
        time_label = QLabel(self._time_ago(act['time']))
        time_label.setStyleSheet("font-size: 11px; color: #a0aec0; border: none;")
        time_label.setMinimumWidth(90)
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lay.addWidget(time_label)

        return row

    # ══════════════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════════════
    def _make_card(self, title, icon_text, icon_bg, icon_color):
        """Create a stat card. Returns (frame, {'value_label', 'sub_label'})."""
        frame = self._make_frame()
        frame.setMinimumHeight(140)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(20, 20, 20, 20)

        top = QHBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #718096; font-size: 13px; font-weight: bold;")
        top.addWidget(lbl_title); top.addStretch()
        icon = QLabel(icon_text)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedSize(40, 40)
        icon.setStyleSheet(f"background-color: {icon_bg}; color: {icon_color}; border-radius: 8px; font-weight: bold; font-size: 18px; padding: 0px;")
        top.addWidget(icon)
        lay.addLayout(top)

        lbl_value = QLabel("—")
        lbl_value.setStyleSheet("color: #2d3748; font-size: 24px; font-weight: bold;")
        lay.addWidget(lbl_value)

        lbl_sub = QLabel("")
        lbl_sub.setStyleSheet("color: #a0aec0; font-size: 11px;")
        lay.addWidget(lbl_sub)
        lay.addStretch()
        return (frame, {'value_label': lbl_value, 'sub_label': lbl_sub})

    def _update_card(self, card_tuple, value_text, sub_text, is_teal=False):
        _, refs = card_tuple
        refs['value_label'].setText(value_text)
        if is_teal:
            refs['value_label'].setStyleSheet("color: #0b8480; font-size: 24px; font-weight: bold;")
        refs['sub_label'].setText(sub_text)

    def _make_frame(self):
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background-color: white; border-radius: 12px; border: 1px solid #e2e8f0; }")
        return frame

    def _parse_dt(self, val):
        """Parse ISO datetime string to datetime."""
        if not val:
            return None
        if isinstance(val, datetime):
            return val
        if isinstance(val, date):
            return datetime(val.year, val.month, val.day)
        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                return datetime.strptime(str(val), fmt)
            except ValueError:
                continue
        return None

    def _time_ago(self, dt):
        if not dt:
            return ""
        diff = datetime.now() - dt
        mins = int(diff.total_seconds() / 60)
        if mins < 1: return "Vừa xong"
        if mins < 60: return f"{mins} phút trước"
        hours = mins // 60
        if hours < 24: return f"{hours} giờ trước"
        days = hours // 24
        if days < 7: return f"{days} ngày trước"
        if days < 30: return f"{days // 7} tuần trước"
        return f"{days // 30} tháng trước"


# ══════════════════════════════════════════════════════════════
#  QPainter Fallback Chart
# ══════════════════════════════════════════════════════════════
class _PainterBarChart(QWidget):
    """Simple bar chart drawn with QPainter when QtCharts is not available."""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setMinimumHeight(200)

    def paintEvent(self, event):
        if not self.data:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        margin_left, margin_bottom, margin_top = 50, 30, 10
        chart_w = w - margin_left - 20
        chart_h = h - margin_bottom - margin_top

        max_val = max((d['rent'] + d['utility']) for d in self.data) or 1
        max_val *= 1.2

        # Y axis lines
        painter.setPen(QPen(QColor("#e2e8f0"), 1))
        for i in range(5):
            y = margin_top + int(chart_h * i / 4)
            painter.drawLine(margin_left, y, w - 20, y)
            val = max_val * (1 - i / 4)
            painter.setPen(QPen(QColor("#a0aec0"), 1))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(0, y - 8, margin_left - 8, 16, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"{val:.0f}")
            painter.setPen(QPen(QColor("#e2e8f0"), 1))

        bar_count = len(self.data)
        bar_group_w = chart_w / bar_count
        bar_w = int(bar_group_w * 0.5)

        for idx, d in enumerate(self.data):
            x = margin_left + int(idx * bar_group_w + (bar_group_w - bar_w) / 2)

            # Rent bar
            rent_h = int((d['rent'] / max_val) * chart_h) if max_val > 0 else 0
            utility_h = int((d['utility'] / max_val) * chart_h) if max_val > 0 else 0

            # Draw utility on top of rent
            total_h = rent_h + utility_h
            bar_y = margin_top + chart_h - total_h

            painter.setBrush(QBrush(QColor("#0b8480")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, margin_top + chart_h - rent_h, bar_w, rent_h, 4, 4)

            if utility_h > 0:
                painter.setBrush(QBrush(QColor("#63d9d2")))
                painter.drawRoundedRect(x, bar_y, bar_w, utility_h, 4, 4)

            # Label
            painter.setPen(QPen(QColor("#4a5568"), 1))
            painter.setFont(QFont("Segoe UI", 8))
            lbl_x = margin_left + int(idx * bar_group_w)
            painter.drawText(lbl_x, h - margin_bottom + 2, int(bar_group_w), 20,
                           Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, d['label'])

        # Legend
        legend_y = margin_top
        painter.setBrush(QBrush(QColor("#0b8480")))
        painter.drawRoundedRect(w - 180, legend_y, 10, 10, 2, 2)
        painter.setPen(QPen(QColor("#4a5568")))
        painter.drawText(w - 165, legend_y - 1, 60, 14, Qt.AlignmentFlag.AlignLeft, "Tiền phòng")

        painter.setBrush(QBrush(QColor("#63d9d2")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(w - 95, legend_y, 10, 10, 2, 2)
        painter.setPen(QPen(QColor("#4a5568")))
        painter.drawText(w - 80, legend_y - 1, 70, 14, Qt.AlignmentFlag.AlignLeft, "Điện nước")

        painter.end()
