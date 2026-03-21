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
    gender: str = ""           # "Nam" / "Nữ"
    dob: str = ""              # "dd/MM/yyyy" hoặc "yyyy-MM-dd"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        now = datetime.now().isoformat()
        return {
            'id': self.id, 'user_id': self.user_id, 'full_name': self.full_name,
            'phone': self.phone, 'email': self.email, 'id_card': self.id_card,
            'address': self.address, 'occupation': self.occupation,
            'gender': self.gender, 'dob': self.dob,
            'created_at': self.created_at or now, 'updated_at': now,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Guest':
        def _str(val):
            """Convert to str, treating None/NaN as empty."""
            if val is None:
                return ''
            s = str(val)
            return '' if s in ('nan', 'None', 'NaN') else s
        return cls(
            id=data.get('id'), user_id=data.get('user_id', 0),
            full_name=_str(data.get('full_name', '')), phone=_str(data.get('phone', '')),
            email=_str(data.get('email', '')), id_card=_str(data.get('id_card', '')),
            address=_str(data.get('address', '')), occupation=_str(data.get('occupation', '')),
            gender=_str(data.get('gender', '')), dob=_str(data.get('dob', '')),
            created_at=data.get('created_at'), updated_at=data.get('updated_at'),
        )

