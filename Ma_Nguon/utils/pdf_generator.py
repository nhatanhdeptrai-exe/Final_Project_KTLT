"""PDFGenerator — Xuất PDF hợp đồng/hóa đơn dùng Edge headless."""
import os
import subprocess
import tempfile
from config.constants import EXPORTS_DIR, TEMPLATES_DIR

BROWSER_PATHS = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]


def _find_browser():
    """Tìm Chrome hoặc Edge trên máy."""
    for path in BROWSER_PATHS:
        if os.path.exists(path):
            return path
    return None


class PDFGenerator:
    """Tạo PDF từ HTML template dùng Edge headless (font tiếng Việt đẹp)."""

    @staticmethod
    def _build_contract_html(contract_data: dict) -> str:
        """Load HTML template và thay placeholder."""
        template_path = os.path.join(str(TEMPLATES_DIR), 'contract_template.html')
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                html = f.read()
            for key, value in contract_data.items():
                html = html.replace(f'{{{{{key}}}}}', str(value))
            return html
        return f"<h1>Hợp đồng {contract_data.get('contract_number', '')}</h1>"

    @staticmethod
    def _html_to_pdf(html: str, output_path: str) -> str:
        """Convert HTML thành PDF dùng Chrome/Edge headless."""
        browser = _find_browser()
        if not browser:
            raise FileNotFoundError("Không tìm thấy Chrome hoặc Edge trên máy.")

        # Lưu HTML tạm
        tmp_html = tempfile.NamedTemporaryFile(
            suffix='.html', delete=False, mode='w', encoding='utf-8'
        )
        tmp_html.write(html)
        tmp_html.close()

        try:
            cmd = [
                browser,
                '--headless',
                '--disable-gpu',
                f'--print-to-pdf={output_path}',
                '--no-pdf-header-footer',
                tmp_html.name
            ]
            subprocess.run(cmd, capture_output=True, timeout=30)
        finally:
            try:
                os.unlink(tmp_html.name)
            except Exception:
                pass

        return output_path

    @staticmethod
    def export_contract_pdf(contract_data: dict, output_path: str) -> str:
        """Tạo PDF hợp đồng và lưu vào output_path."""
        html = PDFGenerator._build_contract_html(contract_data)
        return PDFGenerator._html_to_pdf(html, output_path)

    @staticmethod
    def export_invoice_pdf(invoice_data: dict, output_path: str = None) -> str:
        """Tạo PDF hóa đơn."""
        if not output_path:
            os.makedirs(str(EXPORTS_DIR), exist_ok=True)
            filename = f"{invoice_data.get('invoice_number', 'invoice')}.pdf"
            output_path = os.path.join(str(EXPORTS_DIR), filename)

        html = f"""
        <!DOCTYPE html>
        <html><head><meta charset='utf-8'>
        <style>* {{ font-family: Arial, sans-serif; }}</style>
        </head>
        <body style='margin:40px;'>
        <h1>Hóa đơn {invoice_data.get('invoice_number', '')}</h1>
        <p>Tháng {invoice_data.get('month')}/{invoice_data.get('year')}</p>
        <table border='1' cellpadding='8' style='border-collapse:collapse;'>
            <tr><td>Tiền phòng</td><td>{invoice_data.get('room_rent', 0):,} VNĐ</td></tr>
            <tr><td>Tiền điện</td><td>{invoice_data.get('electricity_cost', 0):,} VNĐ</td></tr>
            <tr><td>Tiền nước</td><td>{invoice_data.get('water_cost', 0):,} VNĐ</td></tr>
            <tr><td><b>Tổng</b></td><td><b>{invoice_data.get('total_amount', 0):,} VNĐ</b></td></tr>
        </table>
        </body></html>
        """
        return PDFGenerator._html_to_pdf(html, output_path)
