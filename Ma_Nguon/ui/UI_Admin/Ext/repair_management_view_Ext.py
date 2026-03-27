
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QComboBox, QMessageBox, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QScrollArea, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from models.repair_request import RepairRequest
from ui.UI_Common.custom_popup import show_success, show_error, show_warning, show_info, ask_question, ask_danger


# ── Stat Card ────────────────────────────────────────────
_repair_stat_counter = 0

class RepairStatCard(QFrame):
    def __init__(self, icon, value, label, bg, val_color="#2d3748", parent=None):
        super().__init__(parent)
        global _repair_stat_counter
        _repair_stat_counter += 1
        obj_name = f"repairStatCard_{_repair_stat_counter}"
        self.setObjectName(obj_name)
        self.setStyleSheet(
            f"QFrame#{obj_name}{{background:white;border:1px solid #e2e8f0;border-radius:10px;padding:12px;}}"
            f" QFrame#{obj_name} QLabel{{border:none;}}")
        lo = QHBoxLayout(self); lo.setSpacing(10)
        ic = QLabel(icon); ic.setFixedSize(44, 44); ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet(f"font-size:24px;background:{bg};border-radius:8px;padding:8px;border:none;"); lo.addWidget(ic)
        info = QVBoxLayout(); info.setSpacing(2)
        self.val_lbl = QLabel(value)
        self.val_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.val_lbl.setStyleSheet(f"color:{val_color};border:none;"); info.addWidget(self.val_lbl)
        d = QLabel(label); d.setStyleSheet("color:#718096;font-size:11px;border:none;"); info.addWidget(d)
        lo.addLayout(info)


