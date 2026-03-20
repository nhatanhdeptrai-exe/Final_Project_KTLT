"""Formatters — Định dạng hiển thị."""
from datetime import datetime


def format_currency(amount: int) -> str:
    """Ví dụ: 3500000 → '3.500.000 VNĐ'"""
    return f"{amount:,.0f} VNĐ".replace(",", ".")


def format_date(date_str: str) -> str:
    """ISO string → 'dd/mm/yyyy'."""
    if not date_str: return ""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime('%d/%m/%Y')
    except:
        return date_str


def format_datetime(dt_str: str) -> str:
    """ISO → 'dd/mm/yyyy HH:MM'."""
    if not dt_str: return ""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return dt_str


def format_phone(phone: str) -> str:
    """0987654321 → '0987.654.321'."""
    if len(phone) == 10:
        return f"{phone[:4]}.{phone[4:7]}.{phone[7:]}"
    return phone


def format_area(area: float) -> str:
    """25.5 → '25.5 m²'."""
    return f"{area} m²"
