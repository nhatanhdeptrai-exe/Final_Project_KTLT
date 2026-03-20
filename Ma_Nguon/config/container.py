"""ServiceContainer — DI Container kết nối toàn bộ hệ thống."""
from repositories.user_repository import UserRepository
from repositories.room_repository import RoomRepository
from repositories.guest_repository import GuestRepository
from repositories.contract_repository import ContractRepository
from repositories.invoice_repository import InvoiceRepository
from repositories.application_repository import ApplicationRepository
from repositories.repair_request_repository import RepairRequestRepository

from services.email_service import EmailService
from services.auth_service import AuthService
from services.room_service import RoomService
from services.guest_service import GuestService
from services.contract_service import ContractService
from services.invoice_service import InvoiceService
from services.application_service import ApplicationService
from services.repair_request_service import RepairRequestService
from services.iot_service import IoTService
from services.backup_service import BackupService
from services.report_service import ReportService


class ServiceContainer:
    """Singleton quản lý toàn bộ dependency."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # === Repositories ===
        self.user_repo = UserRepository()
        self.room_repo = RoomRepository()
        self.guest_repo = GuestRepository()
        self.contract_repo = ContractRepository()
        self.invoice_repo = InvoiceRepository()
        self.application_repo = ApplicationRepository()
        self.repair_request_repo = RepairRequestRepository()

        # === Services ===
        self.email_service = EmailService()
        self.auth_service = AuthService(self.user_repo, self.email_service)
        self.room_service = RoomService(self.room_repo)
        self.guest_service = GuestService(self.guest_repo)
        self.contract_service = ContractService(self.contract_repo, self.room_repo, self.guest_repo)
        self.invoice_service = InvoiceService(self.invoice_repo, self.contract_repo)
        self.application_service = ApplicationService(self.application_repo)
        self.repair_request_service = RepairRequestService(self.repair_request_repo)
        self.iot_service = IoTService(self.room_repo)
        self.backup_service = BackupService()
        self.report_service = ReportService(self.invoice_repo, self.room_repo, self.contract_repo, self.guest_repo)
