"""ContractRepository — CRUD hợp đồng. Storage: XML (contracts.xml)"""
from typing import Optional, List
from config.constants import CONTRACTS_FILE
from handlers.xml_handler import XMLHandler
from models.contract import Contract


class ContractRepository:
    def __init__(self):
        self.file_path = CONTRACTS_FILE
        self.root_tag = 'contracts'
        self.item_tag = 'contract'

    def get_by_id(self, contract_id: int) -> Optional[Contract]:
        data = XMLHandler.find_by_id(self.file_path, contract_id, self.root_tag)
        return Contract.from_dict(data) if data else None

    def get_all(self) -> List[Contract]:
        return [Contract.from_dict(d) for d in XMLHandler.get_all(self.file_path, self.root_tag)]

    def create(self, contract: Contract) -> Contract:
        d = contract.to_dict()
        d.pop('id', None)
        saved = XMLHandler.add_item(self.file_path, d, self.root_tag, self.item_tag)
        return Contract.from_dict(saved)

    def update(self, contract: Contract) -> bool:
        if not contract.id: return False
        d = contract.to_dict()
        d.pop('id', None)
        return XMLHandler.update_item(self.file_path, contract.id, d, self.root_tag)

    def delete(self, contract_id: int) -> bool:
        return XMLHandler.delete_item(self.file_path, contract_id, self.root_tag)

    def get_by_room_id(self, room_id: int) -> List[Contract]:
        return [c for c in self.get_all() if c.room_id == room_id]

    def get_active_by_room(self, room_id: int) -> Optional[Contract]:
        for c in self.get_by_room_id(room_id):
            if c.is_active(): return c
        return None

    def get_by_guest_id(self, guest_id: int) -> List[Contract]:
        return [c for c in self.get_all() if c.guest_id == guest_id]
