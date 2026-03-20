"""User model."""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import bcrypt

@dataclass
class User:
    id: Optional[int] = None
    email: str = ""
    phone: str = ""
    password_hash: str = ""
    full_name: str = ""
    role: str = "guest"
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def set_password(self, password: str) -> None:
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        if not self.password_hash: return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self) -> dict:
        now = datetime.now().isoformat()
        return {
            'id': self.id, 'email': self.email, 'phone': self.phone,
            'password_hash': self.password_hash, 'full_name': self.full_name,
            'role': self.role, 'is_active': self.is_active,
            'created_at': self.created_at or now, 'updated_at': now,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        return cls(
            id=data.get('id'), email=data.get('email', ''), phone=data.get('phone', ''),
            password_hash=data.get('password_hash', ''), full_name=data.get('full_name', ''),
            role=data.get('role', 'guest'), is_active=data.get('is_active', True),
            created_at=data.get('created_at'), updated_at=data.get('updated_at')
        )
