"""Constants & Enums — Hằng số toàn cục."""
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

# === File Paths ===
JSON_DIR = DATA_DIR / 'json'
USERS_FILE = str(JSON_DIR / 'users.json')
ROOMS_FILE = str(JSON_DIR / 'rooms.json')
SETTINGS_FILE = str(JSON_DIR / 'system_settings.json')

XML_DIR = DATA_DIR / 'xml'
CONTRACTS_FILE = str(XML_DIR / 'contracts.xml')
APPLICATIONS_FILE = str(XML_DIR / 'rental_applications.xml')
REPAIRS_FILE = str(XML_DIR / 'repair_requests.xml')

EXCEL_DIR = DATA_DIR / 'excel'
GUESTS_FILE = str(EXCEL_DIR / 'guests.xlsx')
INVOICES_FILE = str(EXCEL_DIR / 'invoices.xlsx')

BACKUPS_DIR = DATA_DIR / 'backups'
EXPORTS_DIR = DATA_DIR / 'exports'
TEMPLATES_DIR = DATA_DIR / 'templates'

# === Status Constants ===
ROOM_STATUS = {'AVAILABLE': 'available', 'OCCUPIED': 'occupied', 'MAINTENANCE': 'maintenance'}
CONTRACT_STATUS = {'ACTIVE': 'active', 'EXPIRED': 'expired', 'TERMINATED': 'terminated'}
INVOICE_STATUS = {'UNPAID': 'unpaid', 'PAID': 'paid', 'OVERDUE': 'overdue'}
APPLICATION_STATUS = {'COMPLETED': 'completed', 'CANCELLED': 'cancelled'}
REPAIR_STATUS = {'PENDING': 'pending', 'IN_PROGRESS': 'in_progress', 'COMPLETED': 'completed'}
REPAIR_PRIORITY = {'LOW': 'low', 'MEDIUM': 'medium', 'HIGH': 'high', 'URGENT': 'urgent'}
USER_ROLES = {'ADMIN': 'admin', 'GUEST': 'guest'}

# === System Defaults ===
DEFAULT_ELECTRICITY_RATE = 3500       # VND/kWh
DEFAULT_WATER_RATE = 25000            # VND/m³
DEFAULT_CONTRACT_DURATION = 12        # tháng
DEFAULT_INVOICE_DUE_DAYS = 5          # ngày từ lúc tạo
DEFAULT_BACKUP_RETENTION_DAYS = 30
DEFAULT_SESSION_TIMEOUT_MINUTES = 30
DEFAULT_PAGE_SIZE = 20
