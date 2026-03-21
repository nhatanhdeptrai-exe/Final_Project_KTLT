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
from ui.UI_Common.custom_popup import show_success, show_error, show_warning, show_info, ask_question, ask_danger

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

        # 1. Tìm guest record (check ALL matching guests)
        guest = None
        active_contract = None
        if self.guest_service:
            all_guests = self.guest_service.get_all_guests()
            matching_guests = []
            for g in all_guests:
                if getattr(g, 'user_id', 0) == getattr(self.user, 'id', -1):
                    matching_guests.append(g)
                elif getattr(g, 'email', None) == getattr(self.user, 'email', None):
                    matching_guests.append(g)
                elif getattr(g, 'phone', None) == getattr(self.user, 'phone', None):
                    matching_guests.append(g)

            # 2. Tìm active contract for any matching guest
            if matching_guests and self.contract_service:
                contracts = self.contract_service.get_all()
                for g in matching_guests:
                    for c in contracts:
                        if str(getattr(c, 'guest_id', '')) == str(getattr(g, 'id', '')):
                            if getattr(c, 'status', '') in ('active', 'Đang thuê', 'Còn hiệu lực'):
                                guest = g
                                active_contract = c
                                break
                    if active_contract:
                        break

        if not guest:
            self._show_empty_state("Bạn chưa đăng ký thuê phòng nào.")
            return

        if not active_contract:
            self._show_empty_state("Bạn chưa có hợp đồng thuê phòng nào đang hiệu lực.")
            return

        # 3. Tìm room
        room = None
        if self.room_service:
            room_id = getattr(active_contract, 'room_id', None)
            if room_id:
                room = self.room_service.get_room_by_id(room_id)

        if not room:
            self._show_empty_state("Không tìm thấy thông tin phòng.")
            return

        # ── Hiển thị dữ liệu lên UI (trực tiếp qua tên widget) ──
        room_name = getattr(room, 'room_number', getattr(room, 'name', '—'))
        address = getattr(room, 'address', getattr(room, 'description', 'Chưa có'))
        area = getattr(room, 'area', getattr(room, 'size', ''))
        price = getattr(room, 'price', getattr(room, 'rent_price', 0))

        # label2 = Tên phòng
        self.ui.label2.setText(f"Phòng {room_name}")
        # label4 = Địa chỉ
        self.ui.label4.setText(f"📍 {address}")
        # label6 = Diện tích
        self.ui.label6.setText(f"{area}m²" if area else "—")
        # label8 = Giá thuê
        self.ui.label8.setText(f"$ {int(price):,} VNĐ/tháng" if price else "—")
        # label10 = Trạng thái
        status = getattr(room, 'status', 'occupied')
        self.ui.label10.setText("• Đang thuê" if status == 'occupied' else f"• {status}")

        # label12 = Số hợp đồng
        contract_num = getattr(active_contract, 'contract_number', f'HĐ{active_contract.id}')
        self.ui.label12.setText(f"Số: {contract_num}")

        # Nội dung hợp đồng
        start = getattr(active_contract, 'start_date', '')
        end = getattr(active_contract, 'end_date', '')
        guest_name = getattr(guest, 'full_name', '')
        guest_cccd = getattr(guest, 'id_card', '—')
        deposit = getattr(active_contract, 'deposit', 0)

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
            f"- Địa chỉ: {address}\n"
            f"- Diện tích: {area}m²\n"
            f"- Mục đích sử dụng: Ở\n\n"
            f"Điều 2: Thời hạn thuê\n"
            f"- Từ ngày: {start}\n"
            f"- Đến ngày: {end}\n\n"
            f"Điều 3: Giá thuê và phương thức thanh toán\n"
            f"- Tiền thuê: {int(price):,} VNĐ/tháng\n"
            f"- Tiền cọc: {int(deposit):,} VNĐ\n"
        )
        self.ui.txtContractContent.setPlainText(contract_text)

        # Load ảnh phòng nếu có
        images = getattr(room, 'images', [])
        if images and len(images) > 0:
            import os
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '..', '..', '..', 'data', images[0])
            if os.path.exists(img_path):
                from PyQt6.QtGui import QPixmap
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    self.ui.lblRoomImage.setPixmap(
                        pixmap.scaled(self.ui.lblRoomImage.size(),
                                     Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation))
                    self.ui.lblRoomImage.setText("")

    def _show_empty_state(self, message):
        """Thay đổi UI để báo khách chưa có phòng."""
        if hasattr(self.ui, 'txtContractContent'):
            self.ui.txtContractContent.setPlainText(message)
            self.ui.txtContractContent.setStyleSheet("color: #e53e3e; font-size: 16px; font-weight: bold; font-style: italic;")

    # ── Actions ──
    def _submit_repair(self):
        title = self.ui.inpMntTitle.text().strip()
        desc = self.ui.inpMntDesc.toPlainText().strip()
        priority = self.ui.inpMntPriority.text().strip() if hasattr(self.ui, 'inpMntPriority') else "medium"

        if not title:
            show_warning(self, "Lỗi", "Vui lòng nhập mục cần sửa chữa")
            return
        if not desc:
            show_warning(self, "Lỗi", "Vui lòng mô tả chi tiết")
            return

        # Map priority text to English if needed
        priority_map = {"Thấp": "low", "Trung bình": "medium", "Cao": "high", "Khẩn cấp": "urgent"}
        priority_en = priority_map.get(priority, priority if priority else "medium")

        if self.repair_service:
            try:
                # Find guest_id and room_id for current user
                guest_id = 0
                room_id = 0
                if self.guest_service:
                    all_guests = self.guest_service.get_all_guests()
                    for g in all_guests:
                        if getattr(g, 'email', None) == getattr(self.user, 'email', None) or \
                           getattr(g, 'phone', None) == getattr(self.user, 'phone', None):
                            guest_id = getattr(g, 'id', 0)
                            break

                if guest_id and self.contract_service:
                    for c in self.contract_service.get_all():
                        if str(getattr(c, 'guest_id', '')) == str(guest_id):
                            if getattr(c, 'status', '') in ('active', 'Đang thuê', 'Còn hiệu lực'):
                                room_id = getattr(c, 'room_id', 0)
                                break

                success, msg = self.repair_service.create_request(
                    guest_id=guest_id,
                    room_id=room_id,
                    title=title,
                    description=desc,
                    priority=priority_en,
                )
                show_success(self, "Thành công", msg)
                self.ui.inpMntTitle.clear()
                self.ui.inpMntDesc.clear()
                if hasattr(self.ui, 'inpMntPriority'):
                    self.ui.inpMntPriority.clear()
                self.ui.stackGuestMain.setCurrentIndex(0)
            except Exception as e:
                show_warning(self, "Lỗi", f"Không thể gửi: {e}")
        else:
            show_success(self, "Thành công", "Gửi yêu cầu sửa chữa thành công (Demo)!")
            self.ui.inpMntTitle.clear()
            self.ui.inpMntDesc.clear()
            if hasattr(self.ui, 'inpMntPriority'):
                self.ui.inpMntPriority.clear()
            self.ui.stackGuestMain.setCurrentIndex(0)

    def _view_contract(self):
        show_info(self, "Chi tiết", "Chức năng xem PDF chi tiết đang được phát triển.")
        
    def _print_contract(self):
        show_info(self, "In hợp đồng", "Đang gửi tín hiệu đến máy in hợp đồng...")
        
    def _register_new_room(self):
        show_info(self, "Đăng ký", "Để đăng ký phòng mới vui lòng liên hệ Ban quản lý tòa nhà.")
