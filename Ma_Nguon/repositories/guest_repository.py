"""GuestRepository — CRUD khách thuê. Storage: XLSX (guests.xlsx)"""
from typing import Optional, List
from config.constants import GUESTS_FILE
from handlers.excel_handler import ExcelHandler
from models.guest import Guest


class GuestRepository:
    def __init__(self):
        self.file_path = GUESTS_FILE

    def get_by_id(self, guest_id: int) -> Optional[Guest]:
        data = ExcelHandler.find_by_id(self.file_path, guest_id)
        return Guest.from_dict(data) if data else None

    def get_all(self) -> List[Guest]:
        return [Guest.from_dict(d) for d in ExcelHandler.get_all(self.file_path)]

    def create(self, guest: Guest) -> Guest:
        d = guest.to_dict()
        d.pop('id', None)
        saved = ExcelHandler.add_item(self.file_path, d)
        return Guest.from_dict(saved)

    def update(self, guest: Guest) -> bool:
        if not guest.id: return False
        d = guest.to_dict()
        d.pop('id', None)
        return ExcelHandler.update_item(self.file_path, guest.id, d)

    def delete(self, guest_id: int) -> bool:
        return ExcelHandler.delete_item(self.file_path, guest_id)

    def get_by_user_id(self, user_id: int) -> Optional[Guest]:
        for d in ExcelHandler.get_all(self.file_path):
            if d.get('user_id') == user_id: return Guest.from_dict(d)
        return None
