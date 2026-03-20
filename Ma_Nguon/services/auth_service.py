"""AuthService - Xác thực người dùng."""
from typing import Optional, Tuple
from models.user import User
from repositories.user_repository import UserRepository
from services.email_service import EmailService
from utils.validators import validate_email, validate_phone, validate_password, validate_name

class AuthService:
    def __init__(self, user_repo: UserRepository, email_service: EmailService = None):
        self.user_repo = user_repo
        self.email_service = email_service
        self._current_user: Optional[User] = None

    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        if not username or not password: return False, "Nhập đủ thông tin", None
        user = self.user_repo.authenticate(username, password)
        if not user: return False, "Sai tài khoản/mật khẩu", None
        if not user.is_active: return False, "Tài khoản bị khóa", None
        self._current_user = user
        return True, "Đăng nhập thành công", user

    def register(self, name: str, phone: str, email: str, password: str, confirm: str) -> Tuple[bool, str]:
        if not validate_name(name)[0]: return False, validate_name(name)[1]
        if not validate_phone(phone)[0]: return False, validate_phone(phone)[1]
        if not validate_email(email)[0]: return False, validate_email(email)[1]
        if not validate_password(password)[0]: return False, validate_password(password)[1]
        if password != confirm: return False, "Mật khẩu không khớp"
        if self.user_repo.get_by_email(email): return False, "Email đã đăng ký"
        if self.user_repo.get_by_phone(phone): return False, "SĐT đã đăng ký"
        
        user = User(email=email.strip(), phone=phone.strip(), full_name=name.strip(), role='guest')
        user.set_password(password)
        if self.user_repo.create(user): return True, "Đăng ký thành công"
        return False, "Lỗi hệ thống"

    def send_registration_otp(self, email: str) -> Tuple[bool, str]:
        if not self.email_service: return False, "Chưa cấu hình mail"
        if self.user_repo.get_by_email(email): return False, "Email đã đăng ký"
        return self.email_service.send_otp(email)

    def verify_registration_otp(self, email: str, otp: str) -> Tuple[bool, str]:
        if not self.email_service: return False, "Chưa cấu hình mail"
        return self.email_service.verify_otp(email, otp)
        
    def send_password_reset_otp(self, email: str) -> Tuple[bool, str]:
        if not self.user_repo.get_by_email(email): return False, "Email chưa đăng ký"
        return self.email_service.send_otp(email)

    def reset_password(self, email: str, new_pass: str) -> Tuple[bool, str]:
        user = self.user_repo.get_by_email(email)
        if not user: return False, "Lỗi"
        if not validate_password(new_pass)[0]: return False, validate_password(new_pass)[1]
        user.set_password(new_pass)
        if self.user_repo.update(user): return True, "Đổi MK thành công"
        return False, "Lỗi"
