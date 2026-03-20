"""Contract model — Hợp đồng thuê. Storage: XML (contracts.xml)"""
from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime

@dataclass
class Contract:
    id: Optional[int] = None
    contract_number: str = ""   # HD[YYYY][MM][NNN]
    room_id: int = 0            # FK -> Room.id
    guest_id: int = 0           # FK -> Guest.id
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    monthly_rent: int = 0       # VND
    deposit: int = 0            # VND
    status: str = "active"      # CONTRACT_STATUS
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def is_active(self) -> bool:
        return self.status == 'active'

    def is_expired(self) -> bool:
        if not self.end_date: return False
        return date.fromisoformat(self.end_date) < date.today()

    def days_until_expiry(self) -> int:
        if not self.end_date: return 0
        return (date.fromisoformat(self.end_date) - date.today()).days

    def to_dict(self) -> dict:
        now = datetime.now().isoformat()
        return {
            'id': self.id, 'contract_number': self.contract_number,
            'room_id': self.room_id, 'guest_id': self.guest_id,
            'start_date': self.start_date, 'end_date': self.end_date,
            'monthly_rent': self.monthly_rent, 'deposit': self.deposit,
            'status': self.status,
            'created_at': self.created_at or now, 'updated_at': now,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Contract':
        return cls(
            id=data.get('id'), contract_number=data.get('contract_number', ''),
            room_id=data.get('room_id', 0), guest_id=data.get('guest_id', 0),
            start_date=data.get('start_date'), end_date=data.get('end_date'),
            monthly_rent=data.get('monthly_rent', 0), deposit=data.get('deposit', 0),
            status=data.get('status', 'active'),
            created_at=data.get('created_at'), updated_at=data.get('updated_at'),
        )
