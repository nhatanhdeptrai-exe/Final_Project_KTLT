"""InvoiceRepository — CRUD hóa đơn. Storage: XLSX (invoices.xlsx)"""
from typing import Optional, List
from config.constants import INVOICES_FILE
from handlers.excel_handler import ExcelHandler
from models.invoice import Invoice


class InvoiceRepository:
    def __init__(self):
        self.file_path = INVOICES_FILE

    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        data = ExcelHandler.find_by_id(self.file_path, invoice_id)
        return Invoice.from_dict(data) if data else None

    def get_all(self) -> List[Invoice]:
        return [Invoice.from_dict(d) for d in ExcelHandler.get_all(self.file_path)]

    def create(self, invoice: Invoice) -> Invoice:
        d = invoice.to_dict()
        d.pop('id', None)
        saved = ExcelHandler.add_item(self.file_path, d)
        return Invoice.from_dict(saved)

    def update(self, invoice: Invoice) -> bool:
        if not invoice.id: return False
        d = invoice.to_dict()
        d.pop('id', None)
        return ExcelHandler.update_item(self.file_path, invoice.id, d)

    def delete(self, invoice_id: int) -> bool:
        return ExcelHandler.delete_item(self.file_path, invoice_id)

    def get_by_contract_id(self, contract_id: int) -> List[Invoice]:
        return [inv for inv in self.get_all() if inv.contract_id == contract_id]

    def get_unpaid(self) -> List[Invoice]:
        return [inv for inv in self.get_all() if inv.status == 'unpaid']

    def get_overdue(self) -> List[Invoice]:
        return [inv for inv in self.get_all() if inv.is_overdue()]
