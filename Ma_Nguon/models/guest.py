"""Guest model — Khách thuê. Storage: XLSX (guests.xlsx)"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Guest:
    id: Optional[int] = None
    user_id: int = 0           # FK -> User.id
    full_name: str = ""
    phone: str = ""
    email: str = ""
    id_card: str = ""
    address: str = ""
    occupation: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        now = datetime.now().isoformat()
        return {
            'id': self.id, 'user_id': self.user_id, 'full_name': self.full_name,
            'phone': self.phone, 'email': self.email, 'id_card': self.id_card,
            'address': self.address, 'occupation': self.occupation,
            'created_at': self.created_at or now, 'updated_at': now,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Guest':
        return cls(
            id=data.get('id'), user_id=data.get('user_id', 0),
            full_name=str(data.get('full_name', '')), phone=str(data.get('phone', '')),
            email=str(data.get('email', '')), id_card=str(data.get('id_card', '')),
            address=str(data.get('address', '')), occupation=str(data.get('occupation', '')),
            created_at=data.get('created_at'), updated_at=data.get('updated_at'),
        )
