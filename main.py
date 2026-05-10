"""
main.py
=======
Khởi chạy ứng dụng.
  - Mặc định (không tham số): Quản lý Công thức Nấu ăn (GUI)
  - --diemdanh              : SmartAttend (GUI gốc)
  - --cli                   : Giao diện dòng lệnh
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
    args = sys.argv[1:]

    if "--cli" in args:
        logger.info("Chạy chế độ CLI.")
        from controllers import cli_controller
        cli_controller.chay_ung_dung()

    elif "--diemdanh" in args:
        logger.info("Chạy SmartAttend (điểm danh) GUI.")
        from controllers import gui_controller
        gui_controller.chay_ung_dung()

    else:
        logger.info(f"=== Khởi chạy Quản lý Công thức Nấu ăn v{__version__} ===")
        from controllers import gui_controller_congthuc
        gui_controller_congthuc.chay_ung_dung()
