"""InvoiceService — Quản lý hóa đơn (tạo hàng tháng, thanh toán)."""
from typing import List, Optional, Tuple
from datetime import date, datetime, timedelta
from models.invoice import Invoice
from repositories.invoice_repository import InvoiceRepository
from repositories.contract_repository import ContractRepository
from config.constants import DEFAULT_INVOICE_DUE_DAYS


class InvoiceService:
    def __init__(self, invoice_repo: InvoiceRepository, contract_repo: ContractRepository):
        self.invoice_repo = invoice_repo
        self.contract_repo = contract_repo

    def get_all(self) -> List[Invoice]:
        return self.invoice_repo.get_all()

    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        return self.invoice_repo.get_by_id(invoice_id)

    def generate_monthly_invoices(self, month: int, year: int,
                                   electricity_data: dict = None,
                                   water_data: dict = None) -> List[Invoice]:
        """Tạo hóa đơn cho tất cả HĐ active. electricity_data/water_data = {room_id: cost}"""
        active_contracts = [c for c in self.contract_repo.get_all() if c.is_active()]
        invoices = []
        for i, contract in enumerate(active_contracts):
            number = f"INV{year}{month:02d}{i + 1:03d}"
            elec = (electricity_data or {}).get(contract.room_id, 0)
            water = (water_data or {}).get(contract.room_id, 0)
            due = (datetime.now() + timedelta(days=DEFAULT_INVOICE_DUE_DAYS)).strftime('%Y-%m-%d')

            inv = Invoice(
                invoice_number=number, contract_id=contract.id,
                month=month, year=year, room_rent=contract.monthly_rent,
                electricity_cost=elec, water_cost=water,
                total_amount=contract.monthly_rent + elec + water,
                status='unpaid', due_date=due,
            )
            saved = self.invoice_repo.create(inv)
            invoices.append(saved)
        return invoices

    def mark_paid(self, invoice_id: int, method: str = 'cash') -> Tuple[bool, str]:
        inv = self.invoice_repo.get_by_id(invoice_id)
        if not inv: return False, "Không tìm thấy hóa đơn"
        inv.status = 'paid'
        inv.payment_date = date.today().isoformat()
        inv.payment_method = method
        self.invoice_repo.update(inv)
        return True, "Thanh toán thành công"

    def get_unpaid(self) -> List[Invoice]:
        return self.invoice_repo.get_unpaid()

    def get_overdue(self) -> List[Invoice]:
        return self.invoice_repo.get_overdue()

    def get_by_contract(self, contract_id: int) -> List[Invoice]:
        return self.invoice_repo.get_by_contract_id(contract_id)
