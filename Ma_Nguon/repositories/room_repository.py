"""RoomRepository — CRUD phòng. Storage: JSON (rooms.json)"""
from typing import Optional, List
from config.constants import ROOMS_FILE
from handlers.json_handler import JSONHandler
from models.room import Room


class RoomRepository:
    def __init__(self):
        self.file_path = ROOMS_FILE
        self.list_key = 'rooms'

    def get_by_id(self, room_id: int) -> Optional[Room]:
        data = JSONHandler.find_by_id(self.file_path, room_id, self.list_key)
        return Room.from_dict(data) if data else None

    def get_all(self) -> List[Room]:
        return [Room.from_dict(d) for d in JSONHandler.get_all(self.file_path, self.list_key)]

    def create(self, room: Room) -> Room:
        d = room.to_dict()
        d.pop('id', None)
        saved = JSONHandler.add_item(self.file_path, d, self.list_key)
        return Room.from_dict(saved)

    def update(self, room: Room) -> bool:
        if not room.id: return False
        d = room.to_dict()
        d.pop('id', None)
        return JSONHandler.update_item(self.file_path, room.id, d, self.list_key)

    def delete(self, room_id: int) -> bool:
        return JSONHandler.delete_item(self.file_path, room_id, self.list_key)

    def get_available(self) -> List[Room]:
        return [r for r in self.get_all() if r.is_available()]

    def get_by_number(self, number: str) -> Optional[Room]:
        for r in self.get_all():
            if r.room_number == number: return r
        return None
