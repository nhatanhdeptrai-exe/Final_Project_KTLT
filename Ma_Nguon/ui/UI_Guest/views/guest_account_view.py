"""
GuestAccountView — Quản lý tài khoản Guest.
Profile card (avatar + tên + email + badge KHÁCH THUÊ + đăng xuất)
+ Settings card (2 tabs: Thông tin cá nhân / Bảo mật).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QMessageBox, QScrollArea, QStackedWidget,
    QRadioButton, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ui.UI_Common.custom_popup import show_success, show_error, show_warning, show_info, ask_question, ask_danger


INPUT_STYLE = (
    "QLineEdit { background-color: white; border: none; border-radius: 8px; "
    "padding: 10px 15px; font-size: 14px; color: #4a5568; }"
    "QLineEdit:focus { border: 2px solid #0b8480; }"
)
COMBO_STYLE = (
    "QComboBox { background-color: white; border: none; border-radius: 8px; "
    "padding: 10px 15px; font-size: 14px; color: #4a5568; }"
)
LABEL_STYLE = "font-weight: bold; color: #1e293b; font-size: 14px;"


class GuestAccountView(QWidget):
    """Widget quản lý tài khoản — Guest."""
    logout_requested = pyqtSignal()

    def __init__(self, user=None, auth_service=None, guest_service=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.auth_service = auth_service
        self.guest_service = guest_service
        self._guest = None
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        main = QHBoxLayout(self)
        main.setContentsMargins(40, 40, 40, 40)
        main.setSpacing(30)

        # ── Left: Profile Card ──
        self.profile_card = QFrame()
        self.profile_card.setFixedWidth(350)
        self.profile_card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.profile_card.setStyleSheet(
            "QFrame#ProfileCard { background-color: white; border-radius: 12px; "
            "border: 1px solid #e2e8f0; }")
        self.profile_card.setObjectName("ProfileCard")
        pc_lay = QVBoxLayout(self.profile_card)
        pc_lay.setSpacing(10)
        pc_lay.setContentsMargins(20, 50, 20, 30)
        pc_lay.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Avatar
        avatar = QLabel("👤")
        avatar.setFixedSize(120, 120)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(
            "background-color: #8c8c8c; border-radius: 60px; font-size: 50px; color: white;")
        pc_lay.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignHCenter)

        pc_lay.addSpacing(10)

        self.lbl_name = QLabel("Your name")
        self.lbl_name.setStyleSheet("font-size: 22px; font-weight: bold; color: #2d3748;")
        self.lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pc_lay.addWidget(self.lbl_name)

        self.lbl_email = QLabel("email@gmail.com")
        self.lbl_email.setStyleSheet("font-size: 15px; color: #718096;")
        self.lbl_email.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pc_lay.addWidget(self.lbl_email)

        pc_lay.addSpacing(15)

        pill = QLabel("KHÁCH THUÊ")
        pill.setStyleSheet(
            "background-color: #dbeafe; color: #3182ce; border-radius: 15px; "
            "padding: 6px 16px; font-weight: bold; font-size: 13px;")
        pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pill.setFixedWidth(120)
        pc_lay.addWidget(pill, alignment=Qt.AlignmentFlag.AlignHCenter)

        pc_lay.addSpacing(5)

        btn_logout = QPushButton("🚪 Đăng xuất")
        btn_logout.setMinimumSize(130, 40)
        btn_logout.setStyleSheet(
            "QPushButton { background-color: #8bbcb9; border: none; border-radius: 15px; "
            "padding: 8px 20px; color: white; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #7aa9a6; }")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.clicked.connect(self._on_logout)
        pc_lay.addWidget(btn_logout, alignment=Qt.AlignmentFlag.AlignHCenter)

        pc_lay.addStretch()

        # Zalo support
        zalo_lbl = QLabel("📞 Liên hệ hỗ trợ: 1234567890")
        zalo_lbl.setStyleSheet("color: #718096; font-size: 12px; font-weight: normal;")
        zalo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pc_lay.addWidget(zalo_lbl)

        main.addWidget(self.profile_card)

        # ── Right: Settings Card ──
        settings = QFrame()
        settings.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        settings.setStyleSheet(
            "QFrame#SettingsCard { background-color: #dbe4e4; border-radius: 12px; }")
        settings.setObjectName("SettingsCard")
        s_lay = QVBoxLayout(settings)
        s_lay.setContentsMargins(0, 0, 0, 0)
        s_lay.setSpacing(0)

        # Header
        header = QFrame()
        header.setMinimumHeight(130)
        header.setStyleSheet(
            "background-color: #0b8480; border-top-left-radius: 12px; "
            "border-top-right-radius: 12px;")
        header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        s_lay.addWidget(header)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        sc_lay = QVBoxLayout(scroll_content)
        sc_lay.setSpacing(25)
        sc_lay.setContentsMargins(40, 30, 40, 40)

        # Tab buttons
        tab_row = QHBoxLayout()
        tab_row.setSpacing(15)
        TAB_STYLE = (
            "QPushButton { background-color: #c1d5d5; color: white; border-radius: 18px; "
            "padding: 10px 20px; font-weight: bold; font-size: 13px; border: none; }"
            "QPushButton:hover { background-color: #a3c4c4; }")
        TAB_ACTIVE = (
            "QPushButton { background-color: #8faaa9; color: white; border-radius: 18px; "
            "padding: 10px 20px; font-weight: bold; font-size: 13px; border: none; }")

        self._tab_style = TAB_STYLE
        self._tab_active = TAB_ACTIVE
        self._tab_buttons = []

        self.btn_tab_personal = QPushButton("👤 THÔNG TIN CÁ NHÂN")
        self.btn_tab_personal.setMinimumHeight(40)
        self.btn_tab_personal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tab_personal.clicked.connect(lambda: self._switch_tab(0))
        tab_row.addWidget(self.btn_tab_personal)
        self._tab_buttons.append(self.btn_tab_personal)

        self.btn_tab_security = QPushButton("🛡 BẢO MẬT")
        self.btn_tab_security.setMinimumHeight(40)
        self.btn_tab_security.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tab_security.clicked.connect(lambda: self._switch_tab(1))
        tab_row.addWidget(self.btn_tab_security)
        self._tab_buttons.append(self.btn_tab_security)

        tab_row.addStretch()
        sc_lay.addLayout(tab_row)

        # Stacked settings pages
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # ── Page 0: Personal Info ──
        page_personal = QWidget()
        pp_lay = QVBoxLayout(page_personal)
        pp_lay.setSpacing(12)
        pp_lay.setContentsMargins(0, 0, 0, 0)

        pp_lay.addWidget(self._label("Họ và tên"))
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Ví dụ: NGUYEN VAN A")
        self.inp_name.setMinimumHeight(45)
        self.inp_name.setStyleSheet(INPUT_STYLE)
        pp_lay.addWidget(self.inp_name)

        pp_lay.addWidget(self._label("Số điện thoại"))
        self.inp_phone = QLineEdit()
        self.inp_phone.setPlaceholderText("0987654321")
        self.inp_phone.setMinimumHeight(45)
        self.inp_phone.setStyleSheet(INPUT_STYLE)
        pp_lay.addWidget(self.inp_phone)

        pp_lay.addWidget(self._label("Email"))
        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("Ví dụ: email@gmail.com")
        self.inp_email.setMinimumHeight(45)
        self.inp_email.setStyleSheet(INPUT_STYLE)
        pp_lay.addWidget(self.inp_email)

        pp_lay.addWidget(self._label("Số CCCD / CMND"))
        self.inp_cccd = QLineEdit()
        self.inp_cccd.setPlaceholderText("012345678910")
        self.inp_cccd.setMinimumHeight(45)
        self.inp_cccd.setStyleSheet(INPUT_STYLE)
        pp_lay.addWidget(self.inp_cccd)

        pp_lay.addWidget(self._label("Giới tính"))
        gender_row = QHBoxLayout()
        self.rb_male = QRadioButton("Nam")
        self.rb_male.setChecked(True)
        self.rb_male.setStyleSheet("font-weight: bold; color: #4a5568; font-size: 14px;")
        self.rb_female = QRadioButton("Nữ")
        self.rb_female.setStyleSheet("font-weight: bold; color: #4a5568; font-size: 14px;")
        gender_row.addWidget(self.rb_male)
        gender_row.addWidget(self.rb_female)
        gender_row.addStretch()
        pp_lay.addLayout(gender_row)

        pp_lay.addWidget(self._label("Ngày sinh"))
        dob_row = QHBoxLayout()
        dob_row.setSpacing(15)
        self.cmb_day = QComboBox()
        self.cmb_day.setMinimumHeight(45)
        self.cmb_day.setStyleSheet(COMBO_STYLE)
        self.cmb_day.addItem("Ngày")
        self.cmb_day.addItems([str(i) for i in range(1, 32)])
        self.cmb_month = QComboBox()
        self.cmb_month.setMinimumHeight(45)
        self.cmb_month.setStyleSheet(COMBO_STYLE)
        self.cmb_month.addItem("Tháng")
        self.cmb_month.addItems([str(i) for i in range(1, 13)])
        self.cmb_year = QComboBox()
        self.cmb_year.setMinimumHeight(45)
        self.cmb_year.setStyleSheet(COMBO_STYLE)
        self.cmb_year.addItem("Năm")
        self.cmb_year.addItems([str(i) for i in range(2010, 1949, -1)])
        dob_row.addWidget(self.cmb_day, 1)
        dob_row.addWidget(self.cmb_month, 1)
        dob_row.addWidget(self.cmb_year, 1)
        pp_lay.addLayout(dob_row)

        pp_lay.addSpacing(20)

        btn_update = QPushButton("Cập nhật")
        btn_update.setMinimumSize(160, 50)
        btn_update.setStyleSheet(
            "QPushButton { background-color: #009688; color: white; border-radius: 8px; "
            "padding: 12px 25px; font-weight: bold; font-size: 16px; }"
            "QPushButton:hover { background-color: #00796b; }")
        btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_update.clicked.connect(self._save_personal)
        r = QHBoxLayout()
        r.addStretch()
        r.addWidget(btn_update)
        pp_lay.addLayout(r)

        self.stack.addWidget(page_personal)

        # ── Page 1: Security ──
        page_security = QWidget()
        ps_lay = QVBoxLayout(page_security)
        ps_lay.setSpacing(12)
        ps_lay.setContentsMargins(0, 0, 0, 0)

        ps_lay.addWidget(self._label("Mật khẩu cũ"))
        self.inp_old_pass = QLineEdit()
        self.inp_old_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_old_pass.setMinimumHeight(45)
        self.inp_old_pass.setStyleSheet(INPUT_STYLE)
        ps_lay.addWidget(self.inp_old_pass)

        ps_lay.addWidget(self._label("Mật khẩu mới"))
        self.inp_new_pass = QLineEdit()
        self.inp_new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_new_pass.setMinimumHeight(45)
        self.inp_new_pass.setStyleSheet(INPUT_STYLE)
        ps_lay.addWidget(self.inp_new_pass)

        ps_lay.addWidget(self._label("Xác nhận mật khẩu mới"))
        self.inp_confirm_pass = QLineEdit()
        self.inp_confirm_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_confirm_pass.setMinimumHeight(45)
        self.inp_confirm_pass.setStyleSheet(INPUT_STYLE)
        ps_lay.addWidget(self.inp_confirm_pass)

        ps_lay.addStretch()

        btn_change = QPushButton("Đổi mật khẩu")
        btn_change.setMinimumSize(160, 50)
        btn_change.setStyleSheet(
            "QPushButton { background-color: #009688; color: white; border-radius: 8px; "
            "padding: 12px 25px; font-weight: bold; font-size: 16px; }"
            "QPushButton:hover { background-color: #00796b; }")
        btn_change.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_change.clicked.connect(self._change_password)
        r2 = QHBoxLayout()
        r2.addStretch()
        r2.addWidget(btn_change)
        ps_lay.addLayout(r2)

        self.stack.addWidget(page_security)

        sc_lay.addWidget(self.stack)
        scroll.setWidget(scroll_content)
        s_lay.addWidget(scroll)
        main.addWidget(settings)

        self._switch_tab(0)

    # ── Helpers ──
    def _label(self, text: str) -> QLabel:
        lb = QLabel(text)
        lb.setStyleSheet(LABEL_STYLE)
        return lb

    def _switch_tab(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self._tab_buttons):
            btn.setStyleSheet(self._tab_active if i == index else self._tab_style)

    # ── Load data ──
    def _load_data(self):
        if not self.user:
            return
        self._guest = None
        self.lbl_name.setText(self.user.full_name or "Your name")
        self.lbl_email.setText(self.user.email or "email@gmail.com")
        self.inp_name.setText(self.user.full_name or "")
        self.inp_phone.setText(str(self.user.phone) if self.user.phone else "")
        self.inp_email.setText(self.user.email or "")

        # Load guest data
        if self.guest_service:
            try:
                self._guest = self.guest_service.get_guest_by_user_id(
                    getattr(self.user, 'id', 0))
            except Exception:
                self._guest = None
            if self._guest:
                self.inp_cccd.setText(getattr(self._guest, 'id_card', '') or '')
                gender = getattr(self._guest, 'gender', '')
                if gender == 'Nữ':
                    self.rb_female.setChecked(True)
                else:
                    self.rb_male.setChecked(True)
                # Restore DOB
                dob = getattr(self._guest, 'dob', '')
                if dob:
                    try:
                        parts = dob.split('/')
                        if len(parts) == 3:
                            day, month, year = parts
                        elif '-' in dob:
                            parts = dob.split('-')
                            year, month, day = parts
                        else:
                            day = month = year = ''
                        if day:
                            idx_d = self.cmb_day.findText(str(int(day)))
                            if idx_d >= 0: self.cmb_day.setCurrentIndex(idx_d)
                        if month:
                            idx_m = self.cmb_month.findText(str(int(month)))
                            if idx_m >= 0: self.cmb_month.setCurrentIndex(idx_m)
                        if year:
                            idx_y = self.cmb_year.findText(str(int(year)))
                            if idx_y >= 0: self.cmb_year.setCurrentIndex(idx_y)
                    except Exception:
                        pass

    # ── Save personal info ──
    def _save_personal(self):
        if not self.user or not self.auth_service:
            return
        name = self.inp_name.text().strip()
        phone = self.inp_phone.text().strip()
        email = self.inp_email.text().strip()
        cccd = self.inp_cccd.text().strip()

        # ── Validation ──
        if not name:
            return show_warning(self, "Lỗi", "Họ và tên không được trống")
        if phone and (not phone.isdigit() or len(phone) != 10):
            return show_warning(self, "Lỗi", "SĐT phải đúng 10 chữ số")
        if email and '@gmail.com' not in email:
            return show_warning(self, "Lỗi", "Email phải có dạng abc@gmail.com")
        if cccd and (not cccd.isdigit() or len(cccd) != 12):
            return show_warning(self, "Lỗi", "Số CCCD/CMND phải đủ 12 chữ số")

        # Build DOB string from comboboxes
        day = self.cmb_day.currentText()
        month = self.cmb_month.currentText()
        year = self.cmb_year.currentText()
        dob = ''
        if day != 'Ngày' and month != 'Tháng' and year != 'Năm':
            dob = f"{day}/{month}/{year}"

        self.user.full_name = name
        self.user.phone = phone
        self.user.email = email

        try:
            ok = self.auth_service.user_repo.update(self.user)
        except Exception:
            ok = False
        if ok:
            self.lbl_name.setText(name)
            self.lbl_email.setText(email)

        # Update or CREATE guest record
        gender = "Nữ" if self.rb_female.isChecked() else "Nam"
        if self.guest_service:
            try:
                if self._guest:
                    self._guest.full_name = name
                    self._guest.phone = phone
                    self._guest.email = email
                    self._guest.id_card = cccd
                    self._guest.gender = gender
                    self._guest.dob = dob
                    self.guest_service.update_guest(self._guest)
                else:
                    # Auto-create guest record for register users
                    from models.guest import Guest
                    new_guest = Guest(
                        user_id=getattr(self.user, 'id', 0),
                        full_name=name, phone=phone, email=email,
                        id_card=cccd, gender=gender, dob=dob,
                    )
                    self.guest_service.create_guest(new_guest)
                    # Reload to get the saved guest with id
                    self._guest = self.guest_service.get_guest_by_user_id(
                        getattr(self.user, 'id', 0))
            except Exception as e:
                print(f'[guest_account] guest save error: {e}')

        if ok:
            show_success(self, "Thành công", "Cập nhật thông tin thành công")
        else:
            show_warning(self, "Lỗi", "Không thể cập nhật")

    # ── Change password ──
    def _change_password(self):
        if not self.user or not self.auth_service:
            return
        old = self.inp_old_pass.text()
        new = self.inp_new_pass.text()
        confirm = self.inp_confirm_pass.text()

        if not old:
            show_warning(self, "Lỗi", "Nhập mật khẩu cũ")
            return
        if not self.user.check_password(old):
            show_warning(self, "Lỗi", "Mật khẩu cũ không đúng")
            return
        if not new or len(new) < 6:
            show_warning(self, "Lỗi", "Mật khẩu mới tối thiểu 6 ký tự")
            return
        if new != confirm:
            show_warning(self, "Lỗi", "Mật khẩu mới không khớp")
            return

        self.user.set_password(new)
        ok = self.auth_service.user_repo.update(self.user)
        if ok:
            self.inp_old_pass.clear()
            self.inp_new_pass.clear()
            self.inp_confirm_pass.clear()
            show_success(self, "Thành công", "Đổi mật khẩu thành công")
        else:
            show_warning(self, "Lỗi", "Không thể đổi mật khẩu")

    # ── Logout ──
    def _on_logout(self):
        from PyQt6.QtWidgets import QDialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Đăng xuất")
        dlg.setFixedSize(380, 220)
        dlg.setStyleSheet("QDialog { background-color: white; }")
        lay = QVBoxLayout(dlg)
        lay.setSpacing(12)
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
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setStyleSheet(
            "QPushButton { background-color: #f7fafc; color: #4a5568; border: 1px solid #cbd5e0; "
            "border-radius: 8px; padding: 8px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #edf2f7; }")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(dlg.reject)

        btn_ok = QPushButton("🚪  Đăng xuất")
        btn_ok.setMinimumHeight(40)
        btn_ok.setStyleSheet(
            "QPushButton { background-color: #e53e3e; color: white; border: none; "
            "border-radius: 8px; padding: 8px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #c53030; }")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.clicked.connect(dlg.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        lay.addLayout(btn_row)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.logout_requested.emit()
