
import json
import os

from config.constants import BASE_DIR

BANK_INFO_FILE = os.path.join(BASE_DIR, 'data', 'bank_info.json')
QR_IMAGE_PATH = os.path.join(BASE_DIR, 'data', 'qr_payment.png')


def load_bank_info() -> dict:
    """Đọc thông tin ngân hàng đã lưu trả về dict rỗng nếu chưa có"""
    if os.path.exists(BANK_INFO_FILE):
        try:
            with open(BANK_INFO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_bank_info(data: dict) -> None:
    """Lưu thông tin ngân hàng vào file JSON"""
    os.makedirs(os.path.dirname(BANK_INFO_FILE), exist_ok=True)
    with open(BANK_INFO_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_qr_path() -> str:
    """Trả về đường dẫn ảnh QR nếu tồn tại, ngược lại trả về """
    return QR_IMAGE_PATH if os.path.exists(QR_IMAGE_PATH) else ''
