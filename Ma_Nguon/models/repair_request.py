"""RepairRequest model — Yêu cầu sửa chữa. Storage: XML (repair_requests.xml)"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class RepairRequest:
    id: Optional[int] = None
    guest_id: int = 0           # FK -> Guest.id
    room_id: int = 0            # FK -> Room.id
    title: str = ""
    description: str = ""
    priority: str = "medium"    # REPAIR_PRIORITY
    status: str = "pending"     # REPAIR_STATUS
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        now = datetime.now().isoformat()
        return {
            'id': self.id, 'guest_id': self.guest_id, 'room_id': self.room_id,
            'title': self.title, 'description': self.description,
            'priority': self.priority, 'status': self.status,
            'created_at': self.created_at or now, 'updated_at': now,
            'completed_at': self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RepairRequest':
        return cls(
            id=data.get('id'), guest_id=data.get('guest_id', 0),
            room_id=data.get('room_id', 0), title=data.get('title', ''),
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'), status=data.get('status', 'pending'),
            created_at=data.get('created_at'), updated_at=data.get('updated_at'),
            completed_at=data.get('completed_at'),
        )
