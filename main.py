"""
main.py
=======
Khởi chạy ứng dụng Quản lý Công thức Nấu ăn.
  - Mặc định: Mở giao diện GUI
"""

import sys
from utils.logger import setup_logger

__version__ = "1.0.0"
logger = setup_logger("main")

# Ép console UTF-8
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

if __name__ == "__main__":
    logger.info(f"=== Khởi chạy Quản lý Công thức Nấu ăn v{__version__} ===")
    from controllers import gui_controller_congthuc
    gui_controller_congthuc.chay_ung_dung()
