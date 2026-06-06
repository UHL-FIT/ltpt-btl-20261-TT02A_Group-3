"""
main_api.py
===========
Khởi chạy ứng dụng dưới dạng Web API Server.
Tập tin này là "Entry Point" dành riêng cho máy chủ API.
Khi chạy file này, một Web Server cục bộ sẽ khởi động tại cổng 5000.

Cách chạy:
  .venv\\Scripts\\activate
  python main_api.py
"""

import sys
from utils.logger import setup_logger

# Thiết lập phiên bản
__version__ = "1.0.0"

# Khởi tạo logger riêng cho file khởi chạy API
logger = setup_logger("main_api")

# Ép console dùng UTF-8 đề phòng lỗi hiển thị trên Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

if __name__ == "__main__":
    logger.info(f"=== Khởi chạy Web API Server v{__version__} ===")
    
    # Import api_controller
    from controllers.api_controller import chay_api
    
    # Khởi chạy API server trên cổng 5000
    try:
        chay_api(host="127.0.0.1", port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("Máy chủ API đã dừng theo yêu cầu của người dùng.")
    except Exception as e:
        logger.error(f"Lỗi khi chạy máy chủ API: {e}")
