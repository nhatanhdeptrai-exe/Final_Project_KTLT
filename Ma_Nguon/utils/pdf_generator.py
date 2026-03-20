"""PDFGenerator — Xuất PDF hợp đồng/hóa đơn."""
import os
from config.constants import EXPORTS_DIR, TEMPLATES_DIR


class PDFGenerator:
    """Tạo PDF từ HTML template dùng reportlab/xhtml2pdf."""

    @staticmethod
    def export_contract_pdf(contract_data: dict, output_name: str = None) -> str:
        """
        Tạo PDF hợp đồng.
        contract_data: dict chứa thông tin hợp đồng + phòng + khách
        Trả về đường dẫn file PDF đã tạo.
        """
        os.makedirs(str(EXPORTS_DIR), exist_ok=True)
        filename = output_name or f"{contract_data.get('contract_number', 'contract')}.pdf"
        output_path = os.path.join(str(EXPORTS_DIR), filename)

        # Đọc template HTML
        template_path = os.path.join(str(TEMPLATES_DIR), 'contract_template.html')
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                html = f.read()
            # Thay thế placeholders
            for key, value in contract_data.items():
                html = html.replace(f'{{{{{key}}}}}', str(value))
        else:
            html = f"<h1>Hợp đồng {contract_data.get('contract_number', '')}</h1>"

        # Ghi PDF dùng xhtml2pdf
        try:
            from xhtml2pdf import pisa
            with open(output_path, 'wb') as f:
                pisa.CreatePDF(html.encode('utf-8'), dest=f, encoding='utf-8')
        except ImportError:
            # Fallback: ghi HTML thay vì PDF
            output_path = output_path.replace('.pdf', '.html')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

        return output_path

    @staticmethod
    def export_invoice_pdf(invoice_data: dict) -> str:
        """Tạo PDF hóa đơn. Tương tự contract."""
        os.makedirs(str(EXPORTS_DIR), exist_ok=True)
        filename = f"{invoice_data.get('invoice_number', 'invoice')}.pdf"
        output_path = os.path.join(str(EXPORTS_DIR), filename)

        html = f"""
        <html><head><meta charset='utf-8'></head>
        <body style='font-family: Arial;'>
        <h1>Hóa đơn {invoice_data.get('invoice_number', '')}</h1>
        <p>Tháng {invoice_data.get('month')}/{invoice_data.get('year')}</p>
        <table border='1' cellpadding='8'>
            <tr><td>Tiền phòng</td><td>{invoice_data.get('room_rent', 0):,} VNĐ</td></tr>
            <tr><td>Tiền điện</td><td>{invoice_data.get('electricity_cost', 0):,} VNĐ</td></tr>
            <tr><td>Tiền nước</td><td>{invoice_data.get('water_cost', 0):,} VNĐ</td></tr>
            <tr><td><b>Tổng</b></td><td><b>{invoice_data.get('total_amount', 0):,} VNĐ</b></td></tr>
        </table>
        </body></html>
        """
        try:
            from xhtml2pdf import pisa
            with open(output_path, 'wb') as f:
                pisa.CreatePDF(html.encode('utf-8'), dest=f, encoding='utf-8')
        except ImportError:
            output_path = output_path.replace('.pdf', '.html')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

        return output_path
