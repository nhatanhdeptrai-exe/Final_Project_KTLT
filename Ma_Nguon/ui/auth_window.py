"""AuthWindow — File kế thừa từ auth_main_ui.py (KHÔNG SỬA file UI gốc)."""
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QMessageBox, QDialog, QVBoxLayout,
                              QLabel, QLineEdit, QPushButton, QInputDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from ui.auth_main_ui import Ui_AuthWindow  # File tự sinh từ .ui — KHÔNG CHỈNH SỬA


# === Helper: Tạo icon từ Unicode ===
def _make_icon(char: str, color: str = '#888888', size: int = 20) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QColor(color))
    painter.setFont(QFont('Segoe UI Symbol', int(size * 0.65)))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, char)
    painter.end()
    return QIcon(pixmap)


# === Worker Thread: Gửi OTP ngầm ===
class OTPWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, send_func, email):
        super().__init__()
        self.send_func = send_func
        self.email = email

    def run(self):
        ok, msg = self.send_func(self.email)
        self.finished.emit(ok, msg)


# === OTP Dialog ===
class OTPDialog(QDialog):
    def __init__(self, email: str, parent=None):
        super().__init__(parent)
        self.email = email
        self.otp_code = ""
        self._otp_sent = False
        self.setWindowTitle("Xác nhận OTP")
        self.setFixedSize(420, 300)
        self.setStyleSheet("""
            QDialog { background-color: #1a4a49; }
            QLabel { color: white; font-size: 14px; }
            QLabel#lblStatus { color: #f6e05e; font-size: 12px; }
            QLineEdit { background-color: white; border-radius: 6px; padding: 12px;
                        font-size: 24px; letter-spacing: 8px; }
            QPushButton#btnVerify { background-color: #0298a0; color: white;
                                    font-weight: bold; border-radius: 8px; padding: 12px; font-size: 14px; }
            QPushButton#btnVerify:disabled { background-color: #4a6a6a; }
            QPushButton#btnResend { background-color: transparent; color: #a0aec0;
                                    text-decoration: underline; border: none; }
        """)
        layout = QVBoxLayout(self)

        lbl = QLabel(f"Nhập mã OTP gửi đến\n{email}")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        self.lbl_status = QLabel("⏳ Đang gửi mã OTP...")
        self.lbl_status.setObjectName("lblStatus")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)

        self.inp = QLineEdit()
        self.inp.setMaxLength(6)
        self.inp.setPlaceholderText("______")
        self.inp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.inp)

        self.btn_verify = QPushButton("Xác nhận OTP")
        self.btn_verify.setObjectName("btnVerify")
        self.btn_verify.setEnabled(False)
        self.btn_verify.clicked.connect(self.verify)
        layout.addWidget(self.btn_verify)

        btn_re = QPushButton("Gửi lại mã")
        btn_re.setObjectName("btnResend")
        btn_re.clicked.connect(lambda: self.done(2))
        layout.addWidget(btn_re)

    def on_otp_sent(self, success: bool, message: str):
        self._otp_sent = success
        if success:
            self.lbl_status.setText("✅ Đã gửi mã OTP! Kiểm tra email.")
            self.lbl_status.setStyleSheet("color: #68d391; font-size: 12px;")
            self.btn_verify.setEnabled(True)
            self.inp.setFocus()
        else:
            self.lbl_status.setText(f"❌ {message}")
            self.lbl_status.setStyleSheet("color: #fc8181; font-size: 12px;")

    def verify(self):
        self.otp_code = self.inp.text().strip()
        if len(self.otp_code) != 6:
            QMessageBox.warning(self, "Lỗi", "Nhập đủ 6 số")
            return
        self.accept()


