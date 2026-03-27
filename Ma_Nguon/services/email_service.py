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

    def send_invoice_email(self, recipient_email: str, invoice_data: dict) -> Tuple[bool, str]:
        """Gửi hóa đơn qua email sau khi thanh toán thành công."""
        if not self.sender_email or not self.sender_password:
            return False, "Chưa cấu hình tài khoản gửi email"

        inv = invoice_data
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Hóa đơn tháng {inv.get('month', '')}/{inv.get('year', '')} — Phòng {inv.get('room_number', '')}"

            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f7fafc;">
                <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; border: 1px solid #e2e8f0;">
                    <h2 style="color: #1a4a49; text-align: center; margin-bottom: 5px;">HÓA ĐƠN THANH TOÁN</h2>
                    <p style="color: #718096; text-align: center; font-size: 14px;">Tháng {inv.get('month', '')}/{inv.get('year', '')} — Phòng {inv.get('room_number', '')}</p>
                    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">

                    <p style="color: #2d3748;"><strong>Khách thuê:</strong> {inv.get('guest_name', '')}</p>
                    <p style="color: #2d3748;"><strong>Mã hóa đơn:</strong> {inv.get('invoice_number', '')}</p>
                    <p style="color: #2d3748;"><strong>Ngày thanh toán:</strong> {inv.get('payment_date', '')}</p>

                    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                    <h3 style="color: #1a4a49;">Chi tiết hóa đơn</h3>

                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <tr style="background-color: #f7fafc;">
                            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">Tiền nhà</td>
                            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: bold;">{inv.get('room_rent', 0):,.0f} VNĐ</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">Tiền điện</td>
                            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: bold;">{inv.get('electricity_cost', 0):,.0f} VNĐ</td>
                        </tr>
                        <tr style="background-color: #f7fafc;">
                            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">Tiền nước</td>
                            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: bold;">{inv.get('water_cost', 0):,.0f} VNĐ</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">Phí dịch vụ khác</td>
                            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: bold;">{inv.get('other_fees', 0):,.0f} VNĐ</td>
                        </tr>
                        <tr style="background-color: #e6fffa;">
                            <td style="padding: 12px; font-weight: bold; font-size: 16px; color: #1a4a49;">TỔNG CỘNG</td>
                            <td style="padding: 12px; text-align: right; font-weight: bold; font-size: 16px; color: #0298a0;">{inv.get('total_amount', 0):,.0f} VNĐ</td>
                        </tr>
                    </table>

                    <div style="margin-top: 25px; padding: 15px; background-color: #c6f6d5; border-radius: 8px; text-align: center;">
                        <span style="color: #276749; font-weight: bold; font-size: 15px;">✅ ĐÃ THANH TOÁN</span>
                    </div>

                    <p style="color: #a0aec0; font-size: 12px; text-align: center; margin-top: 20px;">
                        Hệ Thống Quản Lý Phòng Trọ — Email tự động, vui lòng không trả lời.
                    </p>
                </div>
            </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html', 'utf-8'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            return True, "Đã gửi hóa đơn qua email"
        except Exception as e:
            return False, f"Lỗi gửi email hóa đơn: {str(e)}"

    def is_configured(self) -> bool:
        return bool(self.sender_email and self.sender_password)
