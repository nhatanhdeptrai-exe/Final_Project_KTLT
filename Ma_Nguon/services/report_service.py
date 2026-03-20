"""ReportService — Báo cáo doanh thu, thống kê."""
from typing import Dict, List
from repositories.invoice_repository import InvoiceRepository
from repositories.room_repository import RoomRepository
from repositories.contract_repository import ContractRepository
from repositories.guest_repository import GuestRepository


class ReportService:
    def __init__(self, invoice_repo: InvoiceRepository, room_repo: RoomRepository,
                 contract_repo: ContractRepository, guest_repo: GuestRepository):
        self.invoice_repo = invoice_repo
        self.room_repo = room_repo
        self.contract_repo = contract_repo
        self.guest_repo = guest_repo

    def revenue_by_month(self, month: int, year: int) -> Dict:
        invoices = [i for i in self.invoice_repo.get_all()
                    if i.month == month and i.year == year and i.status == 'paid']
        total = sum(i.total_amount for i in invoices)
        return {'month': month, 'year': year, 'total_revenue': total, 'invoice_count': len(invoices)}

    def occupancy_rate(self) -> Dict:
        rooms = self.room_repo.get_all()
        total = len(rooms)
        occupied = len([r for r in rooms if r.status == 'occupied'])
        rate = (occupied / total * 100) if total > 0 else 0
        return {'total': total, 'occupied': occupied, 'rate': round(rate, 1)}

    def dashboard_summary(self) -> Dict:
        rooms = self.room_repo.get_all()
        contracts = self.contract_repo.get_all()
        guests = self.guest_repo.get_all()
        unpaid = self.invoice_repo.get_unpaid()
        return {
            'total_rooms': len(rooms),
            'available_rooms': len([r for r in rooms if r.status == 'available']),
            'occupied_rooms': len([r for r in rooms if r.status == 'occupied']),
            'active_contracts': len([c for c in contracts if c.is_active()]),
            'total_guests': len(guests),
            'unpaid_invoices': len(unpaid),
            'total_unpaid': sum(i.total_amount for i in unpaid),
        }