# =============================================
# AuthWindow — Kế thừa từ Ui_AuthWindow (file .ui)
# Mọi chỉnh sửa giao diện/logic đều ở đây
# =============================================
class AuthWindow(QWidget, Ui_AuthWindow):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self._worker = None

        # Setup UI từ file tự sinh (KHÔNG dùng loadUi nữa)
        self.setupUi(self)

        # Force refresh style
        self.setStyleSheet(self.styleSheet())

        # Màn hình mặc định = Đăng nhập (index 0)
        self.stackAuth.setCurrentIndex(0)

        # Thêm icon + placeholder vào input fields
        self._setup_icons()
        self._setup_placeholders()

        # Kết nối signals
        if hasattr(self, 'btnLoginsubmit'): self.btnLoginsubmit.clicked.connect(self.login)
        if hasattr(self, 'btnSwitchSignup'): self.btnSwitchSignup.clicked.connect(lambda: self.stackAuth.setCurrentIndex(1))
        if hasattr(self, 'btnForgotPassword'): self.btnForgotPassword.clicked.connect(self.forgot)
        if hasattr(self, 'btnRegisterSubmit'): self.btnRegisterSubmit.clicked.connect(self.register)
        if hasattr(self, 'btnSwitchLogin'): self.btnSwitchLogin.clicked.connect(lambda: self.stackAuth.setCurrentIndex(0))

    def _setup_icons(self):
        """Thêm icon vào các ô nhập liệu."""
        icon_map = {
            'inputUsername': '👤', 'inputPassword': '🔒',
            'inpRegName': '👤', 'inpRegPhone': '📞', 'inpRegEmail': '✉',
            'inpRegPass': '🔒', 'inpRegPassConfirm': '🔒',
        }
        for name, char in icon_map.items():
            widget = getattr(self, name, None)
            if widget and isinstance(widget, QLineEdit):
                widget.addAction(_make_icon(char, '#888888', 22), QLineEdit.ActionPosition.LeadingPosition)

    def _setup_placeholders(self):
        """Thêm placeholder text cho các ô nhập liệu đăng ký."""
        placeholders = {
            'inpRegName': 'Nhập họ và tên',
            'inpRegPhone': 'Nhập số điện thoại',
            'inpRegEmail': 'Nhập địa chỉ email',
            'inpRegPass': 'Nhập mật khẩu',
            'inpRegPassConfirm': 'Nhập lại mật khẩu',
        }
        for name, text in placeholders.items():
            widget = getattr(self, name, None)
            if widget and isinstance(widget, QLineEdit):
                widget.setPlaceholderText(text)

    # === Login ===
    def login(self):
        usr, pwd = self.inputUsername.text().strip(), self.inputPassword.text()
        ok, msg, user = self.auth_service.login(usr, pwd)
        if ok:
            QMessageBox.information(self, "Thành công", f"Chào {user.full_name}!")
        else:
            QMessageBox.warning(self, "Lỗi", msg)

    # === Register ===
    def register(self):
        name = self.inpRegName.text().strip()
        phone = self.inpRegPhone.text().strip()
        email = self.inpRegEmail.text().strip()
        pwd = self.inpRegPass.text()
        confirm = self.inpRegPassConfirm.text()

        if not (name and phone and email and pwd):
            return QMessageBox.warning(self, "Lỗi", "Nhập đủ thông tin")
        if pwd != confirm:
            return QMessageBox.warning(self, "Lỗi", "Mật khẩu không khớp")

        if self.auth_service.email_service and self.auth_service.email_service.is_configured():
            dlg = OTPDialog(email, self)
            self._worker = OTPWorker(self.auth_service.send_registration_otp, email)
            self._worker.finished.connect(dlg.on_otp_sent)
            self._worker.start()

            while True:
                res = dlg.exec()
                if res == QDialog.DialogCode.Accepted:
                    ok, msg = self.auth_service.verify_registration_otp(email, dlg.otp_code)
                    if ok:
                        ok2, msg2 = self.auth_service.register(name, phone, email, pwd, confirm)
                        if ok2:
                            QMessageBox.information(self, "OK", "Đăng ký thành công!")
                            self.stackAuth.setCurrentIndex(0)
                        else:
                            QMessageBox.warning(self, "Lỗi", msg2)
                        return
                    else:
                        QMessageBox.warning(self, "Lỗi", msg)
                elif res == 2:
                    dlg = OTPDialog(email, self)
                    self._worker = OTPWorker(self.auth_service.send_registration_otp, email)
                    self._worker.finished.connect(dlg.on_otp_sent)
                    self._worker.start()
                else:
                    return
        else:
            ok, msg = self.auth_service.register(name, phone, email, pwd, confirm)
            if ok:
                QMessageBox.information(self, "OK", msg)
                self.stackAuth.setCurrentIndex(0)
            else:
                QMessageBox.warning(self, "Lỗi", msg)

    # === Quên mật khẩu ===
    def forgot(self):
        if not self.auth_service.email_service or not self.auth_service.email_service.is_configured():
            return QMessageBox.warning(self, "Lỗi", "Chưa cấu hình mail, hãy báo Admin")

        try:
            dlg = ForgotPasswordDialog(self.auth_service, self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở dialog quên mật khẩu:\n{e}")


# =============================================
# ForgotPasswordDialog — Kế thừa Ui_DialogForgotPass
# File UI tự sinh: dialog_quen_mat_khau_ui.py (KHÔNG SỬA)
# =============================================
from ui.dialog_quen_mat_khau_ui import Ui_DialogForgotPass


class ForgotPasswordDialog(QDialog, Ui_DialogForgotPass):
    def __init__(self, auth_service, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self._worker = None

        # Setup UI từ file tự sinh
        self.setupUi(self)
        self.setStyleSheet(self.styleSheet())  # Force refresh CSS class selectors

        # Bắt đầu ở trang nhập email
        self.stackForgotPass.setCurrentIndex(0)

        # Kết nối signals
        self.btnSendOTP.clicked.connect(self._send_otp)
        self.btnVerifyOTP.clicked.connect(self._verify_otp)
        self.btnResetPass.clicked.connect(self._reset_password)

        # Nút quay lại đăng nhập = đóng dialog
        if hasattr(self, 'btnBackToLogin1'): self.btnBackToLogin1.clicked.connect(self.reject)
        if hasattr(self, 'btnBackToLogin2'): self.btnBackToLogin2.clicked.connect(self.reject)
        if hasattr(self, 'btnBackToLogin3'): self.btnBackToLogin3.clicked.connect(self.reject)
        if hasattr(self, 'btnGoToLogin'): self.btnGoToLogin.clicked.connect(self.accept)

    def _send_otp(self):
        """Bước 1: Gửi OTP đến email (chạy ngầm)."""
        email = self.inpForgotEmail.text().strip()
        if not email or '@' not in email:
            return QMessageBox.warning(self, "Lỗi", "Vui lòng nhập email hợp lệ")

        self.btnSendOTP.setEnabled(False)
        self.btnSendOTP.setText("Đang gửi...")

        self._worker = OTPWorker(self.auth_service.send_password_reset_otp, email)
        self._worker.finished.connect(self._on_otp_sent)
        self._worker.start()

    def _on_otp_sent(self, success: bool, message: str):
        """Callback khi OTP đã gửi xong."""
        self.btnSendOTP.setEnabled(True)
        self.btnSendOTP.setText("Tiếp tục")
        if success:
            self.stackForgotPass.setCurrentIndex(1)  # Chuyển sang trang OTP
        else:
            QMessageBox.warning(self, "Lỗi", message)

    def _verify_otp(self):
        """Bước 2: Xác nhận OTP."""
        otp = self.inpOTP.text().strip()
        if len(otp) != 6:
            return QMessageBox.warning(self, "Lỗi", "Nhập đủ 6 số")

        email = self.inpForgotEmail.text().strip()
        ok, msg = self.auth_service.email_service.verify_otp(email, otp)
        if ok:
            self.stackForgotPass.setCurrentIndex(2)  # Chuyển sang trang đổi mật khẩu
        else:
            QMessageBox.warning(self, "Lỗi", msg)

    def _reset_password(self):
        """Bước 3: Đặt mật khẩu mới."""
        pwd = self.inpNewPass.text()
        confirm = self.inpNewPassConfirm.text()
        if len(pwd) < 6:
            return QMessageBox.warning(self, "Lỗi", "Mật khẩu phải có ít nhất 6 ký tự")
        if pwd != confirm:
            return QMessageBox.warning(self, "Lỗi", "Mật khẩu không khớp")

        email = self.inpForgotEmail.text().strip()
        ok, msg = self.auth_service.reset_password(email, pwd)
        if ok:
            self.stackForgotPass.setCurrentIndex(3)  # Chuyển sang trang thành công
        else:
            QMessageBox.warning(self, "Lỗi", msg)
