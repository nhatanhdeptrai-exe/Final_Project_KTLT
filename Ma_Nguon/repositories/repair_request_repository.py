"""RepairRequestRepository — CRUD yêu cầu sửa chữa. Storage: XML (repair_requests.xml)"""
from typing import Optional, List
from config.constants import REPAIRS_FILE
from handlers.xml_handler import XMLHandler
from models.repair_request import RepairRequest


class RepairRequestRepository:
    def __init__(self):
        self.file_path = REPAIRS_FILE
        self.root_tag = 'repair_requests'
        self.item_tag = 'repair_request'

    def get_by_id(self, req_id: int) -> Optional[RepairRequest]:
        data = XMLHandler.find_by_id(self.file_path, req_id, self.root_tag)
        return RepairRequest.from_dict(data) if data else None

    def get_all(self) -> List[RepairRequest]:
        return [RepairRequest.from_dict(d) for d in XMLHandler.get_all(self.file_path, self.root_tag)]

    def create(self, req: RepairRequest) -> RepairRequest:
        d = req.to_dict()
        d.pop('id', None)
        saved = XMLHandler.add_item(self.file_path, d, self.root_tag, self.item_tag)
        return RepairRequest.from_dict(saved)

    def update(self, req: RepairRequest) -> bool:
        if not req.id: return False
        d = req.to_dict()
        d.pop('id', None)
        return XMLHandler.update_item(self.file_path, req.id, d, self.root_tag)

    def delete(self, req_id: int) -> bool:
        return XMLHandler.delete_item(self.file_path, req_id, self.root_tag)

    def get_by_room_id(self, room_id: int) -> List[RepairRequest]:
        return [r for r in self.get_all() if r.room_id == room_id]

    def get_pending(self) -> List[RepairRequest]:
        return [r for r in self.get_all() if r.status == 'pending']