# ── Detail Dialog ────────────────────────────────────────
class RepairDetailDialog(QDialog):
    """Chi tiết yêu cầu sửa chữa."""
    status_changed = pyqtSignal(int, str)  # request_id, new_status
    delete_requested = pyqtSignal(int)

    def __init__(self, req: RepairRequest, extra: dict = None, parent=None):
        super().__init__(parent)
        self.req = req
        self.extra = extra or {}
        self.setWindowTitle(f"YC{req.id:03d}" if req.id else "Chi tiết")
        self.setFixedSize(450, 520)
        self.setStyleSheet("QDialog{background:white;} QLabel{color:#2d3748;}")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._build()

    def _box(self, label, value, color=None):
        f = QFrame()
        f.setStyleSheet("QFrame{background:#f7fafc;border:1px solid #e2e8f0;border-radius:8px;padding:10px;}")
        lo = QVBoxLayout(f); lo.setContentsMargins(0,0,0,0); lo.setSpacing(3)
        lb = QLabel(label); lb.setStyleSheet("color:#a0aec0;font-size:10px;font-weight:bold;border:none;background:transparent;")
        lo.addWidget(lb)
        if color:
            v = QLabel(f"● {value}"); v.setStyleSheet(f"color:{color};font-size:13px;font-weight:bold;border:none;background:transparent;")
        else:
            v = QLabel(str(value) if value else "—"); v.setStyleSheet("color:#2d3748;font-size:13px;font-weight:bold;border:none;background:transparent;")
        v.setWordWrap(True); lo.addWidget(v)
        return f

    def _section(self, text):
        lb = QLabel(text); lb.setStyleSheet("color:#718096;font-size:11px;font-weight:bold;letter-spacing:1px;")
        return lb

    def _build(self):
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:white;}")
        c = QWidget(); lo = QVBoxLayout(c); lo.setSpacing(8); lo.setContentsMargins(20,20,20,20)

        # Header
        h = QHBoxLayout()
        t = QLabel("🔧 Chi tiết yêu cầu"); t.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        h.addWidget(t); h.addStretch()
        bx = QPushButton("✕"); bx.setFixedSize(28,28)
        bx.setStyleSheet("QPushButton{background:transparent;border:none;font-size:16px;color:#a0aec0;}"
                          "QPushButton:hover{color:#e53e3e;}")
        bx.clicked.connect(self.accept); h.addWidget(bx); lo.addLayout(h)

        req = self.req
        STATUS_MAP = {'pending':('Chờ tiếp nhận','#dd6b20'),'in_progress':('Đang xử lý','#3182ce'),
                      'completed':('Hoàn thành','#38a169'),'cancelled':('Đã hủy','#a0aec0')}
        PRIORITY_MAP = {'low':('Thấp','#38a169'),'medium':('Bình thường','#3182ce'),
                        'urgent':('Khẩn cấp','#e53e3e'),'high':('Cao','#dd6b20')}

        st_text, st_color = STATUS_MAP.get(req.status, ('—','#718096'))
        pr_text, pr_color = PRIORITY_MAP.get(req.priority, ('—','#718096'))

        lo.addWidget(self._section("THÔNG TIN YÊU CẦU"))
        for row in [
            [("MÃ YC", f"YC{req.id:03d}" if req.id else "—"), ("DANH MỤC", req.title)],
            [("PHÒNG", self.extra.get('room_number','—')), ("KHÁCH THUÊ", self.extra.get('guest_name','—'))],
            [("ƯU TIÊN", pr_text), ("TRẠNG THÁI", st_text)],
        ]:
            r = QHBoxLayout(); r.setSpacing(8)
            for lb, vl in row:
                color = pr_color if lb == "ƯU TIÊN" else (st_color if lb == "TRẠNG THÁI" else None)
                r.addWidget(self._box(lb, vl, color=color))
            lo.addLayout(r)

        lo.addWidget(self._box("MÔ TẢ SỰ CỐ", req.description))

        lo.addWidget(self._section("THỜI GIAN"))
        created = req.created_at[:10] if req.created_at else '—'
        completed = req.completed_at[:10] if req.completed_at else '—'
        r = QHBoxLayout(); r.setSpacing(8)
        r.addWidget(self._box("NGÀY GỬI", created))
        r.addWidget(self._box("NGÀY HOÀN THÀNH", completed))
        lo.addLayout(r)

        lo.addStretch()

        # Action buttons based on status
        br = QHBoxLayout(); br.setSpacing(8)
        if req.status == 'pending':
            btn_accept = QPushButton("✅ Tiếp nhận")
            btn_accept.setStyleSheet("QPushButton{background:#38a169;color:white;border:none;border-radius:8px;padding:10px 16px;font-weight:bold;font-size:12px;}QPushButton:hover{background:#2f855a;}")
            btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_accept.clicked.connect(lambda: self._change_status('in_progress'))
            br.addWidget(btn_accept)
            btn_reject = QPushButton("❌ Từ chối")
            btn_reject.setStyleSheet("QPushButton{background:#e53e3e;color:white;border:none;border-radius:8px;padding:10px 16px;font-weight:bold;font-size:12px;}QPushButton:hover{background:#c53030;}")
            btn_reject.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_reject.clicked.connect(lambda: self._change_status('cancelled'))
            br.addWidget(btn_reject)
        elif req.status == 'in_progress':
            btn_done = QPushButton("✅ Hoàn thành")
            btn_done.setStyleSheet("QPushButton{background:#38a169;color:white;border:none;border-radius:8px;padding:10px 16px;font-weight:bold;font-size:12px;}QPushButton:hover{background:#2f855a;}")
            btn_done.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_done.clicked.connect(lambda: self._change_status('completed'))
            br.addWidget(btn_done)
            btn_reject = QPushButton("❌ Từ chối")
            btn_reject.setStyleSheet("QPushButton{background:#e53e3e;color:white;border:none;border-radius:8px;padding:10px 16px;font-weight:bold;font-size:12px;}QPushButton:hover{background:#c53030;}")
            btn_reject.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_reject.clicked.connect(lambda: self._change_status('cancelled'))
            br.addWidget(btn_reject)

        btn_del = QPushButton("🗑️ Xóa")
        btn_del.setStyleSheet("QPushButton{background:white;color:#e53e3e;border:1px solid #fed7d7;border-radius:8px;padding:10px 16px;font-weight:bold;font-size:12px;}QPushButton:hover{background:#fff5f5;}")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(self._on_delete)
        br.addWidget(btn_del)
        lo.addLayout(br)

        scroll.setWidget(c); outer.addWidget(scroll)

    def _change_status(self, new_status):
        self.status_changed.emit(self.req.id, new_status)
        self.accept()

    def _on_delete(self):
        if ask_question(self, "Xác nhận", f"Xóa yêu cầu YC{self.req.id:03d}?"):
            self.delete_requested.emit(self.req.id); self.accept()


