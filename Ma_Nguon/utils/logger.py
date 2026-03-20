"""Logger — Ghi log hệ thống."""
import logging
import os
from config.constants import BASE_DIR


def setup_logger(name: str = 'app', log_file: str = 'app.log') -> logging.Logger:
    """Tạo logger với cả console và file output."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # File handler
    log_path = os.path.join(str(BASE_DIR), log_file)
    fh = logging.FileHandler(log_path, encoding='utf-8')
    fh.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    # Format
    fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
