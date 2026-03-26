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
import os

"""
MyRoomView — Trang "Phòng của tôi" cho Guest.
Sử dụng giao diện được thiết kế từ phong_cua_toi.ui
Hiển thị thông tin phòng, hợp đồng, và form gửi yêu cầu sửa chữa.
"""
import os
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import Qt
from ui.UI_Guest.generated.ui_phong_cua_toi_UI import Ui_GuestMainWindow
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
        self._replace_title_with_combobox()
        self._load_data()

    def _replace_title_with_combobox(self):
        """Thay QLineEdit inpMntTitle bằng QComboBox danh mục sửa chữa."""
        from PyQt6.QtWidgets import QComboBox
        old = self.ui.inpMntTitle
        cb = QComboBox(old.parentWidget())
        cb.setObjectName("inpMntTitle")
        cb.addItems(["Điện", "Nước", "Khóa cửa", "Điều hòa", "Tường/Trần", "Khác"])
        cb.setMinimumHeight(old.minimumHeight() if old.minimumHeight() > 0 else 40)
        cb.setStyleSheet(
            "QComboBox { background-color: white; border: 1px solid #e2e8f0; "
            "border-radius: 8px; padding: 8px 15px; font-size: 14px; color: #4a5568; }"
            "QComboBox:focus { border: 1px solid #0b8480; }")
        # Replace in layout
        layout = self.ui.vboxlayout5
        idx = layout.indexOf(old)
        if idx >= 0:
            layout.replaceWidget(old, cb)
            old.hide()
            old.deleteLater()
        self.ui.inpMntTitle = cb

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
                            if getattr(c, 'status', '') in ('active', 'pending_cancel', 'Đang thuê', 'Còn hiệu lực'):
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

        # ── IoT Điện Nước ──
        self._current_room_number = room_name
        self._setup_iot_display(room_name)

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
            f"Ông/Bà: Tạ Nhật Anh\n"
            f"SĐT: 0364216007\n"
            f"Địa chỉ: 2 đường số 10, P. Tam Bình, Thủ Đức, TP.HCM\n\n"
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

        # Nếu đang chờ duyệt đổi phòng → disable nút + hiển thị trạng thái
        if active_contract and getattr(active_contract, 'status', '') == 'pending_cancel':
            if hasattr(self.ui, 'btnRegNewRoom'):
                self.ui.btnRegNewRoom.setEnabled(False)
                self.ui.btnRegNewRoom.setText("⏳ Đang chờ duyệt đổi phòng...")

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

    def _setup_iot_display(self, room_number):
        """Thêm section IoT điện nước + dọn layout."""
        from PyQt6.QtWidgets import QVBoxLayout, QFrame, QScrollArea
        from PyQt6.QtCore import QTimer

        # 1. Di chuyển nút "Yêu cầu sửa chữa" ra ngoài frame1
        #    từ vboxlayout2 → vboxlayout1 (cùng cấp với "Đăng ký phòng mới")
        btn_mnt = self.ui.btnReqMaintenance
        self.ui.vboxlayout2.removeWidget(btn_mnt)
        reg_idx = self.ui.vboxlayout1.indexOf(self.ui.btnRegNewRoom)
        self.ui.vboxlayout1.insertWidget(reg_idx, btn_mnt)

        # 2. Thêm IoT frame vào cuối frame1 (vboxlayout2)
        iot_frame = QFrame()
        iot_frame.setObjectName("iotFrame")
        iot_frame.setStyleSheet(
            "QFrame#iotFrame { background: #fffbeb; border: 1px solid #fbbf24;"
            " border-radius: 8px; padding: 6px 10px; }"
            " QFrame#iotFrame QLabel { border: none; background: transparent; }")
        iot_lay = QVBoxLayout(iot_frame)
        iot_lay.setSpacing(2)
        iot_lay.setContentsMargins(8, 4, 8, 4)

        self._iot_status_lbl = QLabel("⚡ IOT  🔴 Kết nối...")
        self._iot_status_lbl.setStyleSheet("color: #92400e; font-size: 10px; font-weight: bold;")
        iot_lay.addWidget(self._iot_status_lbl)

        self._guest_elec_val = QLabel("⚡ Điện: ---")
        self._guest_elec_val.setStyleSheet("color: #b45309; font-size: 12px; font-weight: bold;")
        iot_lay.addWidget(self._guest_elec_val)

        self._guest_water_val = QLabel("💧 Nước: ---")
        self._guest_water_val.setStyleSheet("color: #1d4ed8; font-size: 12px; font-weight: bold;")
        iot_lay.addWidget(self._guest_water_val)

        self._guest_iot_time = QLabel("")
        self._guest_iot_time.setStyleSheet("color: #9ca3af; font-size: 9px;")
        iot_lay.addWidget(self._guest_iot_time)

        self.ui.vboxlayout2.addWidget(iot_frame)

        # 3. Wrap panel trái trong scroll area
        left_frame = self.ui.frame
        parent_layout = self.ui.hboxlayout1
        idx = parent_layout.indexOf(left_frame)
        parent_layout.removeWidget(left_frame)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setMaximumWidth(355)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(left_frame)
        parent_layout.insertWidget(idx, scroll)

        # 4. Timer
        self._iot_timer = QTimer(self)
        self._iot_timer.timeout.connect(self._refresh_iot)
        self._iot_timer.start(3000)
        self._refresh_iot()

    def _refresh_iot(self):
        """Cập nhật chỉ số IoT cho guest view."""
        if not hasattr(self, '_current_room_number'):
            return

        iot_service = None
        try:
            parent_window = self.window()
            container = getattr(parent_window, 'container', None)
            if container:
                iot_service = getattr(container, 'iot_service', None)
        except Exception:
            pass

        if not iot_service:
            self._iot_status_lbl.setText("⚡ IOT  🔴 Chưa kết nối")
            return

        data = iot_service.get_latest(self._current_room_number)
        if not data:
            self._iot_status_lbl.setText("⚡ IOT  🔴 Chưa có dữ liệu")
            return

        self._iot_status_lbl.setText("⚡ IOT  🟢 Realtime")

        elec = data.get('electric', {})
        if elec:
            self._guest_elec_val.setText(f"⚡ Điện: {elec.get('value', 0):,.1f} {elec.get('unit', 'kWh')}")

        water = data.get('water', {})
        if water:
            self._guest_water_val.setText(f"💧 Nước: {water.get('value', 0):,.2f} {water.get('unit', 'm³')}")

        ts = data.get('last_update', '')
        if ts:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(ts)
                self._guest_iot_time.setText(f"Cập nhật: {dt.strftime('%H:%M:%S %d/%m')}")
            except Exception:
                pass

    def _show_empty_state(self, message):
        """Thay đổi UI để báo khách chưa có phòng."""
        if hasattr(self.ui, 'txtContractContent'):
            self.ui.txtContractContent.setPlainText(message)
            self.ui.txtContractContent.setStyleSheet("color: #e53e3e; font-size: 16px; font-weight: bold; font-style: italic;")

    # ── Actions ──
    def _submit_repair(self):
        title = self.ui.inpMntTitle.currentText().strip()
        desc = self.ui.inpMntDesc.toPlainText().strip()
        priority = self.ui.inpMntPriority.currentText().strip() if hasattr(self.ui, 'inpMntPriority') else "medium"

        if not title:
            show_warning(self, "Lỗi", "Vui lòng chọn mục cần sửa chữa")
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
                self.ui.inpMntTitle.setCurrentIndex(0)
                self.ui.inpMntDesc.clear()
                if hasattr(self.ui, 'inpMntPriority'):
                    self.ui.inpMntPriority.setCurrentIndex(1)
                self.ui.stackGuestMain.setCurrentIndex(0)
            except Exception as e:
                show_warning(self, "Lỗi", f"Không thể gửi: {e}")
        else:
            show_success(self, "Thành công", "Gửi yêu cầu sửa chữa thành công (Demo)!")
            self.ui.inpMntTitle.setCurrentIndex(0)
            self.ui.inpMntDesc.clear()
            if hasattr(self.ui, 'inpMntPriority'):
                self.ui.inpMntPriority.setCurrentIndex(1)
            self.ui.stackGuestMain.setCurrentIndex(0)

    def _view_contract(self):
        """Mở dialog xem hợp đồng đẹp."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser
        from PyQt6.QtGui import QFont

        contract_data = self._get_contract_data()
        if not contract_data:
            show_warning(self, "Lỗi", "Không tìm thấy thông tin hợp đồng.")
            return

        # Build HTML from template
        from utils.pdf_generator import PDFGenerator
        html = PDFGenerator._build_contract_html(contract_data)

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Hợp đồng {contract_data.get('contract_number', '')}")
        dlg.setFixedSize(650, 700)
        dlg.setStyleSheet("QDialog { background-color: white; }")

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        browser = QTextBrowser()
        browser.setHtml(html)
        browser.setStyleSheet("QTextBrowser { border: none; padding: 10px; }")
        browser.setOpenExternalLinks(False)
        lay.addWidget(browser)

        # Bottom buttons
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(20, 10, 20, 15)
        btn_row.setSpacing(10)
        btn_row.addStretch()

        btn_export = QPushButton("📄 Xuất PDF")
        btn_export.setStyleSheet(
            "QPushButton { background-color: #0b8480; color: white; border: none; "
            "border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #096c69; }")
        btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export.clicked.connect(lambda: (dlg.close(), self._print_contract()))
        btn_row.addWidget(btn_export)

        btn_close = QPushButton("Đóng")
        btn_close.setStyleSheet(
            "QPushButton { background: #f7fafc; color: #4a5568; border: 1px solid #cbd5e0; "
            "border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background: #edf2f7; }")
        btn_close.clicked.connect(dlg.close)
        btn_row.addWidget(btn_close)
        lay.addLayout(btn_row)

        dlg.exec()

    def _print_contract(self):
        """Xuất hợp đồng ra PDF và lưu về máy."""
        from PyQt6.QtWidgets import QFileDialog
        from datetime import datetime

        # Collect contract data
        contract_data = self._get_contract_data()
        if not contract_data:
            show_warning(self, "Lỗi", "Không tìm thấy thông tin hợp đồng.")
            return

        # Save As dialog
        default_name = f"HopDong_{contract_data.get('contract_number', 'HD')}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu hợp đồng", default_name,
            "PDF Files (*.pdf);;All Files (*)")
        if not file_path:
            return

        try:
            from utils.pdf_generator import PDFGenerator
            result = PDFGenerator.export_contract_pdf(contract_data, file_path)
            show_success(self, "Xuất thành công",
                         f"Hợp đồng đã được lưu tại:\n{result}")
            # Auto-open the file
            os.startfile(result)
        except Exception as e:
            show_error(self, "Lỗi", f"Không thể xuất PDF:\n{e}")

    def _get_contract_data(self) -> dict:
        """Thu thập dữ liệu hợp đồng cho PDF export."""
        from datetime import datetime
        if not self.user or not self.guest_service or not self.contract_service:
            return {}

        guest = None
        active_contract = None
        all_guests = self.guest_service.get_all_guests()
        matching_guests = [g for g in all_guests
                           if getattr(g, 'user_id', 0) == getattr(self.user, 'id', -1)
                           or getattr(g, 'email', None) == getattr(self.user, 'email', None)
                           or getattr(g, 'phone', None) == getattr(self.user, 'phone', None)]

        if matching_guests and self.contract_service:
            for g in matching_guests:
                for c in self.contract_service.get_all():
                    if str(getattr(c, 'guest_id', '')) == str(getattr(g, 'id', '')):
                        if getattr(c, 'status', '') in ('active', 'Đang thuê'):
                            guest = g
                            active_contract = c
                            break
                if active_contract:
                    break

        if not guest or not active_contract:
            return {}

        room = None
        if self.room_service:
            room = self.room_service.get_room_by_id(getattr(active_contract, 'room_id', 0))

        price = getattr(active_contract, 'monthly_rent', 0) or (getattr(room, 'price', 0) if room else 0)
        deposit = getattr(active_contract, 'deposit', 0) or (getattr(room, 'deposit', 0) if room else 0)

        return {
            'contract_number': getattr(active_contract, 'contract_number', f'HD{active_contract.id}'),
            'sign_date': datetime.now().strftime('%d/%m/%Y'),
            'landlord_name': 'Tạ Nhật Anh',
            'landlord_phone': '0364216007',
            'landlord_address': '2 đường số 10, P. Tam Bình, Thủ Đức, TP.HCM',
            'guest_name': getattr(guest, 'full_name', ''),
            'guest_dob': getattr(guest, 'dob', '—'),
            'guest_gender': getattr(guest, 'gender', '—'),
            'guest_cccd': getattr(guest, 'id_card', '—'),
            'guest_phone': getattr(guest, 'phone', '—'),
            'guest_email': getattr(guest, 'email', '—'),
            'room_number': getattr(room, 'room_number', '—') if room else '—',
            'room_floor': getattr(room, 'floor', '—') if room else '—',
            'room_area': getattr(room, 'area', '—') if room else '—',
            'monthly_rent': f'{int(price):,}',
            'deposit': f'{int(deposit):,}',
            'start_date': getattr(active_contract, 'start_date', '—'),
            'end_date': getattr(active_contract, 'end_date', '—'),
        }

    def _register_new_room(self):
        """Yêu cầu đổi phòng: xác nhận → gửi thông báo admin → chờ duyệt."""
        import json
        from datetime import datetime

        # 1. Tìm guest + active contract hiện tại
        guest, active_contract, room = self._find_current_booking()
        if not guest or not active_contract:
            show_warning(self, "Lỗi", "Không tìm thấy hợp đồng đang hiệu lực.")
            return

        # 2. Kiểm tra đã có yêu cầu pending_cancel chưa
        if active_contract.status == 'pending_cancel':
            show_info(self, "Thông báo", "Yêu cầu đổi phòng đã được gửi.\nVui lòng chờ admin duyệt.")
            return

        room_name = room.room_number if room else "—"

        # 3. Hỏi xác nhận
        if not ask_danger(self, "Xác nhận đổi phòng",
                          f"Bạn có chắc muốn bỏ phòng {room_name} hiện tại "
                          f"để đăng ký phòng mới?\n\n"
                          f"Yêu cầu sẽ được gửi đến Admin để duyệt.\n"
                          f"Sau khi duyệt, hợp đồng hiện tại sẽ chấm dứt "
                          f"và phòng {room_name} sẽ trở thành trống.",
                          yes_text="Đồng ý đổi phòng", no_text="Hủy bỏ"):
            return

        # 4. Đặt contract sang trạng thái chờ duyệt hủy
        active_contract.status = 'pending_cancel'
        self.contract_service.contract_repo.update(active_contract)

        # 5. Gửi thông báo cho Admin
        notif_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  '..', '..', '..', 'data', 'notifications.json')
        notif_file = os.path.normpath(notif_file)
        try:
            with open(notif_file, 'r', encoding='utf-8') as f:
                notifs = json.load(f)
        except Exception:
            notifs = []

        notifs.insert(0, {
            'id': f'room_change_{active_contract.id}',
            'icon': '🔄',
            'icon_bg': '#fef3c7',
            'icon_color': '#92400e',
            'text': f'Khách {guest.full_name} yêu cầu đổi phòng (hiện tại: {room_name})',
            'time': datetime.now().isoformat(),
            'read': False,
            'target': 'room_change',
        })
        try:
            with open(notif_file, 'w', encoding='utf-8') as f:
                json.dump(notifs, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        # 6. Thông báo cho guest
        show_success(self, "Đã gửi yêu cầu",
                     f"Yêu cầu đổi phòng đã được gửi đến Admin.\n"
                     f"Vui lòng chờ Admin duyệt.\n\n"
                     f"Sau khi duyệt, bạn sẽ có thể đăng ký phòng mới.")

        # 7. Disable nút để tránh gửi trùng
        if hasattr(self.ui, 'btnRegNewRoom'):
            self.ui.btnRegNewRoom.setEnabled(False)
            self.ui.btnRegNewRoom.setText("⏳ Đang chờ duyệt...")

    def _find_current_booking(self):
        """Tìm guest, active contract và room hiện tại."""
        if not self.user or not self.guest_service or not self.contract_service:
            return None, None, None

        guest = None
        active_contract = None
        all_guests = self.guest_service.get_all_guests()
        matching_guests = [g for g in all_guests
                           if getattr(g, 'user_id', 0) == getattr(self.user, 'id', -1)
                           or getattr(g, 'email', None) == getattr(self.user, 'email', None)
                           or getattr(g, 'phone', None) == getattr(self.user, 'phone', None)]

        if matching_guests and self.contract_service:
            for g in matching_guests:
                for c in self.contract_service.get_all():
                    if str(getattr(c, 'guest_id', '')) == str(getattr(g, 'id', '')):
                        if getattr(c, 'status', '') in ('active', 'pending_cancel'):
                            guest = g
                            active_contract = c
                            break
                if active_contract:
                    break

        room = None
        if active_contract and self.room_service:
            room = self.room_service.get_room_by_id(getattr(active_contract, 'room_id', 0))

        return guest, active_contract, room

