"""
DangKyPhongView — Trang "Đăng ký phòng" cho Guest.
Hiển thị danh sách phòng giống giao diện Admin nhưng thay nút Cập nhật
bằng nút Đặt phòng. Chỉ cho đặt phòng trống.
Luồng đặt phòng 3 bước:
  1. Nhập thông tin cá nhân (Họ tên, năm sinh, giới tính, CCCD)
  2. Xem hợp đồng (tạm để trống) + Xác nhận thanh toán tiền cọc
  3. Hiện QR thanh toán + Xác nhận thanh toán → tạo contract pending
"""
import os
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame, QLineEdit, QComboBox, QMessageBox,
    QScrollArea, QDialog, QSizePolicy, QSpacerItem, QStackedWidget,
    QCheckBox, QTextEdit, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPixmap
from ui.UI_Common.custom_popup import show_success, show_error, show_warning, show_info, ask_question, ask_danger

from config.constants import BASE_DIR
from models.room import Room
from models.contract import Contract

from ui.UI_Common.bank_utils import load_bank_info, get_qr_path, QR_IMAGE_PATH


# ═══════════════════════════════════════════════════════════════
# BookingWizard — Dialog 3 bước
# ═══════════════════════════════════════════════════════════════
class BookingWizard(QDialog):
    """Wizard đăng ký phòng 3 bước."""

    def __init__(self, room: Room, user=None, guest_service=None, parent=None):
        super().__init__(parent)
        self.room = room
        self.user = user
        self.guest_service = guest_service
        self.personal_info = {}
        self._guest = None
        self.setWindowTitle(f"Đăng ký phòng {room.room_number}")
        self.setFixedSize(620, 780)
        self.setStyleSheet("QDialog { background-color: #f0f4f7; }")
        self._build_ui()
        self._prefill_guest_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_step1())
        self.stack.addWidget(self._build_step2())
        self.stack.addWidget(self._build_step3())
        layout.addWidget(self.stack)

    # ────────────────────────────────────────────────
    # STEP 1: Thông tin cá nhân
    # ────────────────────────────────────────────────
    def _build_step1(self):
        page = QWidget()
        page.setStyleSheet("background-color: #f0f4f7;")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(20, 15, 20, 15)
        outer.setSpacing(10)

        # Back button
        btn_back = QPushButton("← Quay lại")
        btn_back.setStyleSheet(
            "QPushButton { background: transparent; color: #4a5568; font-weight: bold; "
            "font-size: 14px; border: none; text-align: left; }"
            "QPushButton:hover { color: #2d3748; }")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.reject)
        back_row = QHBoxLayout()
        back_row.addWidget(btn_back)
        back_row.addStretch()
        outer.addLayout(back_row)

        # Form card
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; }")
        form = QVBoxLayout(card)
        form.setContentsMargins(40, 25, 40, 25)
        form.setSpacing(8)

        title = QLabel("Thông tin đặt phòng")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a202c; border: none;")
        form.addWidget(title)

        subtitle = QLabel(f"Phòng {self.room.room_number} - Vui lòng điền đầy đủ thông tin")
        subtitle.setStyleSheet("color: #718096; font-size: 13px; border: none;")
        form.addWidget(subtitle)

        form.addSpacing(5)

        # Field: Họ và tên
        form.addWidget(self._field_label("Họ và tên *"))
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Nhập họ và tên")
        if self.user and hasattr(self.user, 'full_name'):
            self.inp_name.setText(self.user.full_name)
        self._style_input(self.inp_name)
        form.addWidget(self.inp_name)

        # Field: Năm sinh
        form.addWidget(self._field_label("Năm sinh *"))
        self.inp_dob = QLineEdit()
        self.inp_dob.setPlaceholderText("Nhập năm sinh (VD: 2000)")
        self._style_input(self.inp_dob)
        form.addWidget(self.inp_dob)

        # Field: Giới tính
        form.addWidget(self._field_label("Giới tính *"))
        gender_row = QHBoxLayout()
        gender_row.setSpacing(20)
        self.gender_group = QButtonGroup(self)
        radio_style = (
            "QRadioButton { color: #4a5568; font-size: 14px; spacing: 6px; border: none; }"
            "QRadioButton::indicator { width: 18px; height: 18px; }"
            "QRadioButton::indicator:checked { background-color: #0b8480; border: 2px solid #0b8480; border-radius: 9px; }"
            "QRadioButton::indicator:unchecked { background-color: white; border: 2px solid #cbd5e0; border-radius: 9px; }")
        for text in ["Nam", "Nữ"]:
            rb = QRadioButton(text)
            rb.setStyleSheet(radio_style)
            rb.setMinimumHeight(36)
            self.gender_group.addButton(rb)
            gender_row.addWidget(rb)
        gender_row.addStretch()
        form.addLayout(gender_row)

        # Field: CCCD
        form.addWidget(self._field_label("Số CCCD/CMND *"))
        self.inp_cccd = QLineEdit()
        self.inp_cccd.setPlaceholderText("Nhập số CCCD/CMND")
        self._style_input(self.inp_cccd)
        form.addWidget(self.inp_cccd)

        # Field: Số điện thoại
        form.addWidget(self._field_label("Số điện thoại *"))
        self.inp_phone = QLineEdit()
        self.inp_phone.setPlaceholderText("Nhập số điện thoại")
        if self.user and hasattr(self.user, 'phone'):
            self.inp_phone.setText(str(self.user.phone))
        self._style_input(self.inp_phone)
        form.addWidget(self.inp_phone)

        # Field: Email
        form.addWidget(self._field_label("Email *"))
        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("Nhập địa chỉ email")
        if self.user and hasattr(self.user, 'email'):
            self.inp_email.setText(str(self.user.email))
        self._style_input(self.inp_email)
        form.addWidget(self.inp_email)

        form.addStretch()

        # Button: Tiếp tục
        btn_next = QPushButton("Tiếp tục")
        btn_next.setMinimumHeight(48)
        btn_next.setStyleSheet(
            "QPushButton { background-color: #1a4a49; color: white; border: none; "
            "border-radius: 8px; font-weight: bold; font-size: 15px; }"
            "QPushButton:hover { background-color: #0b3d42; }")
        btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_next.clicked.connect(self._on_step1_next)
        form.addWidget(btn_next)

        outer.addWidget(card, 1)
        return page

    def _prefill_guest_data(self):
        """Auto-fill step 1 from saved guest record."""
        if not self.guest_service or not self.user:
            return
        try:
            uid = getattr(self.user, 'id', 0)
            self._guest = self.guest_service.get_guest_by_user_id(uid)
        except Exception:
            self._guest = None
        if not self._guest:
            return
        # Fill fields
        name = getattr(self._guest, 'full_name', '') or ''
        if name:
            self.inp_name.setText(name)
        dob = getattr(self._guest, 'dob', '') or ''
        if dob:
            self.inp_dob.setText(dob)
        cccd = getattr(self._guest, 'id_card', '') or ''
        if cccd:
            self.inp_cccd.setText(cccd)
        gender = getattr(self._guest, 'gender', '') or ''
        if gender:
            for btn in self.gender_group.buttons():
                if btn.text() == gender:
                    btn.setChecked(True)
                    break
        phone = getattr(self._guest, 'phone', '') or ''
        if phone:
            self.inp_phone.setText(str(phone))
        email = getattr(self._guest, 'email', '') or ''
        if email:
            self.inp_email.setText(str(email))

    def _on_step1_next(self):
        name = self.inp_name.text().strip()
        dob = self.inp_dob.text().strip()
        checked_btn = self.gender_group.checkedButton()
        gender = checked_btn.text() if checked_btn else ""
        cccd = self.inp_cccd.text().strip()
        phone = self.inp_phone.text().strip()
        email = self.inp_email.text().strip()

        if not name:
            return show_warning(self, "Lỗi", "Vui lòng nhập họ và tên")
        if not dob:
            return show_warning(self, "Lỗi", "Vui lòng nhập năm sinh")
        if not gender:
            return show_warning(self, "Lỗi", "Vui lòng chọn giới tính")
        if not cccd or not cccd.isdigit() or len(cccd) != 12:
            return show_warning(self, "Lỗi", "Số CCCD/CMND phải đủ 12 chữ số")
        if not phone:
            return show_warning(self, "Lỗi", "Vui lòng nhập số điện thoại")
        if not phone.isdigit() or len(phone) != 10:
            return show_warning(self, "Lỗi", "SĐT phải đúng 10 chữ số")
        if not email:
            return show_warning(self, "Lỗi", "Vui lòng nhập email")
        if '@gmail.com' not in email:
            return show_warning(self, "Lỗi", "Email phải có dạng abc@gmail.com")

        # Kiểm tra trùng email / SĐT với khách thuê khác
        if self.guest_service:
            current_user_id = getattr(self.user, 'id', -1)
            all_guests = self.guest_service.get_all_guests()
            for g in all_guests:
                if getattr(g, 'user_id', 0) == current_user_id:
                    continue
                if email and getattr(g, 'email', '') == email:
                    return show_warning(self, "Lỗi", "Email này đã được sử dụng bởi tài khoản khác")
                if phone and str(getattr(g, 'phone', '')) == phone:
                    return show_warning(self, "Lỗi", "SĐT này đã được sử dụng bởi tài khoản khác")

        self.personal_info = {
            'full_name': name, 'dob': dob,
            'gender': gender, 'id_card': cccd,
            'phone': phone, 'email': email,
        }

        # Save guest info to system
        if self.guest_service:
            try:
                if self._guest:
                    self._guest.full_name = name
                    self._guest.dob = dob
                    self._guest.gender = gender
                    self._guest.id_card = cccd
                    self._guest.phone = phone
                    self._guest.email = email
                    self.guest_service.update_guest(self._guest)
                else:
                    from models.guest import Guest
                    new_g = Guest(
                        user_id=getattr(self.user, 'id', 0),
                        full_name=name, dob=dob, gender=gender,
                        id_card=cccd,
                        phone=phone,
                        email=email,
                    )
                    self.guest_service.create_guest(new_g)
                    self._guest = self.guest_service.get_guest_by_user_id(
                        getattr(self.user, 'id', 0))
            except Exception as e:
                print(f'[BookingWizard] save guest error: {e}')

        # Also update user account if phone/email changed
        if self.user:
            try:
                changed = False
                if phone and str(getattr(self.user, 'phone', '')) != phone:
                    self.user.phone = phone
                    changed = True
                if email and str(getattr(self.user, 'email', '')) != email:
                    self.user.email = email
                    changed = True
                if changed:
                    parent_window = self.window()
                    container = getattr(parent_window, 'container', None)
                    if container and hasattr(container, 'auth_service'):
                        container.auth_service.user_repo.update(self.user)
            except Exception as e:
                print(f'[BookingWizard] update user error: {e}')

        # Fill contract preview with info
        self._fill_contract_preview()
        self.stack.setCurrentIndex(1)

    # ────────────────────────────────────────────────
    # STEP 2: Hợp đồng + Xác nhận thanh toán tiền cọc
    # ────────────────────────────────────────────────
    def _build_step2(self):
        page = QWidget()
        page.setStyleSheet("background-color: #f0f4f7;")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(20, 15, 20, 15)
        outer.setSpacing(10)

        # Back button
        btn_back = QPushButton("← Quay lại")
        btn_back.setStyleSheet(
            "QPushButton { background: transparent; color: #4a5568; font-weight: bold; "
            "font-size: 14px; border: none; text-align: left; }"
            "QPushButton:hover { color: #2d3748; }")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        back_row = QHBoxLayout()
        back_row.addWidget(btn_back)
        back_row.addStretch()
        outer.addLayout(back_row)

        # Contract card
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; }")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(35, 30, 35, 25)
        card_lay.setSpacing(10)

        # Title
        title = QLabel("HỢP ĐỒNG THUÊ PHÒNG TRỌ")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a202c; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(title)

        # Contract content (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.contract_content = QLabel()
        self.contract_content.setWordWrap(True)
        self.contract_content.setStyleSheet("color: #2d3748; font-size: 13px; line-height: 1.6; background: transparent; padding: 10px;")
        self.contract_content.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.contract_content)
        card_lay.addWidget(scroll, 1)

        # Checkbox đồng ý
        self.chk_agree = QCheckBox(
            "Tôi xác nhận đã đọc, hiểu rõ và đồng ý với tất cả các điều khoản "
            "trong hợp đồng thuê phòng trọ này."
        )
        self.chk_agree.setStyleSheet(
            "QCheckBox { color: #4a5568; font-size: 12px; spacing: 8px; border: none; }"
            "QCheckBox::indicator { width: 18px; height: 18px; }")
        card_lay.addWidget(self.chk_agree)

        # Button: Xác nhận và thanh toán
        self.btn_pay = QPushButton("Xác nhận và thanh toán tiền cọc")
        self.btn_pay.setMinimumHeight(48)
        self.btn_pay.setEnabled(False)
        self.btn_pay.setStyleSheet(
            "QPushButton { background-color: #1a4a49; color: white; border: none; "
            "border-radius: 8px; font-weight: bold; font-size: 14px; }"
            "QPushButton:hover { background-color: #0b3d42; }"
            "QPushButton:disabled { background-color: #a0aec0; color: #e2e8f0; }")
        self.btn_pay.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pay.clicked.connect(self._on_step2_next)
        self.chk_agree.stateChanged.connect(
            lambda state: self.btn_pay.setEnabled(state == 2))
        card_lay.addWidget(self.btn_pay)

        note = QLabel("Vui lòng đọc kỹ hợp đồng và đồng ý điều khoản để hoàn tất")
        note.setStyleSheet("color: #a0aec0; font-size: 11px; border: none;")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(note)

        outer.addWidget(card, 1)
        return page

    def _fill_contract_preview(self):
        info = self.personal_info
        room = self.room
        today = datetime.now().strftime("%d/%m/%Y")
        end_dt = datetime.now().replace(year=datetime.now().year + 1)
        end_day = end_dt.strftime("%d/%m/%Y")

        contract_html = f"""
        <div style="text-align: center; margin-bottom: 10px;">
            <b style="font-size: 15px;">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>
            <b>Độc lập - Tự do - Hạnh phúc</b><br>
            <span style="color: #718096;">———————</span><br><br>
            <b style="font-size: 16px;">HỢP ĐỒNG THUÊ PHÒNG TRỌ</b><br>
            <i style="color: #718096;">Ngày {today}</i>
        </div>
        <br>
        <b>ĐIỀU 1: BÊN CHO THUÊ (Bên A)</b><br>
        Ông/Bà: <b>Tạ Nhật Anh</b><br>
        SĐT: <b>0364216007</b><br>
        Địa chỉ: <b>2 đường số 10, P. Tam Bình, Thủ Đức, TP.HCM</b><br><br>

        <b>ĐIỀU 2: BÊN THUÊ (Bên B)</b><br>
        Ông/Bà: <b>{info.get('full_name', '')}</b><br>
        Năm sinh: <b>{info.get('dob', '')}</b><br>
        Giới tính: <b>{info.get('gender', '')}</b><br>
        CCCD/CMND: <b>{info.get('id_card', '')}</b><br>
        Số điện thoại: <b>{info.get('phone', '')}</b><br>
        Email: <b>{info.get('email', '')}</b><br><br>

        <b>ĐIỀU 3: NỘI DUNG HỢP ĐỒNG</b><br>
        Phòng: <b>{room.room_number}</b> — Tầng {room.floor}<br>
        Diện tích: {room.area} m²<br>
        Giá thuê: <b>{room.price:,.0f} VNĐ/tháng</b><br>
        Tiền cọc: <b>{room.deposit:,.0f} VNĐ</b><br>
        Thời hạn thuê: <b>Từ {today} đến {end_day}</b><br><br>

        <b>ĐIỀU 4: TRÁCH NHIỆM CÁC BÊN</b><br>
        <b>Trách nhiệm Bên A:</b><br>
        • Giao phòng và trang thiết bị cho Bên B đúng thời hạn<br>
        • Đảm bảo các điều kiện sinh hoạt cơ bản (điện, nước, vệ sinh)<br>
        • Thông báo trước ít nhất 7 ngày khi muốn vào phòng kiểm tra<br><br>

        <b>Trách nhiệm Bên B:</b><br>
        • Thanh toán đầy đủ và đúng hạn các khoản phí theo thỏa thuận<br>
        • Giữ gìn vệ sinh, bảo quản tài sản trong phòng<br>
        • Không được tự ý sửa chữa, cải tạo phòng trọ khi chưa có sự đồng ý của Bên A<br>
        • Tuân thủ nội quy chung của khu trọ<br>
        • Thông báo trước ít nhất 30 ngày khi muốn chấm dứt hợp đồng<br><br>

        <b>ĐIỀU 5: ĐIỀU KHOẢN CHUNG</b><br>
        • Hợp đồng được lập thành 02 bản có giá trị pháp lý như nhau, mỗi bên giữ 01 bản<br>
        • Mọi tranh chấp phát sinh sẽ được giải quyết thông qua thương lượng, hòa giải<br>
        • Nếu không thỏa thuận được, sẽ đưa ra Tòa án nhân dân có thẩm quyền giải quyết<br>
        """
        self.contract_content.setText(contract_html)

    def _on_step2_next(self):
        if not self.chk_agree.isChecked():
            return show_warning(self, "Lỗi",
                "Vui lòng đọc và đồng ý với các điều khoản hợp đồng.")
        # Update QR info
        self._fill_qr_info()
        self.stack.setCurrentIndex(2)

    # ────────────────────────────────────────────────
    # STEP 3: QR thanh toán
    # ────────────────────────────────────────────────
    def _build_step3(self):
        page = QWidget()
        page.setStyleSheet("background-color: #f0f4f7;")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(20, 15, 20, 15)
        outer.setSpacing(0)

        # Card
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
        self.lbl_qr = QLabel()
        self.lbl_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_qr.setMinimumSize(250, 250)
        self.lbl_qr.setStyleSheet("border: none;")
        if os.path.exists(QR_IMAGE_PATH):
            pixmap = QPixmap(QR_IMAGE_PATH)
            if not pixmap.isNull():
                scaled = pixmap.scaled(QSize(250, 250),
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                self.lbl_qr.setPixmap(scaled)
        else:
            self.lbl_qr.setText("📱 QR Code")
            self.lbl_qr.setStyleSheet("color: #a0aec0; font-size: 18px; "
                                       "background: #f7fafc; border: 2px dashed #cbd5e0; border-radius: 8px;")
        card_lay.addWidget(self.lbl_qr)

        # Amount
        self.lbl_amount = QLabel(f"Số tiền: {self.room.deposit:,.0f} VNĐ")
        self.lbl_amount.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        self.lbl_amount.setStyleSheet("color: #1a202c; border: none;")
        self.lbl_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(self.lbl_amount)

        # Bank info
        self.lbl_bank = QLabel("Ngân hàng: <b>VPBank - 0888898345</b>")
        self.lbl_bank.setStyleSheet("color: #4a5568; font-size: 13px; border: none;")
        self.lbl_bank.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(self.lbl_bank)

        self.lbl_owner = QLabel("Chủ tài khoản: <b>NGUYEN VAN A</b>")
        self.lbl_owner.setStyleSheet("color: #4a5568; font-size: 13px; border: none;")
        self.lbl_owner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(self.lbl_owner)

        card_lay.addSpacing(5)

        # Confirm button
        btn_confirm = QPushButton("Xác nhận thanh toán")
        btn_confirm.setMinimumHeight(48)
        btn_confirm.setStyleSheet(
            "QPushButton { background-color: #1a4a49; color: white; border: none; "
            "border-radius: 8px; font-weight: bold; font-size: 14px; }"
            "QPushButton:hover { background-color: #0b3d42; }")
        btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirm.clicked.connect(self.accept)
        card_lay.addWidget(btn_confirm)

        # Transfer content
        self.lbl_transfer = QLabel()
        self.lbl_transfer.setStyleSheet("color: #1a4a49; font-size: 13px; font-style: italic; border: none;")
        self.lbl_transfer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_transfer.setWordWrap(True)
        card_lay.addWidget(self.lbl_transfer)

        outer.addWidget(card, 1)
        return page

    def _fill_qr_info(self):
        name = self.personal_info.get('full_name', '')
        self.lbl_amount.setText(f"Số tiền: {self.room.deposit:,.0f} VNĐ")
        self.lbl_transfer.setText(
            f"Nội dung chuyển khoản:\n"
            f"<b>Phòng {self.room.room_number} - {name} - Đặt cọc</b>"
        )
        # Load bank info from admin settings
        bank_info = load_bank_info()
        if bank_info:
            bank_name = bank_info.get('bank_name', '')
            account = bank_info.get('account_number', '')
            holder = bank_info.get('account_holder', '')
            self.lbl_bank.setText(f'Ngân hàng: <b>{bank_name} - {account}</b>')
            self.lbl_owner.setText(f'Chủ tài khoản: <b>{holder}</b>')
        # Reload QR image
        qr = get_qr_path()
        if qr:
            pixmap = QPixmap(qr)
            if not pixmap.isNull():
                scaled = pixmap.scaled(QSize(250, 250),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
                self.lbl_qr.setPixmap(scaled)

    # ── Helpers ──
    def _field_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #2d3748; font-size: 13px; font-weight: bold; border: none;")
        # Color the asterisk red
        if "*" in text:
            parts = text.split("*")
            lbl.setText(f'{parts[0]}<span style="color: #e53e3e;">*</span>')
            lbl.setTextFormat(Qt.TextFormat.RichText)
        return lbl

    def _style_input(self, inp: QLineEdit):
        inp.setMinimumHeight(42)
        inp.setStyleSheet(
            "QLineEdit { background-color: #f7fafc; border: 1px solid #e2e8f0; "
            "border-radius: 6px; padding: 10px 12px; font-size: 14px; color: #4a5568; }")


# ═══════════════════════════════════════════════════════════════
# GuestRoomCard
# ═══════════════════════════════════════════════════════════════
class GuestRoomCard(QFrame):
    """Card hiển thị 1 phòng — phiên bản Guest."""
    detail_clicked = pyqtSignal(object)
    book_clicked = pyqtSignal(object)

    STATUS_MAP = {
        'available': ('● Trống', '#38a169', '#e6fffa'),
        'occupied': ('● Đang thuê', '#3182ce', '#ebf8ff'),
        'maintenance': ('● Bảo trì', '#e53e3e', '#fff5f5'),
    }

    def __init__(self, room: Room, parent=None):
        super().__init__(parent)
        self.room = room
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("roomCard")
        self.setStyleSheet("""
            QFrame#roomCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 15px;
            }
            QFrame#roomCard:hover {
                border: 1px solid #0b8480;
            }
        """)
        self.setFixedHeight(260)
        self.setMinimumWidth(200)
        self.setMaximumWidth(280)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # Row 1: Room number + status
        row1 = QHBoxLayout()
        lbl_name = QLabel(self.room.room_number)
        lbl_name.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_name.setStyleSheet("color: #2d3748;")
        row1.addWidget(lbl_name)
        row1.addStretch()

        status_text, status_color, status_bg = self.STATUS_MAP.get(
            self.room.status, ('● ?', '#718096', '#f7fafc'))
        lbl_status = QLabel(status_text)
        lbl_status.setStyleSheet(f"color: {status_color}; font-size: 11px; font-weight: bold; "
                                  f"background-color: {status_bg}; border-radius: 8px; padding: 2px 8px;")
        row1.addWidget(lbl_status)
        layout.addLayout(row1)

        # Row 2: Price
        price_text = f"{self.room.price / 1_000_000:.1f}M/tháng"
        lbl_price = QLabel(price_text)
        lbl_price.setStyleSheet("color: #0b8480; font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl_price)

        # Info rows
        room_type = getattr(self.room, 'room_type', '') or 'Phòng đơn'
        amenities_str = ", ".join(self.room.amenities) if self.room.amenities else "—"
        info_data = [
            ("Tầng", f"Tầng {self.room.floor}"),
            ("Diện tích", f"{self.room.area} m²"),
            ("Tiện nghi", amenities_str),
            ("Loại", room_type),
        ]
        for label, value in info_data:
            row = QHBoxLayout()
            lbl = QLabel(f"  {label}")
            lbl.setStyleSheet("color: #718096; font-size: 11px;")
            lbl.setFixedWidth(70)
            val = QLabel(value)
            val.setStyleSheet("color: #2d3748; font-size: 11px; font-weight: bold;")
            val.setWordWrap(True)
            row.addWidget(lbl)
            row.addWidget(val, 1)
            layout.addLayout(row)

        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_detail = QPushButton("Chi tiết")
        btn_detail.setStyleSheet(
            "QPushButton { background-color: #ebf8ff; color: #3182ce; border: 1px solid #bee3f8; "
            "border-radius: 6px; padding: 5px 12px; font-weight: bold; font-size: 11px; }"
            "QPushButton:hover { background-color: #bee3f8; }")
        btn_detail.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detail.clicked.connect(lambda: self.detail_clicked.emit(self.room))

        btn_book = QPushButton("Đặt phòng")
        if self.room.status == 'available':
            btn_book.setStyleSheet(
                "QPushButton { background-color: #e6fffa; color: #0b8480; border: 1px solid #b2f5ea; "
                "border-radius: 6px; padding: 5px 12px; font-weight: bold; font-size: 11px; }"
                "QPushButton:hover { background-color: #b2f5ea; }")
            btn_book.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_book.clicked.connect(lambda: self.book_clicked.emit(self.room))
        else:
            btn_book.setEnabled(False)
            btn_book.setStyleSheet(
                "QPushButton { background-color: #edf2f7; color: #a0aec0; border: 1px solid #e2e8f0; "
                "border-radius: 6px; padding: 5px 12px; font-weight: bold; font-size: 11px; }")

        btn_row.addWidget(btn_detail)
        btn_row.addWidget(btn_book)
        layout.addLayout(btn_row)


# ═══════════════════════════════════════════════════════════════
# GuestRoomDetailDialog
# ═══════════════════════════════════════════════════════════════
class GuestRoomDetailDialog(QDialog):
    """Dialog xem chi tiết phòng (Guest)."""

    def __init__(self, room: Room, parent=None):
        super().__init__(parent)
        self.room = room
        self.setWindowTitle(f"Chi tiết phòng {room.room_number}")
        self.setMinimumSize(500, 550)
        self.setStyleSheet("QDialog { background-color: white; } QLabel { color: #2d3748; }")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        if self.room.images:
            img_scroll = QScrollArea()
            img_scroll.setFixedHeight(200)
            img_scroll.setWidgetResizable(True)
            img_scroll.setStyleSheet("QScrollArea { border: 1px solid #e2e8f0; border-radius: 8px; background: #f7fafc; }")
            img_container = QWidget()
            img_layout = QHBoxLayout(img_container)
            img_layout.setSpacing(10)
            img_layout.setContentsMargins(10, 10, 10, 10)
            img_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            for img_rel in self.room.images:
                img_path = str(BASE_DIR / 'data' / img_rel)
                if os.path.exists(img_path):
                    pixmap = QPixmap(img_path)
                    if not pixmap.isNull():
                        scaled = pixmap.scaled(QSize(250, 180),
                                               Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)
                        lbl_img = QLabel()
                        lbl_img.setPixmap(scaled)
                        lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        lbl_img.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 4px; background: white;")
                        img_layout.addWidget(lbl_img)
            img_scroll.setWidget(img_container)
            layout.addWidget(img_scroll)
        else:
            no_img = QLabel("📷 Chưa có ảnh phòng")
            no_img.setFixedHeight(80)
            no_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_img.setStyleSheet("color: #a0aec0; font-size: 14px; background: #f7fafc; "
                                  "border: 2px dashed #cbd5e0; border-radius: 8px;")
            layout.addWidget(no_img)

        title = QLabel(f"🏠 Phòng {self.room.room_number}")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        status_map = {
            'available': ('● Trống', '#38a169'),
            'occupied': ('● Đang thuê', '#3182ce'),
            'maintenance': ('● Bảo trì', '#e53e3e'),
        }
        st, sc = status_map.get(self.room.status, ('?', '#718096'))
        lbl_st = QLabel(st)
        lbl_st.setStyleSheet(f"color: {sc}; font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl_st)

        info_items = [
            ("Giá phòng", f"{self.room.price:,.0f} VNĐ/tháng"),
            ("Tiền cọc", f"{self.room.deposit:,.0f} VNĐ"),
            ("Tầng", f"Tầng {self.room.floor}"),
            ("Diện tích", f"{self.room.area} m²"),
            ("Loại phòng", getattr(self.room, 'room_type', 'Phòng đơn') or 'Phòng đơn'),
            ("Tiện nghi", ", ".join(self.room.amenities) if self.room.amenities else "—"),
            ("Mô tả", self.room.description or "—"),
        ]
        for label, value in info_items:
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setFixedWidth(100)
            lbl.setStyleSheet("color: #718096; font-weight: bold;")
            val = QLabel(value)
            val.setWordWrap(True)
            row.addWidget(lbl)
            row.addWidget(val, 1)
            layout.addLayout(row)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Đóng")
        btn_close.setStyleSheet(
            "QPushButton { background-color: #f7fafc; border: 1px solid #cbd5e0; "
            "border-radius: 6px; padding: 8px 16px; font-weight: bold; color: #4a5568; }"
            "QPushButton:hover { background-color: #edf2f7; }")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)


# ═══════════════════════════════════════════════════════════════
# DangKyPhongView — Main view
# ═══════════════════════════════════════════════════════════════
class DangKyPhongView(QWidget):
    """Widget đăng ký phòng — Được nhúng vào GuestRegisterWindow."""

    def __init__(self, user=None, container=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.container = container
        self.room_service = container.room_service if container else None
        self.contract_service = container.contract_service if container else None
        self.guest_service = container.guest_service if container else None
        self._search_text = ""
        self._build_ui()
        self.refresh_rooms()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)

        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm tên phòng...")
        self.search_input.setStyleSheet(
            "QLineEdit { background-color: #f7fafc; border: 1px solid #e2e8f0; "
            "border-radius: 8px; padding: 8px 15px; font-size: 13px; }")
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self._on_search)
        top_bar.addWidget(self.search_input)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tất cả trạng thái", "Trống", "Đang thuê"])
        self.filter_combo.setStyleSheet(
            "QComboBox { background-color: #f7fafc; border: 1px solid #e2e8f0; "
            "border-radius: 8px; padding: 8px 12px; font-size: 13px; }")
        self.filter_combo.currentIndexChanged.connect(self._on_filter)
        top_bar.addWidget(self.filter_combo)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        self.lbl_count = QLabel("Tất cả phòng (0)")
        self.lbl_count.setStyleSheet("color: #2d3748; font-size: 14px; font-weight: bold;")
        main_layout.addWidget(self.lbl_count)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background-color: transparent;")
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self.cards_container)
        main_layout.addWidget(scroll, 1)

    def refresh_rooms(self):
        if not self.room_service:
            return
        rooms = self.room_service.get_all_rooms()
        filter_map = {1: 'available', 2: 'occupied'}
        status_filter = filter_map.get(self.filter_combo.currentIndex())
        if status_filter:
            rooms = [r for r in rooms if r.status == status_filter]
        if self._search_text:
            q = self._search_text.lower()
            rooms = [r for r in rooms if q in r.room_number.lower()]

        self.lbl_count.setText(f"Tất cả phòng ({len(rooms)})")

        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        cols = 4
        for i, room in enumerate(rooms):
            card = GuestRoomCard(room)
            card.detail_clicked.connect(self._on_detail)
            card.book_clicked.connect(self._on_book)
            self.cards_layout.addWidget(card, i // cols, i % cols)

        total_rows = (len(rooms) + cols - 1) // cols if rooms else 0
        for r in range(total_rows):
            self.cards_layout.setRowStretch(r, 0)
        self.cards_layout.setRowStretch(total_rows, 1)

    def _on_search(self, text):
        self._search_text = text
        self.refresh_rooms()

    def _on_filter(self, idx):
        self.refresh_rooms()

    def _on_detail(self, room: Room):
        dlg = GuestRoomDetailDialog(room, parent=self)
        dlg.exec()

    # ── Booking flow (3 steps) ──
    def _find_guest(self):
        if not self.guest_service or not self.user:
            return None
        # Try by user_id first
        user_id = getattr(self.user, 'id', None)
        if user_id:
            g = self.guest_service.get_guest_by_user_id(user_id)
            if g:
                return g
        # Fallback: email/phone
        all_guests = self.guest_service.get_all_guests()
        for g in all_guests:
            if getattr(g, 'email', None) == getattr(self.user, 'email', None):
                return g
            if getattr(g, 'phone', None) == getattr(self.user, 'phone', None):
                return g
        return None

    def _on_book(self, room: Room):
        wizard = BookingWizard(room, self.user, guest_service=self.guest_service, parent=self)
        if wizard.exec() != QDialog.DialogCode.Accepted:
            return

        info = wizard.personal_info

        # Tìm hoặc tạo Guest
        guest = self._find_guest()
        if not guest and self.guest_service:
            from models.guest import Guest
            guest = Guest(
                user_id=getattr(self.user, 'id', 0),
                full_name=info.get('full_name', ''),
                phone=getattr(self.user, 'phone', ''),
                email=getattr(self.user, 'email', ''),
                id_card=info.get('id_card', ''),
            )
            ok, msg = self.guest_service.create_guest(guest)
            if ok:
                # Re-fetch to get the ID
                guest = self._find_guest()

        if not guest:
            show_warning(self, "Lỗi",
                "Không thể tạo hồ sơ khách thuê.\nVui lòng liên hệ quản lý.")
            return

        # Cập nhật thông tin cá nhân
        guest.full_name = info.get('full_name', guest.full_name)
        guest.id_card = info.get('id_card', guest.id_card)
        if self.guest_service:
            try:
                self.guest_service.update_guest(guest)
            except Exception:
                pass

        if not self.contract_service:
            show_warning(self, "Lỗi", "Dịch vụ hợp đồng chưa sẵn sàng.")
            return

        # Tạo hợp đồng pending
        now = datetime.now()
        end_date = now.replace(year=now.year + 1)
        number = f"HD{now.strftime('%Y%m')}{len(self.contract_service.get_all()) + 1:03d}"
        contract = Contract(
            contract_number=number,
            room_id=room.id,
            guest_id=guest.id,
            start_date=now.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            monthly_rent=room.price,
            deposit=room.deposit,
            status='pending',
        )
        self.contract_service.contract_repo.create(contract)

        # Success dialog
        self._show_success(room, number)

    def _show_success(self, room: Room, contract_number: str):
        dlg = QDialog(self)
        dlg.setWindowTitle("Đăng ký thành công")
        dlg.setFixedSize(420, 280)
        dlg.setStyleSheet("QDialog { background-color: white; }")
        layout = QVBoxLayout(dlg)
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 25)

        icon = QLabel("✅")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("Đăng ký phòng thành công!")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #38a169;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        info = QLabel(
            f"Phòng: <b>{room.room_number}</b><br>"
            f"Mã hợp đồng: <b>{contract_number}</b><br>"
            f"Trạng thái: <b style='color: #d69e2e;'>⏳ Chờ duyệt</b><br><br>"
            f"Quản lý sẽ xem xét và phê duyệt yêu cầu của bạn."
        )
        info.setStyleSheet("color: #4a5568; font-size: 13px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addStretch()

        btn = QPushButton("Đã hiểu")
        btn.setMinimumHeight(40)
        btn.setStyleSheet(
            "QPushButton { background-color: #0b8480; color: white; border: none; "
            "border-radius: 8px; padding: 10px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #096c69; }")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.exec()
