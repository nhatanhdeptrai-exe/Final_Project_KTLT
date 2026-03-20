"""GuestService — Quản lý khách thuê."""
from typing import List, Optional, Tuple
from models.guest import Guest
from repositories.guest_repository import GuestRepository


class GuestService:
    def __init__(self, guest_repo: GuestRepository):
        self.guest_repo = guest_repo

    def get_all_guests(self) -> List[Guest]:
        return self.guest_repo.get_all()

    def get_guest_by_id(self, guest_id: int) -> Optional[Guest]:
        return self.guest_repo.get_by_id(guest_id)

    def get_guest_by_user_id(self, user_id: int) -> Optional[Guest]:
        return self.guest_repo.get_by_user_id(user_id)

    def create_guest(self, guest: Guest) -> Tuple[bool, str]:
        saved = self.guest_repo.create(guest)
        if saved: return True, "Tạo hồ sơ khách thành công"
        return False, "Lỗi tạo hồ sơ"

    def update_guest(self, guest: Guest) -> Tuple[bool, str]:
        if self.guest_repo.update(guest): return True, "Cập nhật thành công"
        return False, "Lỗi cập nhật"

    def delete_guest(self, guest_id: int) -> bool:
        return self.guest_repo.delete(guest_id)
