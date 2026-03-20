"""RoomService — Quản lý phòng (CRUD, tìm kiếm, thống kê)."""
from typing import List, Optional, Tuple
from models.room import Room
from repositories.room_repository import RoomRepository


class RoomService:
    def __init__(self, room_repo: RoomRepository):
        self.room_repo = room_repo

    def get_all_rooms(self) -> List[Room]:
        return self.room_repo.get_all()

    def get_available_rooms(self) -> List[Room]:
        return self.room_repo.get_available()

    def get_room_by_id(self, room_id: int) -> Optional[Room]:
        return self.room_repo.get_by_id(room_id)

    def create_room(self, room_number: str, floor: int, area: float, price: int,
                    deposit: int, description: str = '', amenities: list = None) -> Tuple[bool, str]:
        if self.room_repo.get_by_number(room_number):
            return False, f"Phòng {room_number} đã tồn tại"
        room = Room(room_number=room_number, floor=floor, area=area, price=price,
                    deposit=deposit, description=description, amenities=amenities or [])
        self.room_repo.create(room)
        return True, "Tạo phòng thành công"

    def update_room(self, room: Room) -> Tuple[bool, str]:
        if self.room_repo.update(room): return True, "Cập nhật thành công"
        return False, "Lỗi cập nhật"

    def delete_room(self, room_id: int) -> Tuple[bool, str]:
        if self.room_repo.delete(room_id): return True, "Xóa phòng thành công"
        return False, "Không tìm thấy phòng"

    def set_status(self, room_id: int, status: str) -> bool:
        room = self.room_repo.get_by_id(room_id)
        if not room: return False
        room.status = status
        return self.room_repo.update(room)

    def get_statistics(self) -> dict:
        rooms = self.get_all_rooms()
        return {
            'total': len(rooms),
            'available': len([r for r in rooms if r.status == 'available']),
            'occupied': len([r for r in rooms if r.status == 'occupied']),
            'maintenance': len([r for r in rooms if r.status == 'maintenance']),
        }
