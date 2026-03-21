"""
AccountManagementView — Quản lý tài khoản Admin.
Profile card + tabbed settings (personal info / security).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QMessageBox, QScrollArea, QStackedWidget,
    QRadioButton, QSizePolicy, QComboBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

from models.user import User
from ui.UI_Common.custom_popup import show_success, show_error, show_warning, show_info, ask_question, ask_danger
from ui.UI_Common.bank_utils import load_bank_info, save_bank_info, get_qr_path

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


class AccountManagementView(QWidget):
    """Widget quản lý tài khoản — nhúng AdminWindow."""
    logout_requested = pyqtSignal()

    def __init__(self, user: User = None, auth_service=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.auth_service = auth_service
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

        pill = QLabel("CHỦ TRỌ")
        pill.setStyleSheet(
            "background-color: #ead6d6; color: #b84f4f; border-radius: 15px; "
            "padding: 6px 16px; font-weight: bold; font-size: 13px;")
        pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pill.setFixedWidth(100)
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
        tab_row = QHBoxLayout(); tab_row.setSpacing(15)
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

        self.btn_tab_bank = QPushButton("💳 THÔNG TIN NGÂN HÀNG")
        self.btn_tab_bank.setMinimumHeight(40)
        self.btn_tab_bank.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tab_bank.clicked.connect(lambda: self._switch_tab(2))
        tab_row.addWidget(self.btn_tab_bank)
        self._tab_buttons.append(self.btn_tab_bank)

        tab_row.addStretch()
        sc_lay.addLayout(tab_row)

        # Stacked settings pages
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Page 0: Personal Info
        page_personal = QWidget()
        pp_lay = QVBoxLayout(page_personal)
        pp_lay.setSpacing(8)
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

        pp_lay.addSpacing(20)

        btn_update_personal = QPushButton("Cập nhật")
        btn_update_personal.setMinimumSize(160, 50)
        btn_update_personal.setStyleSheet(
            "QPushButton { background-color: #009688; color: white; border-radius: 8px; "
            "padding: 12px 25px; font-weight: bold; font-size: 16px; }"
            "QPushButton:hover { background-color: #00796b; }")
        btn_update_personal.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_update_personal.clicked.connect(self._save_personal)
        r = QHBoxLayout(); r.addStretch(); r.addWidget(btn_update_personal)
        pp_lay.addLayout(r)

        pp_lay.addStretch()

        self.stack.addWidget(page_personal)

        # Page 1: Security
        page_security = QWidget()
        ps_lay = QVBoxLayout(page_security)
        ps_lay.setSpacing(8)
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

        ps_lay.addSpacing(20)

        btn_change_pass = QPushButton("Đổi mật khẩu")
        btn_change_pass.setMinimumSize(160, 50)
        btn_change_pass.setStyleSheet(
            "QPushButton { background-color: #009688; color: white; border-radius: 8px; "
            "padding: 12px 25px; font-weight: bold; font-size: 16px; }"
            "QPushButton:hover { background-color: #00796b; }")
        btn_change_pass.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_change_pass.clicked.connect(self._change_password)
        r2 = QHBoxLayout(); r2.addStretch(); r2.addWidget(btn_change_pass)
        ps_lay.addLayout(r2)

        ps_lay.addStretch()

        self.stack.addWidget(page_security)

        # Page 2: Bank Info
        page_bank = QWidget()
        pb_lay = QVBoxLayout(page_bank)
        pb_lay.setSpacing(12)
        pb_lay.setContentsMargins(0, 0, 0, 0)

        pb_lay.addWidget(self._label("Tên ngân hàng"))
        self.inp_bank_name = QComboBox()
        self.inp_bank_name.setMinimumHeight(45)
        self.inp_bank_name.setStyleSheet(COMBO_STYLE)
        self.inp_bank_name.setEditable(True)
        self.inp_bank_name.addItems([
            "— Chọn ngân hàng —", "Vietcombank", "BIDV", "Agribank",
            "Techcombank", "VPBank", "MBBank", "ACB", "TPBank",
            "Sacombank", "VietinBank", "SHB", "HDBank", "OCB",
            "LienVietPostBank", "MSB", "VIB", "SeABank", "Khác"
        ])
        pb_lay.addWidget(self.inp_bank_name)

        pb_lay.addWidget(self._label("Chi nhánh"))
        self.inp_bank_branch = QLineEdit()
        self.inp_bank_branch.setPlaceholderText("Ví dụ: CN DA NANG")
        self.inp_bank_branch.setMinimumHeight(45)
        self.inp_bank_branch.setStyleSheet(INPUT_STYLE)
        pb_lay.addWidget(self.inp_bank_branch)

        pb_lay.addWidget(self._label("Tên chủ tài khoản"))
        self.inp_bank_holder = QLineEdit()
        self.inp_bank_holder.setPlaceholderText("Ví dụ: NGUYEN VAN A")
        self.inp_bank_holder.setMinimumHeight(45)
        self.inp_bank_holder.setStyleSheet(INPUT_STYLE)
        pb_lay.addWidget(self.inp_bank_holder)

        pb_lay.addWidget(self._label("Số tài khoản"))
        self.inp_bank_account = QLineEdit()
        self.inp_bank_account.setPlaceholderText("Ví dụ: 1234567890")
        self.inp_bank_account.setMinimumHeight(45)
        self.inp_bank_account.setStyleSheet(INPUT_STYLE)
        pb_lay.addWidget(self.inp_bank_account)

        # QR Code upload
        pb_lay.addWidget(self._label("Mã QR chuyển khoản"))
        qr_row = QHBoxLayout(); qr_row.setSpacing(10)
        btn_upload_qr = QPushButton("⬆ Tải ảnh QR lên")
        btn_upload_qr.setMinimumHeight(40)
        btn_upload_qr.setStyleSheet(
            "QPushButton { background-color: #e6fffa; color: #0b8480; border: 1px solid #b2dfdb; "
            "border-radius: 8px; padding: 8px 16px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #b2dfdb; }")
        btn_upload_qr.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_upload_qr.clicked.connect(self._upload_qr)
        qr_row.addWidget(btn_upload_qr)
        self.lbl_qr_file = QLabel("Chưa có tệp nào được chọn")
        self.lbl_qr_file.setStyleSheet("color: #a0aec0; font-size: 12px; font-weight: normal;")
        qr_row.addWidget(self.lbl_qr_file)
        qr_row.addStretch()
        pb_lay.addLayout(qr_row)

        # QR preview
        self.lbl_qr_preview = QLabel()
        self.lbl_qr_preview.setFixedSize(150, 150)
        self.lbl_qr_preview.setStyleSheet(
            "background-color: white; border: 1px solid #e2e8f0; border-radius: 8px;")
        self.lbl_qr_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_qr_preview.hide()
        pb_lay.addWidget(self.lbl_qr_preview)
        self._qr_path = ""

        pb_lay.addStretch()

        btn_save_bank = QPushButton("Lưu thông tin")
        btn_save_bank.setMinimumSize(160, 50)
        btn_save_bank.setStyleSheet(
            "QPushButton { background-color: #009688; color: white; border-radius: 8px; "
            "padding: 12px 25px; font-weight: bold; font-size: 16px; }"
            "QPushButton:hover { background-color: #00796b; }")
        btn_save_bank.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save_bank.clicked.connect(self._save_bank)
        r3 = QHBoxLayout(); r3.addStretch(); r3.addWidget(btn_save_bank)
        pb_lay.addLayout(r3)

        self.stack.addWidget(page_bank)

        sc_lay.addWidget(self.stack)
        scroll.setWidget(scroll_content)
        s_lay.addWidget(scroll)
        main.addWidget(settings)

        # Default tab
        self._switch_tab(0)

    def _label(self, text: str) -> QLabel:
        lb = QLabel(text)
        lb.setStyleSheet(LABEL_STYLE)
        return lb

    def _switch_tab(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self._tab_buttons):
            btn.setStyleSheet(self._tab_active if i == index else self._tab_style)

    def _load_data(self):
        if not self.user:
            return
        self.lbl_name.setText(self.user.full_name or "Your name")
        self.lbl_email.setText(self.user.email or "email@gmail.com")
        self.inp_name.setText(self.user.full_name or "")
        self.inp_phone.setText(str(self.user.phone) if self.user.phone else "")
        self.inp_email.setText(self.user.email or "")
        self._load_bank_data()

    def _load_bank_data(self):
        """Khôi phục thông tin ngân hàng đã lưu."""
        info = load_bank_info()
        if not info:
            return
        # Bank name
        bank_name = info.get('bank_name', '')
        if bank_name:
            idx = self.inp_bank_name.findText(bank_name)
            if idx >= 0:
                self.inp_bank_name.setCurrentIndex(idx)
            else:
                self.inp_bank_name.setEditText(bank_name)
        # Branch
        self.inp_bank_branch.setText(info.get('branch', ''))
        # Holder
        self.inp_bank_holder.setText(info.get('account_holder', ''))
        # Account number
        self.inp_bank_account.setText(info.get('account_number', ''))
        # QR preview
        qr = get_qr_path()
        if qr:
            pixmap = QPixmap(qr).scaled(150, 150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.lbl_qr_preview.setPixmap(pixmap)
            self.lbl_qr_preview.show()
            self.lbl_qr_file.setText('qr_payment.png')
            self.lbl_qr_file.setStyleSheet('color: #2d3748; font-size: 12px; font-weight: bold;')

    def _save_personal(self):
        if not self.user or not self.auth_service:
            return
        name = self.inp_name.text().strip()
        phone = self.inp_phone.text().strip()
        email = self.inp_email.text().strip()

        if not name:
            show_warning(self, "Lỗi", "Họ và tên không được trống"); return
        if not phone or len(phone) != 10 or not phone.isdigit():
            show_warning(self, "Lỗi", "SĐT phải đúng 10 chữ số"); return
        if not email or '@gmail.com' not in email:
            show_warning(self, "Lỗi", "Email phải có dạng abc@gmail.com"); return

        self.user.full_name = name
        self.user.phone = phone
        self.user.email = email

        ok = self.auth_service.user_repo.update(self.user)
        if ok:
            self.lbl_name.setText(name)
            self.lbl_email.setText(email)
            show_success(self, "Thành công", "Cập nhật thông tin thành công")
        else:
            show_warning(self, "Lỗi", "Không thể cập nhật")

    def _change_password(self):
        if not self.user or not self.auth_service:
            return
        old = self.inp_old_pass.text()
        new = self.inp_new_pass.text()
        confirm = self.inp_confirm_pass.text()

        if not old:
            show_warning(self, "Lỗi", "Nhập mật khẩu cũ"); return
        if not self.user.check_password(old):
            show_warning(self, "Lỗi", "Mật khẩu cũ không đúng"); return
        if not new or len(new) < 6:
            show_warning(self, "Lỗi", "Mật khẩu mới tối thiểu 6 ký tự"); return
        if new != confirm:
            show_warning(self, "Lỗi", "Mật khẩu mới không khớp"); return

        self.user.set_password(new)
        ok = self.auth_service.user_repo.update(self.user)
        if ok:
            self.inp_old_pass.clear()
            self.inp_new_pass.clear()
            self.inp_confirm_pass.clear()
            show_success(self, "Thành công", "Đổi mật khẩu thành công")
        else:
            show_warning(self, "Lỗi", "Không thể đổi mật khẩu")

    def _upload_qr(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh QR", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)")
        if not path:
            return
        import os
        self._qr_path = path
        self.lbl_qr_file.setText(os.path.basename(path))
        self.lbl_qr_file.setStyleSheet("color: #2d3748; font-size: 12px; font-weight: bold;")
        pixmap = QPixmap(path).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
        self.lbl_qr_preview.setPixmap(pixmap)
        self.lbl_qr_preview.show()

    def _save_bank(self):
        bank = self.inp_bank_name.currentText().strip()
        account = self.inp_bank_account.text().strip()
        holder = self.inp_bank_holder.text().strip()
        if not bank or bank == "— Chọn ngân hàng —":
            show_warning(self, "Lỗi", "Vui lòng chọn ngân hàng"); return
        if not account:
            show_warning(self, "Lỗi", "Vui lòng nhập số tài khoản"); return
        if not holder:
            show_warning(self, "Lỗi", "Vui lòng nhập tên chủ tài khoản"); return

        # Copy QR image to data folder if selected
        has_qr = False
        if self._qr_path:
            import shutil
            from ui.UI_Common.bank_utils import QR_IMAGE_PATH
            import os
            os.makedirs(os.path.dirname(QR_IMAGE_PATH), exist_ok=True)
            try:
                shutil.copy2(self._qr_path, QR_IMAGE_PATH)
                has_qr = True
            except Exception as e:
                show_warning(self, "Lỗi", f"Không thể lưu QR: {e}"); return
        else:
            has_qr = bool(get_qr_path())

        data = {
            'bank_name': bank,
            'branch': self.inp_bank_branch.text().strip(),
            'account_holder': holder,
            'account_number': account,
            'qr_image': 'qr_payment.png' if has_qr else '',
        }
        save_bank_info(data)
        show_success(self, "Thành công", "Lưu thông tin ngân hàng thành công")

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