# ── Create Request Dialog ────────────────────────────────
class RepairCreateDialog(QDialog):
    """Dialog tạo yêu cầu sửa chữa mới."""
    def __init__(self, guests_rooms=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("➕ Tiếp nhận yêu cầu")
        self.setFixedWidth(450)
        self.setStyleSheet("QDialog{background:white;} QLabel{color:#4a5568;font-weight:bold;font-size:11px;}")
        self.guests_rooms = guests_rooms or {}  # {guest_id: (name, room_number, room_id)}
        self._build()

    def _build(self):
        lo = QVBoxLayout(self); lo.setSpacing(12); lo.setContentsMargins(25,25,25,25)
        t = QLabel("➕ Tiếp nhận yêu cầu sửa chữa")
        t.setStyleSheet("font-size:16px;color:#2d3748;font-weight:bold;"); lo.addWidget(t)

        lo.addWidget(QLabel("KHÁCH THUÊ *"))
        self.cb_guest = QComboBox()
        self.cb_guest.setStyleSheet("QComboBox{background:white;border:1px solid #e2e8f0;border-radius:6px;padding:8px;font-size:13px;}")
        self.cb_guest.addItem("— Chọn khách —")
        for gid, (name, room_num, room_id) in self.guests_rooms.items():
            self.cb_guest.addItem(f"{name} — {room_num}", gid)
        lo.addWidget(self.cb_guest)

        lo.addWidget(QLabel("DANH MỤC *"))
        self.cb_category = QComboBox()
        self.cb_category.setStyleSheet("QComboBox{background:white;border:1px solid #e2e8f0;border-radius:6px;padding:8px;font-size:13px;}")
        self.cb_category.addItems(["Điện", "Nước", "Khóa cửa", "Điều hòa", "Tường/Trần", "Khác"])
        lo.addWidget(self.cb_category)

        lo.addWidget(QLabel("MỨC ĐỘ ƯU TIÊN *"))
        self.cb_priority = QComboBox()
        self.cb_priority.setStyleSheet("QComboBox{background:white;border:1px solid #e2e8f0;border-radius:6px;padding:8px;font-size:13px;}")
        self.cb_priority.addItems(["Bình thường", "Thấp", "Cao", "Khẩn cấp"])
        lo.addWidget(self.cb_priority)

        lo.addWidget(QLabel("MÔ TẢ SỰ CỐ *"))
        self.inp_desc = QTextEdit()
        self.inp_desc.setMaximumHeight(80)
        self.inp_desc.setStyleSheet("QTextEdit{background:white;border:1px solid #e2e8f0;border-radius:6px;padding:8px;font-size:13px;}")
        lo.addWidget(self.inp_desc)

        br = QHBoxLayout(); br.addStretch()
        btn_cancel = QPushButton("Hủy")
        btn_cancel.setStyleSheet("QPushButton{background:#f7fafc;border:1px solid #e2e8f0;border-radius:6px;color:#4a5568;font-weight:bold;padding:10px 20px;}")
        btn_cancel.clicked.connect(self.reject); br.addWidget(btn_cancel)
        btn_save = QPushButton("💾 Lưu yêu cầu")
        btn_save.setStyleSheet("QPushButton{background:#0b8480;border:none;border-radius:6px;color:white;font-weight:bold;padding:10px 20px;}")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self._on_save); br.addWidget(btn_save)
        lo.addLayout(br)

    def _on_save(self):
        if self.cb_guest.currentIndex() == 0:
            show_warning(self, "Lỗi", "Vui lòng chọn khách thuê"); return
        if not self.inp_desc.toPlainText().strip():
            show_warning(self, "Lỗi", "Vui lòng mô tả sự cố"); return

        guest_id = self.cb_guest.currentData()
        info = self.guests_rooms.get(guest_id, ('','',''))
        priority_map = {"Bình thường":"medium","Thấp":"low","Cao":"high","Khẩn cấp":"urgent"}
        self.result_data = {
            'guest_id': guest_id,
            'room_id': info[2],
            'title': self.cb_category.currentText(),
            'description': self.inp_desc.toPlainText().strip(),
            'priority': priority_map.get(self.cb_priority.currentText(), 'medium'),
        }
        self.accept()


