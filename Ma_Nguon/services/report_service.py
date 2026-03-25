"""ReportService — Báo cáo doanh thu, thống kê (sử dụng Numpy)."""
from typing import Dict, List
from datetime import datetime
import numpy as np
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

    def revenue_statistics(self, num_months: int = 6) -> Dict:
        """Thống kê doanh thu N tháng gần nhất sử dụng Numpy."""
        now = datetime.now()
        monthly_totals = []
        for i in range(num_months):
            m = now.month - i
            y = now.year
            while m <= 0:
                m += 12; y -= 1
            data = self.revenue_by_month(m, y)
            monthly_totals.append(data['total_revenue'])

        arr = np.array(monthly_totals, dtype=np.float64)
        return {
            'values': arr,
            'mean': float(np.mean(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'median': float(np.median(arr)),
            'total': float(np.sum(arr)),
        }

    def monthly_revenue_array(self, num_months: int = 6) -> Dict:
        """Trả về numpy arrays cho tiền phòng và điện nước N tháng."""
        now = datetime.now()
        labels, rent_list, utility_list = [], [], []
        for i in range(num_months - 1, -1, -1):
            m = now.month - i
            y = now.year
            while m <= 0:
                m += 12; y -= 1
            invoices = [inv for inv in self.invoice_repo.get_all()
                        if int(inv.month) == m and int(inv.year) == y and inv.status == 'paid']
            rent_list.append(sum(int(inv.room_rent or 0) for inv in invoices))
            utility_list.append(sum(int(inv.electricity_cost or 0) + int(inv.water_cost or 0) for inv in invoices))
            labels.append(f'Tháng {m}')
        return {
            'labels': labels,
            'rent': np.array(rent_list, dtype=np.float64) / 1_000_000,
            'utility': np.array(utility_list, dtype=np.float64) / 1_000_000,
        }

    def room_status_distribution(self) -> Dict:
        """Phân bố trạng thái phòng — dùng cho biểu đồ tròn."""
        rooms = self.room_repo.get_all()
        counts = np.array([
            len([r for r in rooms if r.status == 'available']),
            len([r for r in rooms if r.status == 'occupied']),
            len([r for r in rooms if r.status == 'maintenance']),
        ])
        return {
            'labels': ['Trống', 'Đang thuê', 'Bảo trì'],
            'counts': counts,
            'colors': ['#38a169', '#3182ce', '#e53e3e'],
        }

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
