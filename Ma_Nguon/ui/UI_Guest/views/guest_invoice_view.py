"""
GuestInvoiceView — Trang Hóa đơn / Thanh toán cho Guest.
Hiển thị danh sách hóa đơn theo hợp đồng của khách, cho phép thanh toán qua QR.
"""
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QDialog, QSpacerItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap

from ui.UI_Common.custom_popup import show_success, show_warning, show_info
from ui.UI_Common.bank_utils import load_bank_info, get_qr_path


# ═══════════════════════════════════════════════════════════════
# Payment Dialog — QR thanh toán
# ═══════════════════════════════════════════════════════════════
class PaymentDialog(QDialog):
    def __init__(self, invoice, room_number='', guest_name='', parent=None):
        super().__init__(parent)
        self.invoice = invoice
        self.setWindowTitle("Thanh toán hóa đơn")
        self.setFixedSize(500, 580)
        self.setStyleSheet("QDialog { background-color: #f0f4f7; }")
        self._build_ui(room_number, guest_name)

    def _build_ui(self, room_number, guest_name):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; }")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(40, 30, 40, 25)
        card_lay.setSpacing(12)
        card_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Quét mã QR để thanh toán")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a202c; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(title)

        # QR Image
        lbl_qr = QLabel()
        lbl_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_qr.setMinimumSize(250, 250)
        lbl_qr.setStyleSheet("border: none;")
        qr = get_qr_path()
        if qr:
            pixmap = QPixmap(qr)
            if not pixmap.isNull():
                scaled = pixmap.scaled(QSize(250, 250),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
                lbl_qr.setPixmap(scaled)
        else:
            lbl_qr.setText("📱 QR Code\n(Chưa cài đặt)")
            lbl_qr.setStyleSheet(
                "color: #a0aec0; font-size: 16px; background: #f7fafc; "
                "border: 2px dashed #cbd5e0; border-radius: 8px;")
        card_lay.addWidget(lbl_qr)

        # Amount
        lbl_amount = QLabel(f"Số tiền: {self.invoice.total_amount:,.0f} VNĐ")
        lbl_amount.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        lbl_amount.setStyleSheet("color: #1a202c; border: none;")
        lbl_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(lbl_amount)

        # Bank info
        bank_info = load_bank_info()
        bank_name = bank_info.get('bank_name', 'Chưa cài đặt')
        account = bank_info.get('account_number', '')
        holder = bank_info.get('account_holder', '')

        lbl_bank = QLabel(f"Ngân hàng: <b>{bank_name} - {account}</b>")
        lbl_bank.setStyleSheet("color: #4a5568; font-size: 13px; border: none;")
        lbl_bank.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(lbl_bank)

        lbl_owner = QLabel(f"Chủ tài khoản: <b>{holder}</b>")
        lbl_owner.setStyleSheet("color: #4a5568; font-size: 13px; border: none;")
        lbl_owner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(lbl_owner)

        card_lay.addSpacing(5)

        # Confirm button
        btn_confirm = QPushButton("Xác nhận đã thanh toán")
        btn_confirm.setMinimumHeight(48)
        btn_confirm.setStyleSheet(
            "QPushButton { background-color: #1a4a49; color: white; border: none; "
            "border-radius: 8px; font-weight: bold; font-size: 14px; }"
            "QPushButton:hover { background-color: #0b3d42; }")
        btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirm.clicked.connect(self.accept)
        card_lay.addWidget(btn_confirm)

        # Transfer note
        lbl_note = QLabel(
            f"* Nội dung chuyển khoản: <b>{guest_name} - {room_number}</b>")
        lbl_note.setStyleSheet(
            "color: #718096; font-size: 11px; font-style: italic; border: none;")
        lbl_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_note.setWordWrap(True)
        card_lay.addWidget(lbl_note)

        layout.addWidget(card)


# ═══════════════════════════════════════════════════════════════
# GuestInvoiceView — Trang chính
# ═══════════════════════════════════════════════════════════════
class GuestInvoiceView(QWidget):
    def __init__(self, user=None, invoice_service=None, contract_service=None,
                 room_service=None, guest_service=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.invoice_service = invoice_service
        self.contract_service = contract_service
        self.room_service = room_service
        self.guest_service = guest_service

        self._invoices = []
        self._current_idx = 0
        self._contract = None
        self._room = None
        self._guest = None

        self._build_ui()
        self._load_data()

    # ── Build UI ──
    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Banner
        self.banner = QFrame()
        self.banner.setMinimumHeight(60)
        self.banner.setStyleSheet("background-color: #1a4a49; border-radius: 8px;")
        banner_lay = QHBoxLayout(self.banner)
        banner_lay.setContentsMargins(20, 0, 20, 0)

        self.lbl_banner = QLabel("📄 HÓA ĐƠN")
        self.lbl_banner.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.lbl_banner.setStyleSheet("color: white;")
        banner_lay.addWidget(self.lbl_banner)
        banner_lay.addStretch()

        # Pagination
        self.pagination_layout = QHBoxLayout()
        self.pagination_layout.setSpacing(3)
        self.btn_prev = self._page_btn("‹ Trước")
        self.btn_prev.clicked.connect(self._prev_page)
        self.pagination_layout.addWidget(self.btn_prev)
        self._page_buttons = []
        self.btn_next = self._page_btn("Tiếp ›")
        self.btn_next.clicked.connect(self._next_page)
        banner_lay.addLayout(self.pagination_layout)

        main.addWidget(self.banner)

        # Scroll area for invoice card
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background-color: transparent; }"
            "QScrollBar:vertical { width: 10px; }")

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 10, 0, 10)
        scroll.setWidget(self.scroll_content)
        main.addWidget(scroll, 1)

        # Invoice card placeholder
        self.invoice_card = None

        # Empty state
        self.lbl_empty = QLabel("📋 Chưa có hóa đơn nào")
        self.lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty.setStyleSheet("color: #a0aec0; font-size: 16px; font-weight: bold;")
        self.scroll_layout.addWidget(self.lbl_empty)

    def _page_btn(self, text):
        btn = QPushButton(text)
        btn.setMinimumHeight(28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: white; "
            "border-radius: 4px; font-size: 10pt; padding: 2px 8px; }"
            "QPushButton:hover { background-color: rgba(255,255,255,0.2); }")
        return btn

    # ── Load Data ──
    def _load_data(self):
        if not self.user:
            return
        user_id = int(getattr(self.user, 'id', 0) or 0)

        # 1. Find ALL guest records for this user (may be duplicates)
        my_guest_ids = set()
        self._guest = None
        if self.guest_service:
            try:
                all_guests = self.guest_service.get_all_guests()
                for g in all_guests:
                    gid = int(getattr(g, 'user_id', 0) or 0)
                    if gid == user_id:
                        my_guest_ids.add(int(g.id))
                        if self._guest is None:
                            self._guest = g
            except Exception:
                pass

        # 2. Find ALL contracts matching any of this user's guest IDs
        self._contracts = []
        self._contract = None
        if my_guest_ids and self.contract_service:
            try:
                all_contracts = self.contract_service.contract_repo.get_all()
                for c in all_contracts:
                    c_guest_id = int(getattr(c, 'guest_id', 0) or 0)
                    if c_guest_id in my_guest_ids:
                        self._contracts.append(c)
                # Prefer active contract for room display
                for c in self._contracts:
                    if c.is_active():
                        self._contract = c
                        break
                if not self._contract and self._contracts:
                    self._contract = self._contracts[0]
            except Exception:
                pass

        # 3. Get room info
        if self._contract and self.room_service:
            try:
                self._room = self.room_service.get_room_by_id(
                    int(getattr(self._contract, 'room_id', 0) or 0))
            except Exception:
                self._room = None

        # 4. Collect invoices from ALL contracts
        self._invoices = []
        if self._contracts and self.invoice_service:
            try:
                for ct in self._contracts:
                    ct_id = int(getattr(ct, 'id', 0) or 0)
                    invs = self.invoice_service.get_by_contract(ct_id)
                    self._invoices.extend(invs)
                self._invoices.sort(key=lambda inv: (inv.year, inv.month), reverse=True)
            except Exception:
                self._invoices = []

        self._current_idx = 0
        self._refresh_ui()

    def _refresh_ui(self):
        if not self._invoices:
            self.lbl_empty.show()
            self._update_pagination()
            if self.invoice_card:
                self.invoice_card.hide()
            return
        self.lbl_empty.hide()
        self._show_invoice(self._current_idx)
        self._update_pagination()

    # ── Show Invoice Card ──
    def _show_invoice(self, idx):
        if idx < 0 or idx >= len(self._invoices):
            return
        inv = self._invoices[idx]

        # Remove old card
        if self.invoice_card:
            self.scroll_layout.removeWidget(self.invoice_card)
            self.invoice_card.deleteLater()

        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: white; border: 1px solid #e2e8f0; "
            "border-radius: 12px; } QLabel { color: #2d3748; }")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(25, 25, 25, 25)
        card_lay.setSpacing(10)

        # Room info
        room_num = getattr(self._room, 'room_number', '---') if self._room else '---'
        lbl_room_label = QLabel("Phòng:")
        lbl_room_label.setStyleSheet("color: #718096; font-size: 10pt;")
        card_lay.addWidget(lbl_room_label)

        lbl_room = QLabel(f"Phòng {room_num}")
        lbl_room.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        lbl_room.setStyleSheet("color: #1a4a49;")
        card_lay.addWidget(lbl_room)

        # Address + Due date row
        info_row = QHBoxLayout()
        info_row.setSpacing(8)
        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        left_col.addWidget(self._bold_label("ĐỊA CHỈ"))
        addr = QLabel("Số 2 Đường số 10, Khu phố 37, Phường\nTam Bình, TP. HCM")
        addr.setStyleSheet("color: #4a5568;")
        left_col.addWidget(addr)

        left_col.addItem(QSpacerItem(0, 10))

        left_col.addWidget(self._bold_label("HẠN THANH TOÁN"))
        due = inv.due_date or "Chưa xác định"
        try:
            due_dt = datetime.fromisoformat(due)
            due = due_dt.strftime("%d/%m/%Y")
        except Exception:
            pass
        lbl_due = QLabel(due)
        lbl_due.setStyleSheet("color: #4a5568;")
        left_col.addWidget(lbl_due)

        info_row.addLayout(left_col)
        info_row.addStretch()

        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        right_col.addWidget(self._bold_label("KỲ THANH TOÁN", Qt.AlignmentFlag.AlignRight))
        period = QLabel(f"Tháng {inv.month:02d}/{inv.year}")
        period.setStyleSheet("color: #4a5568;")
        period.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.addWidget(period)
        right_col.addStretch()
        info_row.addLayout(right_col)

        card_lay.addLayout(info_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #e2e8f0;")
        card_lay.addWidget(sep)

        # Detail header
        card_lay.addWidget(self._bold_label("CHI TIẾT HÓA ĐƠN", size=12))

        # Line items
        self._add_line_item(card_lay, "Tiền nhà",
            f"Tháng {inv.month}/{inv.year}", inv.room_rent)
        self._add_line_item(card_lay, "Tiền điện", "", inv.electricity_cost)
        self._add_line_item(card_lay, "Tiền nước", "", inv.water_cost)
        if inv.other_fees:
            self._add_line_item(card_lay, "Phí dịch vụ", "Vệ sinh, bảo trì", inv.other_fees)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #e2e8f0;")
        card_lay.addWidget(sep2)

        # Total row
        total_row = QHBoxLayout()
        lbl_total_label = QLabel("TỔNG CỘNG")
        lbl_total_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_total_label.setStyleSheet("color: #1a202c;")
        total_row.addWidget(lbl_total_label)
        total_row.addStretch()
        lbl_total = QLabel(f"{inv.total_amount:,.0f} VNĐ")
        lbl_total.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        lbl_total.setStyleSheet("color: #0298a0;")
        total_row.addWidget(lbl_total)
        card_lay.addLayout(total_row)

        # Status row
        status_row = QHBoxLayout()
        lbl_st = QLabel("Trạng thái:")
        lbl_st.setStyleSheet("font-size: 12px; color: #4a5568;")
        status_row.addWidget(lbl_st)

        if inv.status == 'paid':
            badge = QLabel(" Đã thanh toán ")
            badge.setStyleSheet(
                "background-color: #c6f6d5; color: #276749; padding: 4px 12px; "
                "border-radius: 10px; font-weight: bold; font-size: 11px;")
        else:
            badge = QLabel(" Chưa thanh toán ")
            badge.setStyleSheet(
                "background-color: #fed7d7; color: #9b2c2c; padding: 4px 12px; "
                "border-radius: 10px; font-weight: bold; font-size: 11px;")
        status_row.addWidget(badge)
        status_row.addStretch()
        card_lay.addLayout(status_row)

        # Pay button (only for unpaid)
        if inv.status != 'paid':
            btn_pay = QPushButton("📧  Thanh toán")
            btn_pay.setMinimumHeight(52)
            btn_pay.setStyleSheet(
                "QPushButton { background-color: #f6e05e; color: #1a202c; border: none; "
                "border-radius: 10px; font-weight: bold; font-size: 15px; }"
                "QPushButton:hover { background-color: #ecc94b; }")
            btn_pay.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_pay.clicked.connect(lambda _, i=inv: self._on_pay(i))
            card_lay.addWidget(btn_pay)

            note = QLabel(
                "* Lưu ý: Vui lòng ghi rõ nội dung chuyển khoản: "
                "<b>Tên – Số phòng</b>")
            note.setStyleSheet("color: #718096; font-size: 11px; font-style: italic;")
            note.setAlignment(Qt.AlignmentFlag.AlignCenter)
            note.setWordWrap(True)
            card_lay.addWidget(note)
        else:
            paid_info = QHBoxLayout()
            paid_info.addStretch()
            pay_date = inv.payment_date or ""
            try:
                pay_dt = datetime.fromisoformat(pay_date)
                pay_date = pay_dt.strftime("%d/%m/%Y")
            except Exception:
                pass
            lbl_paid = QLabel(f"✅ Đã thanh toán ngày {pay_date}")
            lbl_paid.setStyleSheet("color: #38a169; font-size: 13px; font-weight: bold;")
            paid_info.addWidget(lbl_paid)
            paid_info.addStretch()
            card_lay.addLayout(paid_info)

        self.invoice_card = card
        self.scroll_layout.insertWidget(0, card)

        # Update banner
        self.lbl_banner.setText(
            f"📄 HÓA ĐƠN THÁNG {inv.month}/{inv.year}")

    def _add_line_item(self, parent_lay, label, sub_label, amount):
        row = QHBoxLayout()
        left = QVBoxLayout()
        left.setSpacing(2)
        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        left.addWidget(lbl)
        if sub_label:
            sub = QLabel(sub_label)
            sub.setStyleSheet("color: #a0aec0; font-size: 10pt;")
            left.addWidget(sub)
        row.addLayout(left)
        row.addStretch()
        val = QLabel(f"{amount:,.0f} VNĐ")
        val.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        val.setStyleSheet("color: #0298a0;")
        val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(val)
        parent_lay.addLayout(row)

    def _bold_label(self, text, align=None, size=10):
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", size, QFont.Weight.Bold))
        if align:
            lbl.setAlignment(align)
        return lbl

    # ── Pagination ──
    def _update_pagination(self):
        # Remove old page buttons
        for btn in self._page_buttons:
            self.pagination_layout.removeWidget(btn)
            btn.deleteLater()
        self._page_buttons.clear()

        # Remove prev/next temporarily
        self.pagination_layout.removeWidget(self.btn_prev)
        self.pagination_layout.removeWidget(self.btn_next)

        # Re-add prev
        self.pagination_layout.addWidget(self.btn_prev)
        self.btn_prev.setEnabled(self._current_idx > 0)

        total = len(self._invoices)
        for i in range(total):
            inv = self._invoices[i]
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(28, 28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if i == self._current_idx:
                btn.setStyleSheet(
                    "QPushButton { background-color: #0298a0; color: white; "
                    "border-radius: 4px; font-weight: bold; font-size: 10pt; }")
            else:
                btn.setStyleSheet(
                    "QPushButton { background-color: transparent; color: white; "
                    "border-radius: 4px; font-size: 10pt; }"
                    "QPushButton:hover { background-color: rgba(255,255,255,0.2); }")
            btn.clicked.connect(lambda _, idx=i: self._go_to_page(idx))
            self.pagination_layout.addWidget(btn)
            self._page_buttons.append(btn)

        # Re-add next
        self.pagination_layout.addWidget(self.btn_next)
        self.btn_next.setEnabled(self._current_idx < total - 1)

    def _prev_page(self):
        if self._current_idx > 0:
            self._current_idx -= 1
            self._refresh_ui()

    def _next_page(self):
        if self._current_idx < len(self._invoices) - 1:
            self._current_idx += 1
            self._refresh_ui()

    def _go_to_page(self, idx):
        self._current_idx = idx
        self._refresh_ui()

    # ── Payment ──
    def _on_pay(self, invoice):
        room_num = getattr(self._room, 'room_number', '') if self._room else ''
        guest_name = getattr(self._guest, 'full_name', '') if self._guest else ''
        dlg = PaymentDialog(invoice, room_num, guest_name, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        # Mark as paid
        if self.invoice_service:
            try:
                ok, msg = self.invoice_service.mark_paid(invoice.id, method='transfer')
                if ok:
                    show_success(self, "Thành công", "Thanh toán hóa đơn thành công!")
                    self._load_data()  # Reload
                else:
                    show_warning(self, "Lỗi", msg)
            except Exception as e:
                show_warning(self, "Lỗi", f"Lỗi thanh toán: {e}")
