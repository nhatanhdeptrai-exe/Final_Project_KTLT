"""Validators."""
import re
from typing import Tuple

def validate_email(email: str) -> Tuple[bool, str]:
    if not email or not email.strip(): return False, "Email không được để trống"
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email.strip()):
        return False, "Email không đúng định dạng"
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    if not phone or not phone.strip(): return False, "SĐT không được để trống"
    if not re.match(r'^0\d{9}$', phone.strip()): return False, "SĐT phải 10 chữ số, bắt đầu bằng 0"
    return True, ""

def validate_password(password: str) -> Tuple[bool, str]:
    if not password or len(password) < 6: return False, "Mật khẩu tối thiểu 6 ký tự"
    return True, ""

def validate_name(name: str) -> Tuple[bool, str]:
    if not name or len(name.strip()) < 2: return False, "Tên bắt buộc và tối thiểu 2 ký tự"
    return True, ""
