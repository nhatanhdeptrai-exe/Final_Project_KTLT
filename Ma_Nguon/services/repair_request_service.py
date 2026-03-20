"""RepairRequestService — Quản lý yêu cầu sửa chữa."""
from typing import List, Optional, Tuple
from datetime import datetime
from models.repair_request import RepairRequest
from repositories.repair_request_repository import RepairRequestRepository


class RepairRequestService:
    def __init__(self, repair_repo: RepairRequestRepository):
        self.repair_repo = repair_repo

    def get_all(self) -> List[RepairRequest]:
        return self.repair_repo.get_all()

    def get_by_id(self, req_id: int) -> Optional[RepairRequest]:
        return self.repair_repo.get_by_id(req_id)

    def create_request(self, guest_id: int, room_id: int, title: str,
                       description: str, priority: str = 'medium') -> Tuple[bool, str]:
        req = RepairRequest(
            guest_id=guest_id, room_id=room_id, title=title,
            description=description, priority=priority, status='pending',
        )
        self.repair_repo.create(req)
        return True, "Gửi yêu cầu sửa chữa thành công"

    def update_status(self, req_id: int, status: str) -> Tuple[bool, str]:
        req = self.repair_repo.get_by_id(req_id)
        if not req: return False, "Không tìm thấy yêu cầu"
        req.status = status
        if status == 'completed':
            req.completed_at = datetime.now().isoformat()
        self.repair_repo.update(req)
        return True, f"Cập nhật trạng thái: {status}"

    def get_pending(self) -> List[RepairRequest]:
        return self.repair_repo.get_pending()

    def get_by_room(self, room_id: int) -> List[RepairRequest]:
        return self.repair_repo.get_by_room_id(room_id)
