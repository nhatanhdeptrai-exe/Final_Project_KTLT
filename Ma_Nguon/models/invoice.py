"""Invoice model — Hóa đơn. Storage: XLSX (invoices.xlsx)"""
from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime

@dataclass
class Invoice:
    id: Optional[int] = None
    invoice_number: str = ""    # INV[YYYY][MM][NNN]
    contract_id: int = 0        # FK -> Contract.id
    month: int = 0
    year: int = 0
    room_rent: int = 0          # VND
    electricity_cost: int = 0   # VND
    water_cost: int = 0         # VND
    other_fees: int = 0         # VND
    total_amount: int = 0       # = room_rent + electricity + water + other
    status: str = "unpaid"      # INVOICE_STATUS
    due_date: Optional[str] = None
    payment_date: Optional[str] = None
    payment_method: Optional[str] = None
    created_at: Optional[str] = None

    def is_overdue(self) -> bool:
        if not self.due_date or self.status == 'paid': return False
        return date.fromisoformat(self.due_date) < date.today()

    def days_overdue(self) -> int:
        if not self.is_overdue(): return 0
        return (date.today() - date.fromisoformat(self.due_date)).days

    def calculate_total(self) -> int:
        self.total_amount = self.room_rent + self.electricity_cost + self.water_cost + self.other_fees
        return self.total_amount

    def to_dict(self) -> dict:
        now = datetime.now().isoformat()
        return {
            'id': self.id, 'invoice_number': self.invoice_number,
            'contract_id': self.contract_id, 'month': self.month, 'year': self.year,
            'room_rent': self.room_rent, 'electricity_cost': self.electricity_cost,
            'water_cost': self.water_cost, 'other_fees': self.other_fees,
            'total_amount': self.total_amount, 'status': self.status,
            'due_date': self.due_date, 'payment_date': self.payment_date,
            'payment_method': self.payment_method, 'created_at': self.created_at or now,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Invoice':
        return cls(
            id=data.get('id'), invoice_number=data.get('invoice_number', ''),
            contract_id=data.get('contract_id', 0), month=data.get('month', 0),
            year=data.get('year', 0), room_rent=data.get('room_rent', 0),
            electricity_cost=data.get('electricity_cost', 0),
            water_cost=data.get('water_cost', 0), other_fees=data.get('other_fees', 0),
            total_amount=data.get('total_amount', 0), status=data.get('status', 'unpaid'),
            due_date=data.get('due_date'), payment_date=data.get('payment_date'),
            payment_method=data.get('payment_method'), created_at=data.get('created_at'),
        )
