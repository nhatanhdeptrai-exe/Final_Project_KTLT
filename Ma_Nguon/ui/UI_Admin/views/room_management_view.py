"""
RoomManagementView — Quản lý phòng (trang Admin).
Hiển thị danh sách phòng dạng card, hỗ trợ CRUD qua dialog.
"""
import os
import shutil
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame, QLineEdit, QComboBox, QMessageBox,
    QScrollArea, QDialog, QSizePolicy, QSpacerItem, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon

from config.constants import BASE_DIR
from models.room import Room
from ui.UI_Admin.generated.ui_dialog_them_phong import Ui_DialogFormPhong

# Thư mục lưu ảnh phòng
ROOM_IMAGES_DIR = BASE_DIR / 'data' / 'room_images'
ROOM_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


class RoomCard(QFrame):
    """Card hiển thị thông tin 1 phòng."""
    detail_clicked = pyqtSignal(object)
    edit_clicked = pyqtSignal(object)

    STATUS_MAP = {
        'available': ('● Trống', '#38a169', '#e6fffa'),
        'occupied': ('● Đang thuê', '#3182ce', '#ebf8ff'),
        'maintenance': ('● Bảo trì', '#e53e3e', '#fff5f5'),
    }

    def __init__(self, room: Room, parent=None):
        super().__init__(parent)
        self.room = room
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("roomCard")
        self.setStyleSheet("""
            QFrame#roomCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 15px;
            }
            QFrame#roomCard:hover {
                border: 1px solid #0b8480;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        """)
        self.setFixedHeight(260)
        self.setMinimumWidth(200)
        self.setMaximumWidth(280)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # Row 1: Room number + status
        row1 = QHBoxLayout()
        lbl_name = QLabel(self.room.room_number)
        lbl_name.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_name.setStyleSheet("color: #2d3748;")
        row1.addWidget(lbl_name)
        row1.addStretch()

        status_text, status_color, status_bg = self.STATUS_MAP.get(
            self.room.status, ('● ?', '#718096', '#f7fafc'))
        lbl_status = QLabel(status_text)
        lbl_status.setStyleSheet(f"color: {status_color}; font-size: 11px; font-weight: bold; "
                                  f"background-color: {status_bg}; border-radius: 8px; padding: 2px 8px;")
        row1.addWidget(lbl_status)
        layout.addLayout(row1)

        # Row 2: Price
        price_text = f"{self.room.price / 1_000_000:.1f}M/tháng"
        lbl_price = QLabel(price_text)
        lbl_price.setStyleSheet("color: #0b8480; font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl_price)

        # Info rows
        room_type = getattr(self.room, 'room_type', '') or 'Phòng đơn'
        amenities_str = ", ".join(self.room.amenities) if self.room.amenities else "—"
        info_data = [
            ("Tầng", f"Tầng {self.room.floor}"),
            ("Diện tích", f"{self.room.area} m²"),
            ("Tiện nghi", amenities_str),
            ("Loại", room_type),
        ]
        for label, value in info_data:
            row = QHBoxLayout()
            lbl = QLabel(f"  {label}")
            lbl.setStyleSheet("color: #718096; font-size: 11px;")
            lbl.setFixedWidth(70)
            val = QLabel(value)
            val.setStyleSheet("color: #2d3748; font-size: 11px; font-weight: bold;")
            val.setWordWrap(True)
            row.addWidget(lbl)
            row.addWidget(val, 1)
            layout.addLayout(row)

        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_detail = QPushButton("Chi tiết")
        btn_detail.setStyleSheet(
            "QPushButton { background-color: #ebf8ff; color: #3182ce; border: 1px solid #bee3f8; "
            "border-radius: 6px; padding: 5px 12px; font-weight: bold; font-size: 11px; }"
            "QPushButton:hover { background-color: #bee3f8; }")
        btn_detail.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detail.clicked.connect(lambda: self.detail_clicked.emit(self.room))

        btn_edit = QPushButton("Cập nhật")
        btn_edit.setStyleSheet(
            "QPushButton { background-color: #e6fffa; color: #0b8480; border: 1px solid #b2f5ea; "
            "border-radius: 6px; padding: 5px 12px; font-weight: bold; font-size: 11px; }"
            "QPushButton:hover { background-color: #b2f5ea; }")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.room))

        btn_row.addWidget(btn_detail)
        btn_row.addWidget(btn_edit)
        layout.addLayout(btn_row)


