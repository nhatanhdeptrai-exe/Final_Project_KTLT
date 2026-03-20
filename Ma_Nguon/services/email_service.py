"""EmailService - Gửi OTP qua email."""
import random, smtplib, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Tuple

# Lấy cấu hình email từ Backend (settings.py)
from config import settings

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = settings.EMAIL_SENDER
        self.sender_password = settings.EMAIL_PASSWORD
        self._otp_store: Dict[str, Dict] = {}
        self.otp_expiry_seconds = 300

    def generate_otp(self) -> str:
        return str(random.randint(100000, 999999))

    def send_otp(self, recipient_email: str) -> Tuple[bool, str]:
        # Kiểm tra config
        if not self.sender_email or not self.sender_password:
            return False, "Chưa cấu hình tài khoản gửi OTP trong config/settings.py"
            
        otp_code = self.generate_otp()
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = "Mã OTP - Hệ Thống Quản Lý Phòng Trọ"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #0298a0;">Xác nhận tài khoản</h2>
                <p>Mã OTP của bạn là:</p>
                <h1 style="color: #1a4a49; font-size: 36px; letter-spacing: 8px; background: #f0f0f0; padding: 15px 25px; display: inline-block; border-radius: 8px;">{otp_code}</h1>
                <p>Mã này có hiệu lực trong 5 phút.</p>
            </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            self._otp_store[recipient_email.lower()] = {
                'code': otp_code,
                'expires': time.time() + self.otp_expiry_seconds
            }
            return True, "Đã gửi mã OTP đến email"
        except Exception as e:
            return False, f"Lỗi gửi email: {str(e)}"

    def verify_otp(self, email: str, otp_code: str) -> Tuple[bool, str]:
        email = email.lower()
        if email not in self._otp_store: return False, "Chưa gửi mã OTP"
        stored = self._otp_store[email]
        if time.time() > stored['expires']:
            del self._otp_store[email]
            return False, "Mã OTP đã hết hạn"
        if stored['code'] != otp_code: return False, "Mã OTP không đúng"
        del self._otp_store[email]
        return True, "Xác nhận OTP thành công"

    def is_configured(self) -> bool:
        return bool(self.sender_email and self.sender_password)
