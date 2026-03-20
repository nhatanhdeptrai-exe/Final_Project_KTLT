"""Room model — Phòng trọ. Storage: JSON (rooms.json)"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class Room:
    id: Optional[int] = None
    room_number: str = ""
    floor: int = 1
    area: float = 0.0         # m²
    price: int = 0             # VND/tháng
    deposit: int = 0           # VND
    status: str = "available"  # ROOM_STATUS
    description: str = ""
    amenities: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def is_available(self) -> bool:
        return self.status == 'available'

    def to_dict(self) -> dict:
        now = datetime.now().isoformat()
        return {
            'id': self.id, 'room_number': self.room_number, 'floor': self.floor,
            'area': self.area, 'price': self.price, 'deposit': self.deposit,
            'status': self.status, 'description': self.description,
            'amenities': self.amenities, 'images': self.images,
            'created_at': self.created_at or now, 'updated_at': now,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Room':
        return cls(
            id=data.get('id'), room_number=data.get('room_number', ''),
            floor=data.get('floor', 1), area=data.get('area', 0.0),
            price=data.get('price', 0), deposit=data.get('deposit', 0),
            status=data.get('status', 'available'), description=data.get('description', ''),
            amenities=data.get('amenities', []), images=data.get('images', []),
            created_at=data.get('created_at'), updated_at=data.get('updated_at'),
        )
