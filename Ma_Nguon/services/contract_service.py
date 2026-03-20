"""ContractService — Quản lý hợp đồng (tạo, terminate, export PDF)."""
from typing import List, Optional, Tuple
from datetime import date, datetime
from models.contract import Contract
from repositories.contract_repository import ContractRepository
from repositories.room_repository import RoomRepository
from repositories.guest_repository import GuestRepository


class ContractService:
    def __init__(self, contract_repo: ContractRepository, room_repo: RoomRepository, guest_repo: GuestRepository):
        self.contract_repo = contract_repo
        self.room_repo = room_repo
        self.guest_repo = guest_repo

    def get_all(self) -> List[Contract]:
        return self.contract_repo.get_all()

    def get_by_id(self, contract_id: int) -> Optional[Contract]:
        return self.contract_repo.get_by_id(contract_id)

    def create_contract(self, room_id: int, guest_id: int, start_date: str,
                        end_date: str, monthly_rent: int, deposit: int) -> Tuple[bool, str]:
        room = self.room_repo.get_by_id(room_id)
        if not room: return False, "Phòng không tồn tại"
        if not room.is_available(): return False, "Phòng đã có người thuê"
        guest = self.guest_repo.get_by_id(guest_id)
        if not guest: return False, "Khách không tồn tại"

        now = datetime.now()
        number = f"HD{now.strftime('%Y%m')}{len(self.get_all()) + 1:03d}"
        contract = Contract(
            contract_number=number, room_id=room_id, guest_id=guest_id,
            start_date=start_date, end_date=end_date,
            monthly_rent=monthly_rent, deposit=deposit, status='active'
        )
        self.contract_repo.create(contract)
        room.status = 'occupied'
        self.room_repo.update(room)
        return True, f"Tạo hợp đồng {number} thành công"

    def terminate_contract(self, contract_id: int) -> Tuple[bool, str]:
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract: return False, "Không tìm thấy hợp đồng"
        contract.status = 'terminated'
        self.contract_repo.update(contract)
        room = self.room_repo.get_by_id(contract.room_id)
        if room:
            room.status = 'available'
            self.room_repo.update(room)
        return True, "Kết thúc hợp đồng thành công"

    def get_active_contracts(self) -> List[Contract]:
        return [c for c in self.get_all() if c.is_active()]

    def get_expiring_soon(self, days: int = 30) -> List[Contract]:
        return [c for c in self.get_active_contracts() if 0 < c.days_until_expiry() <= days]
