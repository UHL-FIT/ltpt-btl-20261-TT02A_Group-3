"""
main.py
=======
Khởi chạy ứng dụng Quản lý Công thức Nấu ăn.
  - Mặc định: Mở giao diện đồ họa người dùng (GUI)

Tập tin này đóng vai trò là "điểm xuất phát" (Entry Point) của chương trình.
Khi bạn bấm chạy dự án, Python sẽ đọc và thực thi tệp này đầu tiên.
"""

import sys  # Thư viện hệ thống của Python, dùng để tương tác với môi trường chạy (như console, argument, encode...)
from utils.logger import setup_logger  # Nhập hàm cấu hình ghi log từ thư mục utils

# Định nghĩa phiên bản hiện tại của ứng dụng
__version__ = "1.0.0"

# Khởi tạo một đối tượng logger có tên là "main" để ghi nhật ký hoạt động cho file này.
logger = setup_logger("main")

# =========================================================================
# PHẦN XỬ LÝ ĐẶC BIỆT: ÉP ĐỊNH DẠNG CONSOLE THÀNH UTF-8
# =========================================================================
# Lập trình viên mới thường gặp lỗi hiển thị tiếng Việt (UnicodeEncodeError) 
# khi chạy ứng dụng terminal hoặc đóng gói thành file .exe trên Windows.
# Đoạn mã dưới đây kiểm tra xem cổng xuất dữ liệu (sys.stdout/sys.stderr) có hỗ trợ
# việc định cấu hình lại (reconfigure) hay không. Nếu có, nó sẽ ép hệ thống dùng UTF-8.
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Ép luồng đầu ra tiêu chuẩn (in ra màn hình) dùng UTF-8
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")  # Ép luồng báo lỗi tiêu chuẩn dùng UTF-8

# =========================================================================
# KHỐI LỆNH KHỞI CHẠY CHÍNH (MAIN BLOCK)
# =========================================================================
# Dòng lệnh dưới đây có nghĩa: "Nếu file này được chạy trực tiếp bằng lệnh python main.py"
# chứ không phải bị import từ một file khác, thì mới thực hiện các lệnh bên dưới.
if __name__ == "__main__":
    # Ghi lại dấu mốc khởi động ứng dụng vào cả file log và màn hình console
    logger.info(f"=== Khởi chạy Quản lý Công thức Nấu ăn v{__version__} ===")
    
    # Import Controller (gui_controller_congthuc) tại đây nhằm tối ưu hóa bộ nhớ:
    # Chỉ nạp controller và giao diện đồ họa Tkinter khi chương trình thực sự bắt đầu chạy.
    from controllers import gui_controller_congthuc
    
    # Gọi hàm khởi chạy vòng lặp sự kiện chính của giao diện đồ họa (GUI Event Loop)
    gui_controller_congthuc.chay_ung_dung()
