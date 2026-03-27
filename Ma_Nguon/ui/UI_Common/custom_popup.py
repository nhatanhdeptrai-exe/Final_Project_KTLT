
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor


# ── Style constants ──
_OVERLAY = "QDialog { background-color: white; border-radius: 16px; }"

_BTN_OK = (
    "QPushButton { background-color: #0b8480; color: white; border: none; "
    "border-radius: 8px; padding: 10px 28px; font-weight: bold; font-size: 13px; }"
    "QPushButton:hover { background-color: #097a76; }"
)

_BTN_DANGER = (
    "QPushButton { background-color: #e53e3e; color: white; border: none; "
    "border-radius: 8px; padding: 10px 28px; font-weight: bold; font-size: 13px; }"
    "QPushButton:hover { background-color: #c53030; }"
)

_BTN_CANCEL = (
    "QPushButton { background-color: #f7fafc; color: #4a5568; "
    "border: 1px solid #cbd5e0; border-radius: 8px; padding: 10px 28px; "
    "font-weight: bold; font-size: 13px; }"
    "QPushButton:hover { background-color: #edf2f7; }"
)

# Icon + color mapping
_TYPE_CONFIG = {
    "success": {"icon": "✅", "color": "#38a169"},
    "error":   {"icon": "❌", "color": "#e53e3e"},
    "warning": {"icon": "⚠️", "color": "#dd6b20"},
    "info":    {"icon": "ℹ️", "color": "#3182ce"},
    "question":{"icon": "❓", "color": "#805ad5"},
}


def _build_dialog(parent, title: str, message: str, msg_type: str = "info",
                  width: int = 400, height: int = 220) -> QDialog:
    """Tạo dialog cơ bản với icon, tiêu đề, và nội dung."""
    cfg = _TYPE_CONFIG.get(msg_type, _TYPE_CONFIG["info"])

    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.setFixedSize(width, height)
    dlg.setStyleSheet(_OVERLAY)

    lay = QVBoxLayout(dlg)
    lay.setSpacing(8)
    lay.setContentsMargins(30, 25, 30, 25)

    # Icon
    icon = QLabel(cfg["icon"])
    icon.setStyleSheet("font-size: 42px; background: transparent;")
    icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lay.addWidget(icon)

    # Title
    lbl_title = QLabel(title)
    lbl_title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
    lbl_title.setStyleSheet(f"color: {cfg['color']}; background: transparent;")
    lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl_title.setWordWrap(True)
    lay.addWidget(lbl_title)

    # Message
    lbl_msg = QLabel(message)
    lbl_msg.setStyleSheet("color: #4a5568; font-size: 13px; background: transparent;")
    lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl_msg.setWordWrap(True)
    lay.addWidget(lbl_msg)

    lay.addStretch()

    return dlg, lay


def show_success(parent, title: str, message: str):
    """Hiện popup thành công (chỉ nút OK)."""
    dlg, lay = _build_dialog(parent, title, message, "success")

    btn = QPushButton("OK")
    btn.setMinimumHeight(40)
    btn.setStyleSheet(_BTN_OK)
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.clicked.connect(dlg.accept)

    row = QHBoxLayout()
    row.addStretch()
    row.addWidget(btn)
    row.addStretch()
    lay.addLayout(row)

    dlg.exec()


def show_error(parent, title: str, message: str):
    """Hiện popup lỗi (chỉ nút OK)."""
    dlg, lay = _build_dialog(parent, title, message, "error")

    btn = QPushButton("OK")
    btn.setMinimumHeight(40)
    btn.setStyleSheet(_BTN_DANGER)
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.clicked.connect(dlg.accept)

    row = QHBoxLayout()
    row.addStretch()
    row.addWidget(btn)
    row.addStretch()
    lay.addLayout(row)

    dlg.exec()


def show_warning(parent, title: str, message: str):
    """Hiện popup cảnh báo (chỉ nút OK)."""
    dlg, lay = _build_dialog(parent, title, message, "warning")

    btn = QPushButton("OK")
    btn.setMinimumHeight(40)
    btn.setStyleSheet(_BTN_OK)
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.clicked.connect(dlg.accept)

    row = QHBoxLayout()
    row.addStretch()
    row.addWidget(btn)
    row.addStretch()
    lay.addLayout(row)

    dlg.exec()


def show_info(parent, title: str, message: str):
    """Hiện popup thông tin (chỉ nút OK)."""
    dlg, lay = _build_dialog(parent, title, message, "info")

    btn = QPushButton("OK")
    btn.setMinimumHeight(40)
    btn.setStyleSheet(_BTN_OK)
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.clicked.connect(dlg.accept)

    row = QHBoxLayout()
    row.addStretch()
    row.addWidget(btn)
    row.addStretch()
    lay.addLayout(row)

    dlg.exec()


def ask_question(parent, title: str, message: str,
                 yes_text: str = "Đồng ý", no_text: str = "Hủy bỏ") -> bool:
    """Hiện popup xác nhận với 2 nút Yes/No. Trả về True nếu chọn Yes."""
    dlg, lay = _build_dialog(parent, title, message, "question", height=230)

    row = QHBoxLayout()
    row.setSpacing(12)

    btn_no = QPushButton(no_text)
    btn_no.setMinimumHeight(40)
    btn_no.setStyleSheet(_BTN_CANCEL)
    btn_no.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn_no.clicked.connect(dlg.reject)

    btn_yes = QPushButton(yes_text)
    btn_yes.setMinimumHeight(40)
    btn_yes.setStyleSheet(_BTN_OK)
    btn_yes.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn_yes.clicked.connect(dlg.accept)

    row.addWidget(btn_no)
    row.addWidget(btn_yes)
    lay.addLayout(row)

    return dlg.exec() == QDialog.DialogCode.Accepted


def ask_danger(parent, title: str, message: str,
               yes_text: str = "Xóa", no_text: str = "Hủy bỏ") -> bool:
    """Hiện popup xác nhận nguy hiểm (nút đỏ). Trả về True nếu chọn Yes."""
    dlg, lay = _build_dialog(parent, title, message, "error", height=230)

    row = QHBoxLayout()
    row.setSpacing(12)

    btn_no = QPushButton(no_text)
    btn_no.setMinimumHeight(40)
    btn_no.setStyleSheet(_BTN_CANCEL)
    btn_no.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn_no.clicked.connect(dlg.reject)

    btn_yes = QPushButton(yes_text)
    btn_yes.setMinimumHeight(40)
    btn_yes.setStyleSheet(_BTN_DANGER)
    btn_yes.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn_yes.clicked.connect(dlg.accept)

    row.addWidget(btn_no)
    row.addWidget(btn_yes)
    lay.addLayout(row)

    return dlg.exec() == QDialog.DialogCode.Accepted