# ── Main View ────────────────────────────────────────────
class RepairManagementView(QWidget):
    """Widget quản lý yêu cầu sửa chữa — nhúng vào AdminWindow."""

    HEADERS = ["Mã YC", "Phòng", "Khách thuê", "Danh mục", "Mô tả sự cố",
               "Ưu tiên", "Ngày gửi", "Trạng thái", "Thao tác"]

    STATUS_COLORS = {
        'pending': ('⏳ Chờ tiếp nhận', '#dd6b20'),
        'in_progress': ('🔧 Đang xử lý', '#3182ce'),
        'completed': ('✅ Hoàn thành', '#38a169'),
        'cancelled': ('✕ Đã hủy', '#a0aec0'),
    }
    PRIORITY_COLORS = {
        'low': ('Thấp', '#38a169'), 'medium': ('Bình thường', '#3182ce'),
        'high': ('Cao', '#dd6b20'), 'urgent': ('Khẩn cấp', '#e53e3e'),
    }
    CATEGORIES = ["Tất cả", "Điện", "Nước", "Khóa cửa", "Điều hòa", "Tường/Trần", "Khác"]

    def __init__(self, repair_service=None, guest_service=None, room_service=None,
                 contract_service=None, parent=None):
        super().__init__(parent)
        self.repair_service = repair_service
        self.guest_service = guest_service
        self.room_service = room_service
        self.contract_service = contract_service
        self._active_category = "Tất cả"
        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        main = QVBoxLayout(self); main.setContentsMargins(20,15,20,15); main.setSpacing(12)

        # Stats
        stats = QHBoxLayout(); stats.setSpacing(15)
        self.card_total = RepairStatCard("📋", "0", "Tổng yêu cầu", "#ebf8ff")
        self.card_pending = RepairStatCard("⏳", "0", "Chờ tiếp nhận", "#fffaf0", "#dd6b20")
        self.card_progress = RepairStatCard("🔧", "0", "Đang xử lý", "#ebf8ff", "#3182ce")
        self.card_done = RepairStatCard("✅", "0", "Hoàn thành", "#e6fffa", "#38a169")
        for c in [self.card_total, self.card_pending, self.card_progress, self.card_done]:
            stats.addWidget(c)
        main.addLayout(stats)

        # Category filter tabs
        cat_row = QHBoxLayout(); cat_row.setSpacing(4)
        self._cat_buttons = []
        for cat in self.CATEGORIES:
            btn = QPushButton(cat)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setChecked(cat == "Tất cả")
            btn.clicked.connect(lambda _, c=cat: self._on_category(c))
            self._cat_buttons.append(btn)
            cat_row.addWidget(btn)
        self._update_cat_styles()
        cat_row.addStretch()

        self.filter_status = QComboBox()
        self.filter_status.addItems(["Tất cả trạng thái", "Chờ tiếp nhận", "Đang xử lý", "Hoàn thành", "Đã hủy"])
        self.filter_status.setStyleSheet("QComboBox{background:#f7fafc;border:1px solid #e2e8f0;border-radius:8px;padding:8px 12px;font-size:13px;}")
        self.filter_status.currentIndexChanged.connect(lambda: self.refresh_data())
        cat_row.addWidget(self.filter_status)
        main.addLayout(cat_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(0, 65)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(1, 55)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(8, 70)
        for col in range(2, 8):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { background-color:white; border:1px solid #e2e8f0; border-radius:8px;
                           gridline-color:#edf2f7; font-size:12px; }
            QTableWidget::item { padding:4px; }
            QTableWidget::item:alternate { background-color:#f7fafc; }
            QHeaderView::section { background-color:#f7fafc; color:#718096; font-weight:bold;
                                   border:none; padding:8px 4px; font-size:11px; }
        """)
        main.addWidget(self.table, 1)

        self.lbl_count = QLabel("Hiển thị 0 yêu cầu")
        self.lbl_count.setStyleSheet("color:#a0aec0;font-size:12px;")
        main.addWidget(self.lbl_count)

    def _update_cat_styles(self):
        for btn in self._cat_buttons:
            if btn.text() == self._active_category:
                btn.setStyleSheet("QPushButton{background:#0b8480;color:white;border:none;border-radius:6px;padding:6px 14px;font-weight:bold;font-size:12px;}")
            else:
                btn.setStyleSheet("QPushButton{background:#f7fafc;color:#4a5568;border:1px solid #e2e8f0;border-radius:6px;padding:6px 14px;font-size:12px;}QPushButton:hover{background:#edf2f7;}")

    def _on_category(self, cat):
        self._active_category = cat
        self._update_cat_styles()
        self.refresh_data()

    # ── Data ──
    def _build_lookup(self):
        self._guests_by_id = {}
        self._rooms_by_id = {}
        self._guests_rooms = {}  # guest_id -> (name, room_number, room_id)
        if self.guest_service:
            try:
                for g in self.guest_service.get_all_guests():
                    self._guests_by_id[g.id] = g
            except: pass
        if self.room_service:
            try:
                for r in self.room_service.get_all_rooms():
                    self._rooms_by_id[r.id] = r
            except: pass
        # Map guest -> room via contracts
        if self.contract_service:
            try:
                for c in self.contract_service.get_all():
                    if c.is_active():
                        guest = self._guests_by_id.get(c.guest_id)
                        room = self._rooms_by_id.get(c.room_id)
                        if guest:
                            self._guests_rooms[guest.id] = (
                                guest.full_name,
                                room.room_number if room else f"P{c.room_id}",
                                c.room_id
                            )
            except: pass

    def refresh_data(self):
        if not self.repair_service: return
        self._build_lookup()
        reqs = self.repair_service.get_all()

        # Category filter
        if self._active_category != "Tất cả":
            reqs = [r for r in reqs if r.title == self._active_category]

        # Status filter
        status_map = {1:'pending', 2:'in_progress', 3:'completed', 4:'cancelled'}
        sf = status_map.get(self.filter_status.currentIndex())
        if sf:
            reqs = [r for r in reqs if r.status == sf]

        # Stats
        all_reqs = self.repair_service.get_all()
        self.card_total.val_lbl.setText(str(len(all_reqs)))
        self.card_pending.val_lbl.setText(str(sum(1 for r in all_reqs if r.status == 'pending')))
        self.card_progress.val_lbl.setText(str(sum(1 for r in all_reqs if r.status == 'in_progress')))
        self.card_done.val_lbl.setText(str(sum(1 for r in all_reqs if r.status == 'completed')))

        # Table
        self.table.setRowCount(len(reqs))
        for i, req in enumerate(reqs):
            self.table.setRowHeight(i, 50)
            guest = self._guests_by_id.get(req.guest_id)
            room = self._rooms_by_id.get(req.room_id)
            guest_name = guest.full_name if guest else f"KT{req.guest_id:03d}"
            room_num = room.room_number if room else f"P{req.room_id}"

            self.table.setItem(i, 0, QTableWidgetItem(f"YC{req.id:03d}" if req.id else "—"))
            self.table.setItem(i, 1, QTableWidgetItem(room_num))

            # Guest name
            name_item = QTableWidgetItem(guest_name)
            name_item.setToolTip(guest_name)
            self.table.setItem(i, 2, name_item)

            self.table.setItem(i, 3, QTableWidgetItem(req.title))

            desc_item = QTableWidgetItem(req.description[:40] + "..." if len(req.description) > 40 else req.description)
            desc_item.setToolTip(req.description)
            self.table.setItem(i, 4, desc_item)

            # Priority
            pr_text, pr_color = self.PRIORITY_COLORS.get(req.priority, ('—','#718096'))
            pr_lbl = QLabel(pr_text)
            pr_lbl.setStyleSheet(f"color:{pr_color};font-weight:bold;font-size:11px;background:transparent;")
            pr_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(i, 5, pr_lbl)

            # Date
            created = req.created_at[:10] if req.created_at else '—'
            self.table.setItem(i, 6, QTableWidgetItem(created))

            # Status
            st_text, st_color = self.STATUS_COLORS.get(req.status, ('—','#718096'))
            st_lbl = QLabel(st_text)
            st_lbl.setStyleSheet(f"color:{st_color};font-weight:bold;font-size:10px;background:transparent;")
            st_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(i, 7, st_lbl)

            # Actions
            actions = QWidget(); actions.setStyleSheet("background:transparent;")
            al = QHBoxLayout(actions); al.setContentsMargins(2,2,2,2)
            btn = QPushButton("Chi tiết")
            btn.setStyleSheet("QPushButton{background:#ebf8ff;color:#3182ce;border:none;border-radius:4px;padding:4px 6px;font-weight:bold;font-size:10px;}QPushButton:hover{background:#bee3f8;}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor); btn.setFixedHeight(24)
            btn.clicked.connect(lambda _, r=req: self._on_detail(r))
            al.addWidget(btn)
            self.table.setCellWidget(i, 8, actions)

        self.lbl_count.setText(f"Hiển thị {len(reqs)}/{len(all_reqs)} yêu cầu")

    # ── CRUD ──
    def _on_add(self):
        self._build_lookup()
        dlg = RepairCreateDialog(guests_rooms=self._guests_rooms, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.result_data
            ok, msg = self.repair_service.create_request(
                guest_id=data['guest_id'], room_id=data['room_id'],
                title=data['title'], description=data['description'],
                priority=data['priority'])
            if ok:
                show_success(self, "Thành công", msg)
                self.refresh_data()
            else:
                show_warning(self, "Lỗi", msg)

    def _on_detail(self, req):
        guest = self._guests_by_id.get(req.guest_id)
        room = self._rooms_by_id.get(req.room_id)
        dlg = RepairDetailDialog(req, extra={
            'guest_name': guest.full_name if guest else '—',
            'room_number': room.room_number if room else '—',
        }, parent=self)
        dlg.status_changed.connect(self._on_status_change)
        dlg.delete_requested.connect(self._on_delete)
        dlg.exec()

    def _on_status_change(self, req_id, new_status):
        ok, msg = self.repair_service.update_status(req_id, new_status)
        if ok:
            show_success(self, "Thành công", msg)
            self.refresh_data()
        else:
            show_warning(self, "Lỗi", msg)

    def _on_delete(self, req_id):
        ok = self.repair_service.repair_repo.delete(req_id)
        if ok:
            show_success(self, "Thành công", "Xóa yêu cầu thành công")
            self.refresh_data()
        else:
            show_warning(self, "Lỗi", "Không thể xóa")
