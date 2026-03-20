"""
MyRoomView — Trang "Phòng của tôi" cho Guest.
Hiển thị thông tin phòng, hợp đồng, và form gửi yêu cầu sửa chữa.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QStackedWidget,
    QLineEdit, QTextEdit, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt


class MyRoomView(QWidget):
    """Widget Phòng của tôi — nhúng GuestWindow."""

    def __init__(self, user=None, contract_service=None, room_service=None,
                 repair_service=None, guest_service=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.contract_service = contract_service
        self.room_service = room_service
        self.repair_service = repair_service
        self.guest_service = guest_service
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        self.stack = QStackedWidget()
        main.addWidget(self.stack)

        # ── Page 0: My Room ──
        page_room = QWidget()
        page_room.setStyleSheet("background-color: #f0f4f7;")
        pr_lay = QVBoxLayout(page_room)
        pr_lay.setContentsMargins(30, 30, 30, 30)
        pr_lay.setSpacing(15)

        # Banner
        banner = QFrame()
        banner.setMinimumHeight(55)
        banner.setStyleSheet(
            "background-color: #1a4a49; border-radius: 8px; padding: 10px 20px;")
        b_lay = QHBoxLayout(banner)
        b_lbl = QLabel("📄 HỢP ĐỒNG THUÊ NHÀ")
        b_lbl.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        b_lay.addWidget(b_lbl)
        pr_lay.addWidget(banner)

        # Content row
        content_row = QHBoxLayout()
        content_row.setSpacing(20)

        # ── Left: Room info ──
        left = QWidget()
        left.setFixedWidth(350)
        l_lay = QVBoxLayout(left)
        l_lay.setContentsMargins(0, 0, 0, 0)
        l_lay.setSpacing(15)

        # Room image
        self.lbl_room_img = QLabel("🏠 Ảnh phòng")
        self.lbl_room_img.setMinimumHeight(150)
        self.lbl_room_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_room_img.setStyleSheet(
            "background-color: #cbd5e0; border-radius: 8px; color: #4a5568; font-size: 14px;")
        l_lay.addWidget(self.lbl_room_img)

        # Room info card
        card = QFrame()
        card.setStyleSheet("background-color: #e6f2f2; border-radius: 12px; padding: 15px;")
        c_lay = QVBoxLayout(card)
        c_lay.setSpacing(6)

        c_lay.addWidget(self._card_title("🏠 THÔNG TIN PHÒNG"))

        c_lay.addWidget(self._card_label("TÊN PHÒNG"))
        self.lbl_room_name = self._card_value("—")
        c_lay.addWidget(self.lbl_room_name)

        c_lay.addWidget(self._card_label("ĐỊA CHỈ"))
        self.lbl_address = self._card_value("—")
        c_lay.addWidget(self.lbl_address)

        c_lay.addWidget(self._card_label("DIỆN TÍCH"))
        self.lbl_area = self._card_value("—")
        c_lay.addWidget(self.lbl_area)

        c_lay.addWidget(self._card_label("SỐ TIỀN THUÊ"))
        self.lbl_price = self._card_value("—")
        c_lay.addWidget(self.lbl_price)

        c_lay.addWidget(self._card_label("TRẠNG THÁI"))
        self.lbl_status = QLabel("• Đang thuê")
        self.lbl_status.setStyleSheet("color: #38a169; font-size: 14px; font-weight: bold;")
        c_lay.addWidget(self.lbl_status)

        # Repair request button
        btn_repair = QPushButton("🔧 Yêu cầu sửa chữa")
        btn_repair.setMinimumHeight(40)
        btn_repair.setStyleSheet(
            "QPushButton { background-color: #0298a0; color: white; font-weight: bold; "
            "font-size: 14px; border-radius: 6px; padding: 10px; }"
            "QPushButton:hover { background-color: #027a80; }")
        btn_repair.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_repair.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        c_lay.addWidget(btn_repair)

        l_lay.addWidget(card)
        l_lay.addStretch()
        content_row.addWidget(left)

        # ── Right: Contract panel ──
        contract = QFrame()
        contract.setStyleSheet("background-color: white; border-radius: 8px;")
        ct_lay = QVBoxLayout(contract)
        ct_lay.setContentsMargins(40, 40, 40, 40)
        ct_lay.setSpacing(10)

        title = QLabel("HỢP ĐỒNG THUÊ NHÀ")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a202c;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ct_lay.addWidget(title)

        self.lbl_contract_no = QLabel("Số: —")
        self.lbl_contract_no.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_contract_no.setStyleSheet("color: #4a5568; font-size: 14px;")
        ct_lay.addWidget(self.lbl_contract_no)

        ct_lay.addSpacing(10)

        self.txt_contract = QLabel()
        self.txt_contract.setWordWrap(True)
        self.txt_contract.setStyleSheet("color: #2d3748; font-size: 14px; line-height: 1.6;")
        self.txt_contract.setAlignment(Qt.AlignmentFlag.AlignTop)
        ct_lay.addWidget(self.txt_contract, 1)

        ct_lay.addSpacing(10)

        # Contract buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_view = QPushButton("Xem hợp đồng")
        btn_view.setMinimumSize(150, 45)
        btn_view.setStyleSheet(
            "QPushButton { background-color: #0298a0; color: white; font-weight: bold; "
            "font-size: 14px; border-radius: 6px; padding: 10px; }"
            "QPushButton:hover { background-color: #027a80; }")
        btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(btn_view)
        btn_row.addStretch()
        btn_print = QPushButton("In hợp đồng")
        btn_print.setMinimumSize(150, 45)
        btn_print.setStyleSheet(
            "QPushButton { background-color: #0298a0; color: white; font-weight: bold; "
            "font-size: 14px; border-radius: 6px; padding: 10px; }"
            "QPushButton:hover { background-color: #027a80; }")
        btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(btn_print)
        btn_row.addStretch()
        ct_lay.addLayout(btn_row)

        content_row.addWidget(contract)
        pr_lay.addLayout(content_row)
        self.stack.addWidget(page_room)

        # ── Page 1: Maintenance Request Form ──
        page_mnt = QWidget()
        page_mnt.setStyleSheet("background-color: #f0f4f7;")
        pm_lay = QVBoxLayout(page_mnt)
        pm_lay.setContentsMargins(30, 30, 30, 30)
        pm_lay.setSpacing(15)

        # Back button
        btn_back = QPushButton("← Quay lại")
        btn_back.setStyleSheet(
            "QPushButton { background: transparent; color: #4a5568; "
            "font-weight: bold; font-size: 16px; border: none; text-align: left; }"
            "QPushButton:hover { color: #2d3748; }")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        back_row = QHBoxLayout()
        back_row.addWidget(btn_back)
        back_row.addStretch()
        pm_lay.addLayout(back_row)

        # Form card
        form = QFrame()
        form.setStyleSheet(
            "background-color: white; border: 1px solid #e2e8f0; border-radius: 12px;")
        f_lay = QVBoxLayout(form)
        f_lay.setContentsMargins(40, 40, 40, 40)
        f_lay.setSpacing(20)

        f_title = QLabel("🔧 Gửi yêu cầu sửa chữa")
        f_title.setStyleSheet("color: #1a202c; font-size: 18px; font-weight: bold;")
        f_lay.addWidget(f_title)

        f_lay.addWidget(self._form_label("Mục cần sửa chữa *"))
        self.inp_mnt_title = QLineEdit()
        self.inp_mnt_title.setPlaceholderText("Ví dụ: Vòi nước, Điều hòa, Cửa...")
        self.inp_mnt_title.setMinimumHeight(45)
        self.inp_mnt_title.setStyleSheet(
            "background-color: white; border: 1px solid #cbd5e0; border-radius: 6px; "
            "padding: 10px; font-size: 14px;")
        f_lay.addWidget(self.inp_mnt_title)

        f_lay.addWidget(self._form_label("Mức độ ưu tiên *"))
        self.cmb_priority = QComboBox()
        self.cmb_priority.addItems(["Thấp", "Trung bình", "Cao", "Khẩn cấp"])
        self.cmb_priority.setCurrentIndex(1)
        self.cmb_priority.setMinimumHeight(45)
        self.cmb_priority.setStyleSheet(
            "QComboBox { background-color: white; border: 1px solid #cbd5e0; "
            "border-radius: 6px; padding: 10px; font-size: 14px; }")
        f_lay.addWidget(self.cmb_priority)

        f_lay.addWidget(self._form_label("Mô tả chi tiết *"))
        self.inp_mnt_desc = QTextEdit()
        self.inp_mnt_desc.setPlaceholderText("Hãy mô tả chi tiết vấn đề...")
        self.inp_mnt_desc.setMinimumHeight(120)
        self.inp_mnt_desc.setStyleSheet(
            "background-color: white; border: 1px solid #cbd5e0; border-radius: 6px; "
            "padding: 10px; font-size: 14px;")
        f_lay.addWidget(self.inp_mnt_desc)

        btn_submit = QPushButton("📤 Gửi yêu cầu")
        btn_submit.setMinimumHeight(50)
        btn_submit.setStyleSheet(
            "QPushButton { background-color: #0298a0; color: white; font-weight: bold; "
            "font-size: 14px; border-radius: 6px; padding: 10px; }"
            "QPushButton:hover { background-color: #027a80; }")
        btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_submit.clicked.connect(self._submit_repair)
        f_lay.addWidget(btn_submit)

        pm_lay.addWidget(form)
        pm_lay.addStretch()
        self.stack.addWidget(page_mnt)

        self.stack.setCurrentIndex(0)

    # ── Helpers ──
    def _card_title(self, text):
        lb = QLabel(text)
        lb.setStyleSheet("color: #1a4a49; font-size: 16px; font-weight: bold;")
        return lb

    def _card_label(self, text):
        lb = QLabel(text)
        lb.setStyleSheet("color: #4a5568; font-size: 12px;")
        return lb

    def _card_value(self, text):
        lb = QLabel(text)
        lb.setStyleSheet("color: #2d3748; font-size: 14px; font-weight: bold;")
        return lb

    def _form_label(self, text):
        lb = QLabel(text)
        lb.setStyleSheet("color: #4a5568; font-size: 14px;")
        return lb

    # ── Data ──
    def _load_data(self):
        """Load room/contract data for current guest user."""
        if not self.user:
            return

        # Find guest's contract
        contract = None
        room = None
        guest = None

        if self.guest_service:
            all_guests = self.guest_service.get_all_guests()
            for g in all_guests:
                if getattr(g, 'email', None) == getattr(self.user, 'email', None):
                    guest = g
                    break
                if getattr(g, 'phone', None) == getattr(self.user, 'phone', None):
                    guest = g
                    break

        if guest and self.contract_service:
            contracts = self.contract_service.get_all()
            for c in contracts:
                if str(getattr(c, 'guest_id', '')) == str(getattr(guest, 'id', '')):
                    if getattr(c, 'status', '') in ('active', 'Đang thuê', 'Còn hiệu lực'):
                        contract = c
                        break

        if contract and self.room_service:
            room_id = getattr(contract, 'room_id', None)
            if room_id:
                room = self.room_service.get_room_by_id(room_id)

        # Populate UI
        if room:
            self.lbl_room_name.setText(getattr(room, 'name', '—'))
            self.lbl_address.setText(f"📍 {getattr(room, 'address', 'Chưa có')}")
            area = getattr(room, 'area', getattr(room, 'size', ''))
            self.lbl_area.setText(f"{area}m²" if area else "—")
            price = getattr(room, 'price', getattr(room, 'rent_price', 0))
            self.lbl_price.setText(f"💰 {int(price):,}đ/tháng" if price else "—")

        if contract:
            self.lbl_contract_no.setText(
                f"Số: {getattr(contract, 'id', '—')}")
            start = getattr(contract, 'start_date', '')
            end = getattr(contract, 'end_date', '')
            room_name = getattr(room, 'name', '') if room else ''
            guest_name = getattr(guest, 'full_name', getattr(guest, 'name', '')) if guest else ''

            contract_text = (
                f"<b>BÊN CHO THUÊ (Bên A):</b> Chủ trọ<br><br>"
                f"<b>BÊN THUÊ (Bên B):</b> {guest_name}<br><br>"
                f"<b>Phòng:</b> {room_name}<br>"
                f"<b>Ngày bắt đầu:</b> {start}<br>"
                f"<b>Ngày kết thúc:</b> {end}<br><br>"
                f"<b>Trạng thái:</b> {getattr(contract, 'status', 'Đang thuê')}"
            )
            self.txt_contract.setText(contract_text)

    def _submit_repair(self):
        title = self.inp_mnt_title.text().strip()
        desc = self.inp_mnt_desc.toPlainText().strip()
        priority = self.cmb_priority.currentText()

        if not title:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mục cần sửa chữa")
            return
        if not desc:
            QMessageBox.warning(self, "Lỗi", "Vui lòng mô tả chi tiết")
            return

        if self.repair_service:
            try:
                self.repair_service.create({
                    'title': title,
                    'description': desc,
                    'priority': priority,
                    'status': 'Chờ tiếp nhận',
                    'guest_name': getattr(self.user, 'full_name', ''),
                })
                QMessageBox.information(self, "Thành công", "Gửi yêu cầu sửa chữa thành công!")
                self.inp_mnt_title.clear()
                self.inp_mnt_desc.clear()
                self.cmb_priority.setCurrentIndex(1)
                self.stack.setCurrentIndex(0)
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể gửi: {e}")
        else:
            QMessageBox.information(self, "Thành công", "Gửi yêu cầu sửa chữa thành công!")
            self.inp_mnt_title.clear()
            self.inp_mnt_desc.clear()
            self.stack.setCurrentIndex(0)
