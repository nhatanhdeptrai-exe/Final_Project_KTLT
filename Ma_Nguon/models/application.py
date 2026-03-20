"""Application model — Đơn đăng ký thuê phòng. Storage: XML (rental_applications.xml)"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Application:
    id: Optional[int] = None
    guest_id: int = 0           # FK -> Guest.id
    room_id: int = 0            # FK -> Room.id
    contract_id: Optional[int] = None  # FK -> Contract.id (auto-created)
    status: str = "completed"   # APPLICATION_STATUS
    move_in_date: Optional[str] = None
    occupation: str = ""
    additional_notes: str = ""
    created_at: Optional[str] = None

    def to_dict(self) -> dict:
        now = datetime.now().isoformat()
        return {
            'id': self.id, 'guest_id': self.guest_id, 'room_id': self.room_id,
            'contract_id': self.contract_id, 'status': self.status,
            'move_in_date': self.move_in_date, 'occupation': self.occupation,
            'additional_notes': self.additional_notes,
            'created_at': self.created_at or now,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Application':
        return cls(
            id=data.get('id'), guest_id=data.get('guest_id', 0),
            room_id=data.get('room_id', 0), contract_id=data.get('contract_id'),
            status=data.get('status', 'completed'),
            move_in_date=data.get('move_in_date'), occupation=data.get('occupation', ''),
            additional_notes=data.get('additional_notes', ''),
            created_at=data.get('created_at'),
        )
