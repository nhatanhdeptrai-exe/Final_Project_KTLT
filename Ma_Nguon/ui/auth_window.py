"""AuthWindow UI."""
import os
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QMessageBox, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QInputDialog
from PyQt6.QtCore import Qt
from PyQt6 import uic

class OTPDialog(QDialog):
    def __init__(self, email: str, parent=None):
        super().__init__(parent)
        self.email = email
        self.otp_code = ""
        self.setWindowTitle("Xác nhận OTP")
        self.setFixedSize(400, 250)
        self.setStyleSheet("""
            QDialog { background-color: #1a4a49; }
            QLabel { color: white; font-size: 14px; }
            QLineEdit { background-color: white; border-radius: 6px; padding: 12px; font-size: 24px; letter-spacing: 8px; text-align: center; }
            QPushButton#btnVerify { background-color: #0298a0; color: white; font-weight: bold; border-radius: 8px; padding: 12px; }
            QPushButton#btnResend { background-color: transparent; color: #a0aec0; text-decoration: underline; border: none; }
        """)
        layout = QVBoxLayout(self)
        
        lbl = QLabel(f"Nhập mã OTP vừa gửi đến\n{email}")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        
        self.inp = QLineEdit()
        self.inp.setMaxLength(6)
        self.inp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.inp)
        
        btn = QPushButton("Xác nhận OTP")
        btn.setObjectName("btnVerify")
        btn.clicked.connect(self.verify)
        layout.addWidget(btn)
        
        btn_re = QPushButton("Gửi lại mã")
        btn_re.setObjectName("btnResend")
        btn_re.clicked.connect(lambda: self.done(2))
        layout.addWidget(btn_re)

    def verify(self):
        self.otp_code = self.inp.text().strip()
        if len(self.otp_code) != 6:
            QMessageBox.warning(self, "Lỗi", "Nhập đủ 6 số")
            return
        self.accept()

class AuthWindow(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        ui_path = Path(__file__).parent.parent.parent / 'ui' / 'UI_Common' / 'auth_main.ui'
        if not ui_path.exists(): ui_path = Path(r'D:\Documents\Do_AN\ui\UI_Common\auth_main.ui')
        if not ui_path.exists(): 
            QMessageBox.critical(self, "Lỗi", f"Không tìm thấy file: {ui_path}")
            return
            
        uic.loadUi(str(ui_path), self)
        
        if hasattr(self, 'btnLoginsubmit'): self.btnLoginsubmit.clicked.connect(self.login)
        if hasattr(self, 'btnSwitchSignup'): self.btnSwitchSignup.clicked.connect(lambda: self.stackAuth.setCurrentIndex(1))
        if hasattr(self, 'btnForgotPassword'): self.btnForgotPassword.clicked.connect(self.forgot)
        if hasattr(self, 'btnRegisterSubmit'): self.btnRegisterSubmit.clicked.connect(self.register)
        if hasattr(self, 'btnSwitchLogin'): self.btnSwitchLogin.clicked.connect(lambda: self.stackAuth.setCurrentIndex(0))

    def login(self):
        usr, pwd = self.inputUsername.text().strip(), self.inputPassword.text()
        ok, msg, user = self.auth_service.login(usr, pwd)
        if ok:
            QMessageBox.information(self, "Thành công", f"Chào {user.full_name}!")
        else:
            QMessageBox.warning(self, "Lỗi", msg)

    def register(self):
        name, phone, email = self.inpRegName.text().strip(), self.inpRegPhone.text().strip(), self.inpRegEmail.text().strip()
        pwd, confirm = self.inpRegPass.text(), self.inpRegPassConfirm.text()
        
        if not (name and phone and email and pwd): return QMessageBox.warning(self, "Lỗi", "Nhập đủ thông tin")
        if pwd != confirm: return QMessageBox.warning(self, "Lỗi", "Mật khẩu không khớp")
        
        if self.auth_service.email_service.is_configured():
            ok, msg = self.auth_service.send_registration_otp(email)
            if not ok: return QMessageBox.warning(self, "Lỗi", msg)
            
            while True:
                dlg = OTPDialog(email, self)
                res = dlg.exec()
                if res == QDialog.DialogCode.Accepted:
                    ok, msg = self.auth_service.verify_registration_otp(email, dlg.otp_code)
                    if ok:
                        ok2, msg2 = self.auth_service.register(name, phone, email, pwd, confirm)
                        if ok2:
                            QMessageBox.information(self, "OK", "Đăng ký thành công!")
                            self.stackAuth.setCurrentIndex(0)
                        else: QMessageBox.warning(self, "Lỗi", msg2)
                        return
                    else: QMessageBox.warning(self, "Lỗi", msg)
                elif res == 2:
                    self.auth_service.send_registration_otp(email)
                else: return
        else:
            ok, msg = self.auth_service.register(name, phone, email, pwd, confirm)
            if ok:
                QMessageBox.information(self, "OK", msg)
                self.stackAuth.setCurrentIndex(0)
            else:
                QMessageBox.warning(self, "Lỗi", msg)

    def forgot(self):
        if not self.auth_service.email_service.is_configured():
            return QMessageBox.warning(self, "Lỗi", "Chưa cấu hình mail, hãy báo Admin")
        email, ok = QInputDialog.getText(self, "Quên mật khẩu", "Nhập email:")
        if not ok or not email: return
        
        ok, msg = self.auth_service.send_password_reset_otp(email)
        if not ok: return QMessageBox.warning(self, "Lỗi", msg)
        
        dlg = OTPDialog(email, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            ok, msg = self.auth_service.email_service.verify_otp(email, dlg.otp_code)
            if ok:
                pwd, ok2 = QInputDialog.getText(self, "MK Mới", "Nhập mật khẩu mới:", QLineEdit.EchoMode.Password)
                if ok2 and pwd:
                    ok3, msg3 = self.auth_service.reset_password(email, pwd)
                    QMessageBox.information(self, "Kết quả", msg3)
            else:
                QMessageBox.warning(self, "Lỗi", msg)