class RoomFormDialog(QDialog):
    """Dialog thêm/sửa phòng."""

    def __init__(self, room: Room = None, parent=None):
        super().__init__(parent)
        self.room = room
        self._selected_images: list[str] = []  # absolute paths to new images
        self.ui = Ui_DialogFormPhong()
        self.ui.setupUi(self)

        # Connect image upload button
        self.ui.btnImage.clicked.connect(self._on_pick_images)

        if room:
            self.setWindowTitle("✏️ Cập nhật phòng")
            self.ui.lblDialogTitle.setText("✏️ Cập nhật phòng")
            self._fill_form(room)

        self.ui.btnCancel.clicked.connect(self.reject)
        self.ui.btnSave.clicked.connect(self._on_save)

    def _on_pick_images(self):
        """Mở file dialog chọn ảnh phòng."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Chọn ảnh phòng", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if files:
            self._selected_images = files
            # Show preview of first image on the button
            pixmap = QPixmap(files[0])
            if not pixmap.isNull():
                scaled = pixmap.scaled(QSize(380, 140),
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                self.ui.btnImage.setIcon(QIcon(scaled))
                self.ui.btnImage.setIconSize(scaled.size())
                count = len(files)
                self.ui.btnImage.setText(f"  {count} ảnh đã chọn" if count > 1 else "")

    def _save_images(self, room_number: str) -> list[str]:
        """Copy ảnh đã chọn vào thư mục room_images, trả về danh sách tên file."""
        saved = []
        room_dir = ROOM_IMAGES_DIR / room_number
        room_dir.mkdir(parents=True, exist_ok=True)
        for src_path in self._selected_images:
            filename = os.path.basename(src_path)
            dst = room_dir / filename
            try:
                shutil.copy2(src_path, str(dst))
                # Store relative path: room_images/P101/photo.jpg
                saved.append(f"room_images/{room_number}/{filename}")
            except Exception:
                pass
        return saved

    def _fill_form(self, room: Room):
        self.ui.inpName.setText(room.room_number)
        self.ui.inpPrice.setText(str(room.price))
        self.ui.inpArea.setText(str(room.area))
        self.ui.inpAmenities.setText(", ".join(room.amenities))
        self.ui.inpDesc.setPlainText(room.description)

        # Set floor combo
        floor_idx = room.floor - 1
        if 0 <= floor_idx < self.ui.cbFloor.count():
            self.ui.cbFloor.setCurrentIndex(floor_idx)

        # Set type combo
        room_type = getattr(room, 'room_type', 'Phòng đơn') or 'Phòng đơn'
        idx = self.ui.cbType.findText(room_type)
        if idx >= 0:
            self.ui.cbType.setCurrentIndex(idx)

        # Show existing image preview if available
        if room.images:
            img_path = str(BASE_DIR / 'data' / room.images[0])
            if os.path.exists(img_path):
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(QSize(380, 140),
                                           Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
                    self.ui.btnImage.setIcon(QIcon(scaled))
                    self.ui.btnImage.setIconSize(scaled.size())
                    self.ui.btnImage.setText(f"  {len(room.images)} ảnh (bấm để thay đổi)")

    def _on_save(self):
        name = self.ui.inpName.text().strip()
        price_str = self.ui.inpPrice.text().strip().replace('.', '').replace(',', '')

        if not name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên phòng")
            return
        if not price_str:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập giá phòng")
            return

        try:
            price = int(price_str)
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Giá phòng không hợp lệ")
            return

        area_str = self.ui.inpArea.text().strip()
        try:
            area = float(area_str) if area_str else 0.0
        except ValueError:
            area = 0.0

        floor_text = self.ui.cbFloor.currentText()
        floor = int(floor_text.replace("Tầng ", "")) if "Tầng" in floor_text else 1

        amenities_text = self.ui.inpAmenities.text().strip()
        amenities = [a.strip() for a in amenities_text.split(",") if a.strip()] if amenities_text else []

        room_type = self.ui.cbType.currentText()
        desc = self.ui.inpDesc.toPlainText().strip()

        # Save images
        images = []
        if self._selected_images:
            images = self._save_images(name)
        elif self.room and self.room.images:
            images = self.room.images  # keep existing images

        self.result_data = {
            'room_number': name,
            'price': price,
            'floor': floor,
            'area': area,
            'amenities': amenities,
            'room_type': room_type,
            'description': desc,
            'images': images,
        }
        self.accept()


class RoomDetailDialog(QDialog):
    """Dialog xem chi tiết phòng."""
    delete_requested = pyqtSignal(int)

    def __init__(self, room: Room, parent=None):
        super().__init__(parent)
        self.room = room
        self.setWindowTitle(f"Chi tiết phòng {room.room_number}")
        self.setMinimumSize(500, 600)
        self.setStyleSheet("QDialog { background-color: white; } QLabel { color: #2d3748; }")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # ── Image area ──
        if self.room.images:
            img_scroll = QScrollArea()
            img_scroll.setFixedHeight(200)
            img_scroll.setWidgetResizable(True)
            img_scroll.setStyleSheet("QScrollArea { border: 1px solid #e2e8f0; border-radius: 8px; background: #f7fafc; }")
            img_container = QWidget()
            img_layout = QHBoxLayout(img_container)
            img_layout.setSpacing(10)
            img_layout.setContentsMargins(10, 10, 10, 10)
            img_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            for img_rel in self.room.images:
                img_path = str(BASE_DIR / 'data' / img_rel)
                if os.path.exists(img_path):
                    pixmap = QPixmap(img_path)
                    if not pixmap.isNull():
                        scaled = pixmap.scaled(QSize(250, 180),
                                               Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)
                        lbl_img = QLabel()
                        lbl_img.setPixmap(scaled)
                        lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        lbl_img.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 4px; background: white;")
                        img_layout.addWidget(lbl_img)

            img_scroll.setWidget(img_container)
            layout.addWidget(img_scroll)
        else:
            no_img = QLabel("📷 Chưa có ảnh phòng")
            no_img.setFixedHeight(80)
            no_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_img.setStyleSheet("color: #a0aec0; font-size: 14px; background: #f7fafc; "
                                  "border: 2px dashed #cbd5e0; border-radius: 8px;")
            layout.addWidget(no_img)

        # Title
        title = QLabel(f"🏠 Phòng {self.room.room_number}")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2d3748;")
        layout.addWidget(title)

        # Status
        status_map = {
            'available': ('● Trống', '#38a169'),
            'occupied': ('● Đang thuê', '#3182ce'),
            'maintenance': ('● Bảo trì', '#e53e3e'),
        }
        st, sc = status_map.get(self.room.status, ('?', '#718096'))
        lbl_st = QLabel(st)
        lbl_st.setStyleSheet(f"color: {sc}; font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl_st)

        # Info
        info_items = [
            ("Giá phòng", f"{self.room.price:,.0f} VNĐ/tháng"),
            ("Tiền cọc", f"{self.room.deposit:,.0f} VNĐ"),
            ("Tầng", f"Tầng {self.room.floor}"),
            ("Diện tích", f"{self.room.area} m²"),
            ("Loại phòng", getattr(self.room, 'room_type', 'Phòng đơn') or 'Phòng đơn'),
            ("Tiện nghi", ", ".join(self.room.amenities) if self.room.amenities else "—"),
            ("Mô tả", self.room.description or "—"),
        ]
        for label, value in info_items:
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setFixedWidth(100)
            lbl.setStyleSheet("color: #718096; font-weight: bold;")
            val = QLabel(value)
            val.setWordWrap(True)
            val.setStyleSheet("color: #2d3748;")
            row.addWidget(lbl)
            row.addWidget(val, 1)
            layout.addLayout(row)

        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_del = QPushButton("🗑️ Xóa phòng")
        btn_del.setStyleSheet(
            "QPushButton { background-color: #fff5f5; color: #e53e3e; border: 1px solid #fed7d7; "
            "border-radius: 6px; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:hover { background-color: #fed7d7; }")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(self._on_delete)

        btn_close = QPushButton("Đóng")
        btn_close.setStyleSheet(
            "QPushButton { background-color: #f7fafc; border: 1px solid #cbd5e0; "
            "border-radius: 6px; padding: 8px 16px; font-weight: bold; color: #4a5568; }"
            "QPushButton:hover { background-color: #edf2f7; }")
        btn_close.clicked.connect(self.accept)

        btn_row.addWidget(btn_del)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _on_delete(self):
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc muốn xóa phòng {self.room.room_number}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.room.id)
            self.accept()


class RoomManagementView(QWidget):
    """Widget quản lý phòng — Được nhúng vào AdminWindow."""

    def __init__(self, room_service=None, parent=None):
        super().__init__(parent)
        self.room_service = room_service
        self._current_filter = "all"
        self._search_text = ""
        self._build_ui()
        self.refresh_rooms()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)

        # ── Top bar: search + filter + add button ──
        top_bar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm tên phòng...")
        self.search_input.setStyleSheet(
            "QLineEdit { background-color: #f7fafc; border: 1px solid #e2e8f0; "
            "border-radius: 8px; padding: 8px 15px; font-size: 13px; }")
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self._on_search)
        top_bar.addWidget(self.search_input)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tất cả trạng thái", "Trống", "Đang thuê", "Bảo trì"])
        self.filter_combo.setStyleSheet(
            "QComboBox { background-color: #f7fafc; border: 1px solid #e2e8f0; "
            "border-radius: 8px; padding: 8px 12px; font-size: 13px; }")
        self.filter_combo.currentIndexChanged.connect(self._on_filter)
        top_bar.addWidget(self.filter_combo)

        top_bar.addStretch()

        btn_add = QPushButton("+ Thêm phòng mới")
        btn_add.setStyleSheet(
            "QPushButton { background-color: #0b8480; color: white; border: none; "
            "border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #096c69; }")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._on_add_room)
        top_bar.addWidget(btn_add)

        main_layout.addLayout(top_bar)

        # ── Room count label ──
        self.lbl_count = QLabel("Tất cả phòng (0)")
        self.lbl_count.setStyleSheet("color: #2d3748; font-size: 14px; font-weight: bold;")
        main_layout.addWidget(self.lbl_count)

        # ── Scroll area for room cards ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background-color: transparent;")
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(self.cards_container)
        main_layout.addWidget(scroll, 1)

    # ── Data ──
    def refresh_rooms(self):
        """Load & display rooms from service."""
        if not self.room_service:
            return

        rooms = self.room_service.get_all_rooms()

        # Apply filter
        filter_map = {1: 'available', 2: 'occupied', 3: 'maintenance'}
        status_filter = filter_map.get(self.filter_combo.currentIndex())
        if status_filter:
            rooms = [r for r in rooms if r.status == status_filter]

        # Apply search
        if self._search_text:
            q = self._search_text.lower()
            rooms = [r for r in rooms if q in r.room_number.lower() or q in r.description.lower()]

        self.lbl_count.setText(f"Tất cả phòng ({len(rooms)})")

        # Clear old cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Create cards (5 per row, matching the screenshot)
        cols = 5
        for i, room in enumerate(rooms):
            card = RoomCard(room)
            card.detail_clicked.connect(self._on_detail)
            card.edit_clicked.connect(self._on_edit)
            self.cards_layout.addWidget(card, i // cols, i % cols)

        # Prevent rows from stretching — push cards to top
        total_rows = (len(rooms) + cols - 1) // cols if rooms else 0
        for r in range(total_rows):
            self.cards_layout.setRowStretch(r, 0)
        # Add a stretch row at the bottom to absorb extra space
        self.cards_layout.setRowStretch(total_rows, 1)

    def _on_search(self, text):
        self._search_text = text
        self.refresh_rooms()

    def _on_filter(self, idx):
        self.refresh_rooms()

    # ── CRUD Actions ──
    def _on_add_room(self):
        dlg = RoomFormDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.result_data
            ok, msg = self.room_service.create_room(
                room_number=data['room_number'],
                floor=data['floor'],
                area=data['area'],
                price=data['price'],
                deposit=data['price'],  # deposit = price by default
                description=data['description'],
                amenities=data['amenities'],
            )
            if ok:
                # Save images to the newly created room
                if data.get('images'):
                    rooms = self.room_service.get_all_rooms()
                    new_room = next((r for r in rooms if r.room_number == data['room_number']), None)
                    if new_room:
                        new_room.images = data['images']
                        self.room_service.update_room(new_room)
                QMessageBox.information(self, "Thành công", msg)
                self.refresh_rooms()
            else:
                QMessageBox.warning(self, "Lỗi", msg)

    def _on_edit(self, room: Room):
        dlg = RoomFormDialog(room=room, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.result_data
            room.room_number = data['room_number']
            room.floor = data['floor']
            room.area = data['area']
            room.price = data['price']
            room.description = data['description']
            room.amenities = data['amenities']
            room.images = data.get('images', room.images)
            ok, msg = self.room_service.update_room(room)
            if ok:
                QMessageBox.information(self, "Thành công", msg)
                self.refresh_rooms()
            else:
                QMessageBox.warning(self, "Lỗi", msg)

    def _on_detail(self, room: Room):
        dlg = RoomDetailDialog(room, parent=self)
        dlg.delete_requested.connect(self._on_delete_room)
        dlg.exec()

    def _on_delete_room(self, room_id: int):
        ok, msg = self.room_service.delete_room(room_id)
        if ok:
            QMessageBox.information(self, "Thành công", msg)
            self.refresh_rooms()
        else:
            QMessageBox.warning(self, "Lỗi", msg)
