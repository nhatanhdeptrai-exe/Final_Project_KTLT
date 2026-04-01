"""InvoiceService — Quản lý hóa đơn (tạo hàng tháng, thanh toán)."""
from typing import List, Optional, Tuple, Dict
from datetime import date, datetime, timedelta
from models.invoice import Invoice
from repositories.invoice_repository import InvoiceRepository
from repositories.contract_repository import ContractRepository
from config.constants import DEFAULT_INVOICE_DUE_DAYS, SETTINGS_FILE
from handlers.json_handler import JSONHandler


class InvoiceService:
    def __init__(self, invoice_repo: InvoiceRepository, contract_repo: ContractRepository):
        self.invoice_repo = invoice_repo
        self.contract_repo = contract_repo

    def get_rates(self) -> Dict[str, int]:
        """Đọc đơn giá điện/nước từ file cấu hình (gọi 1 lần khi mở dialog)."""
        settings = JSONHandler.load(SETTINGS_FILE)
        return {
            'electricity_rate': settings.get('electricity_rate', 3500),
            'water_rate': settings.get('water_rate', 25000),
        }

    def calculate_costs(self, elec_old: int, elec_new: int,
                        water_old: int, water_new: int,
                        rent: int, other: int,
                        rates: Dict[str, int] = None) -> Dict[str, int]:
        """Tính tiền điện, nước, tổng cộng (logic nghiệp vụ thuần túy)."""
        if rates is None:
            rates = self.get_rates()
        elec_cost = max(0, elec_new - elec_old) * rates['electricity_rate']
        water_cost = max(0, water_new - water_old) * rates['water_rate']
        total = rent + elec_cost + water_cost + other
        return {
            'electricity_cost': elec_cost,
            'water_cost': water_cost,
            'total': total,
        }

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
