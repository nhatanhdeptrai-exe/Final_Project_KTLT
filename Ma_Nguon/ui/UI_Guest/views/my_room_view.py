"""
MyRoomView — Trang "Phòng của tôi" cho Guest.
Hiển thị thông tin phòng, hợp đồng, và form gửi yêu cầu sửa chữa.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QStackedWidget,
    QLineEdit, QTextEdit, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt

"""
MyRoomView — Trang "Phòng của tôi" cho Guest.
Sử dụng giao diện được thiết kế từ phong_cua_toi.ui
Hiển thị thông tin phòng, hợp đồng, và form gửi yêu cầu sửa chữa.
"""
import os
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import Qt
from ui.UI_Guest.generated.ui_phong_cua_toi import Ui_GuestMainWindow

class MyRoomView(QWidget):
    """Widget Phòng của tôi — nhúng GuestWindow."""

    def __init__(self, user=None, contract_service=None, room_service=None,
                 repair_service=None, guest_service=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.contract_service = contract_service
        self.room_service = room_service
        self.repair_service = repair_service
        self.guest_service = guest_service
        
        self.ui = Ui_GuestMainWindow()
        self.ui.setupUi(self)
        
        # Override the container widget's layout if necessary to fit perfectly
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui.PagePhongCuaToi)
        
        self._setup_connections()
        self._load_data()

    def _setup_connections(self):
        # Default view is pageMyRoom (index 0)
        self.ui.stackGuestMain.setCurrentIndex(0)
        
        # Room card buttons
        if hasattr(self.ui, 'btnReqMaintenance'):
            self.ui.btnReqMaintenance.clicked.connect(lambda: self.ui.stackGuestMain.setCurrentIndex(1))
        
        # Maintenance form buttons
        if hasattr(self.ui, 'btnBackToRoom'):
            self.ui.btnBackToRoom.clicked.connect(lambda: self.ui.stackGuestMain.setCurrentIndex(0))
            
        if hasattr(self.ui, 'btnSubmitMnt'):
            self.ui.btnSubmitMnt.clicked.connect(self._submit_repair)
            
        # Contract buttons
        if hasattr(self.ui, 'btnViewContract'):
            self.ui.btnViewContract.clicked.connect(self._view_contract)
            
        if hasattr(self.ui, 'btnPrintContract'):
            self.ui.btnPrintContract.clicked.connect(self._print_contract)
            
        # Register new room (from this view)
        if hasattr(self.ui, 'btnRegNewRoom'):
            self.ui.btnRegNewRoom.clicked.connect(self._register_new_room)

    # ── Data Loading ──
    def _load_data(self):
        """Load room/contract data for current guest user."""
        if not self.user:
            return

        # 1. Tìm guest record
        guest = None
        if self.guest_service:
            all_guests = self.guest_service.get_all_guests()
            for g in all_guests:
                if getattr(g, 'email', None) == getattr(self.user, 'email', None) or \
                   getattr(g, 'phone', None) == getattr(self.user, 'phone', None):
                    guest = g
                    break

        if not guest:
            # Not a recognized guest yet
            self._show_empty_state("Bạn chưa đăng ký thuê phòng nào.")
            return

        # 2. Tìm active contract
        contract = None
        if self.contract_service:
            contracts = self.contract_service.get_all()
            for c in contracts:
                if str(getattr(c, 'guest_id', '')) == str(getattr(guest, 'id', '')):
                    if getattr(c, 'status', '') in ('active', 'Đang thuê', 'Còn hiệu lực'):
                        contract = c
                        break

        if not contract:
            self._show_empty_state("Bạn chưa có hợp đồng thuê phòng nào đang hiệu lực.")
            return

        # 3. Tìm room
        room = None
        if self.room_service:
            room_id = getattr(contract, 'room_id', None)
            if room_id:
                room = self.room_service.get_room_by_id(room_id)

        if not room:
            self._show_empty_state("Không tìm thấy thông tin phòng.")
            return

        # ── Hiển thị dữ liệu lên UI ──
        
        # Thông tin phòng
        labels = self.ui.pageMyRoom.findChildren(QLabel, "CardValue")
        
        if len(labels) >= 4:
            # Dựa vào thứ tự thiết kế: Tên, Địa chỉ, Diện tích, Giá
            labels[0].setText(getattr(room, 'name', '—'))
            labels[1].setText(f"📍 {getattr(room, 'address', 'Chưa có')}")
            
            area = getattr(room, 'area', getattr(room, 'size', ''))
            labels[2].setText(f"{area}m²" if area else "—")
            
            price = getattr(room, 'price', getattr(room, 'rent_price', 0))
            labels[3].setText(f"{int(price):,} VNĐ/tháng" if price else "—")
            
        status_lbl = self.ui.pageMyRoom.findChild(QLabel, "StatusActive")
        if status_lbl:
            status_lbl.setText("• Đang thuê" if getattr(room, 'status', '') == 'occupied' else f"• {getattr(room, 'status', 'Đang thuê')}")

        # Thông tin hợp đồng
        if hasattr(self.ui, 'txtContractContent'):
             # Update contract title if possible
             for lbl in self.ui.ContractPanel.findChildren(QLabel):
                 if "Số: " in lbl.text():
                     lbl.setText(f"Số: HĐ{getattr(contract, 'id', '—')}/{getattr(contract, 'start_date', '2024')[:4]}")
                     break
                     
             start = getattr(contract, 'start_date', '')
             end = getattr(contract, 'end_date', '')
             room_name = getattr(room, 'name', '')
             guest_name = getattr(guest, 'full_name', getattr(guest, 'name', ''))
             guest_cccd = getattr(guest, 'id_card', getattr(guest, 'cccd', '—'))

             contract_text = (
                 f"Hôm nay, ngày {start}, chúng tôi gồm:\n\n"
                 f"BÊN CHO THUÊ (Bên A):\n"
                 f"Ông/Bà: Quản trị viên\n"
                 f"SĐT: 0123.456.789\n\n"
                 f"BÊN THUÊ (Bên B):\n"
                 f"Ông/Bà: {guest_name}\n"
                 f"Số CMND/CCCD: {guest_cccd}\n"
                 f"SĐT: {getattr(guest, 'phone', '—')}\n\n"
                 f"Hai bên cùng thỏa thuận ký kết hợp đồng thuê nhà với các điều khoản sau:\n\n"
                 f"Điều 1: Đối tượng của hợp đồng\n"
                 f"- Bên A đồng ý cho Bên B thuê phòng trọ: {room_name}\n"
                 f"- Địa chỉ: {getattr(room, 'address', '—')}\n"
                 f"- Diện tích: {area}m²\n"
                 f"- Mục đích sử dụng: Ở\n\n"
                 f"Điều 2: Thời hạn thuê\n"
                 f"- Từ ngày: {start}\n"
                 f"- Đến ngày: {end}\n\n"
                 f"Điều 3: Giá thuê và phương thức thanh toán\n"
                 f"- Tiền thuê: {int(price):,} VNĐ/tháng\n"
                 f"- Tiền cọc: {int(getattr(contract, 'deposit', 0)):,} VNĐ\n"
             )
             self.ui.txtContractContent.setPlainText(contract_text)

    def _show_empty_state(self, message):
        """Thay đổi UI để báo khách chưa có phòng."""
        if hasattr(self.ui, 'txtContractContent'):
            self.ui.txtContractContent.setPlainText(message)
            self.ui.txtContractContent.setStyleSheet("color: #e53e3e; font-size: 16px; font-weight: bold; font-style: italic;")

    # ── Actions ──
    def _submit_repair(self):
        title = self.ui.inpMntTitle.text().strip()
        desc = self.ui.inpMntDesc.toPlainText().strip()
        priority = self.ui.inpMntPriority.text().strip() if hasattr(self.ui, 'inpMntPriority') and isinstance(self.ui.inpMntPriority, QLineEdit) else "Bình thường"

        if not title:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mục cần sửa chữa")
            return
        if not desc:
            QMessageBox.warning(self, "Lỗi", "Vui lòng mô tả chi tiết")
            return

        if self.repair_service:
            try:
                self.repair_service.create({
                    'title': title,
                    'description': desc,
                    'priority': priority,
                    'status': 'Chờ xử lý',
                    'guest_name': getattr(self.user, 'full_name', ''),
                })
                QMessageBox.information(self, "Thành công", "Gửi yêu cầu sửa chữa thành công!")
                self.ui.inpMntTitle.clear()
                self.ui.inpMntDesc.clear()
                if hasattr(self.ui, 'inpMntPriority') and isinstance(self.ui.inpMntPriority, QLineEdit):
                     self.ui.inpMntPriority.clear()
                self.ui.stackGuestMain.setCurrentIndex(0)
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể gửi: {e}")
        else:
            QMessageBox.information(self, "Thành công", "Gửi yêu cầu sửa chữa thành công (Demo)!")
            self.ui.inpMntTitle.clear()
            self.ui.inpMntDesc.clear()
            if hasattr(self.ui, 'inpMntPriority') and isinstance(self.ui.inpMntPriority, QLineEdit):
                 self.ui.inpMntPriority.clear()
            self.ui.stackGuestMain.setCurrentIndex(0)

    def _view_contract(self):
        QMessageBox.information(self, "Chi tiết", "Chức năng xem PDF chi tiết đang được phát triển.")
        
    def _print_contract(self):
        QMessageBox.information(self, "In hợp đồng", "Đang gửi tín hiệu đến máy in hợp đồng...")
        
    def _register_new_room(self):
        QMessageBox.information(self, "Đăng ký", "Để đăng ký phòng mới vui lòng liên hệ Ban quản lý tòa nhà.")
