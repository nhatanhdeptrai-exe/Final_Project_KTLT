"""ApplicationService — Quản lý đơn đăng ký thuê phòng."""
from typing import List, Optional, Tuple
from models.application import Application
from repositories.application_repository import ApplicationRepository


class ApplicationService:
    def __init__(self, app_repo: ApplicationRepository):
        self.app_repo = app_repo

    def get_all(self) -> List[Application]:
        return self.app_repo.get_all()

    def get_by_id(self, app_id: int) -> Optional[Application]:
        return self.app_repo.get_by_id(app_id)

    def submit(self, guest_id: int, room_id: int, move_in_date: str,
               occupation: str = '', notes: str = '') -> Tuple[bool, str]:
        app = Application(
            guest_id=guest_id, room_id=room_id, status='completed',
            move_in_date=move_in_date, occupation=occupation, additional_notes=notes,
        )
        self.app_repo.create(app)
        return True, "Nộp đơn thành công"

    def cancel(self, app_id: int) -> Tuple[bool, str]:
        app = self.app_repo.get_by_id(app_id)
        if not app: return False, "Không tìm thấy đơn"
        app.status = 'cancelled'
        self.app_repo.update(app)
        return True, "Hủy đơn thành công"

    def get_by_guest(self, guest_id: int) -> List[Application]:
        return self.app_repo.get_by_guest_id(guest_id)
