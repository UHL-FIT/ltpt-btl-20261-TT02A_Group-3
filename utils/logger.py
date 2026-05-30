"""
utils/logger.py
===============
Cấu hình ghi nhật ký (logging) cho toàn bộ ứng dụng.
Ghi log chi tiết ra file (data/app.log) và hiển thị cảnh báo trên console (chỉ các lỗi từ WARNING trở lên).

Ghi chú cho người mới: Logging là kỹ thuật cực kỳ quan trọng giúp theo dõi hoạt động 
và bắt lỗi của phần mềm mà không cần lạm dụng lệnh print(). Khi ứng dụng chạy thực tế,
lệnh print() sẽ không lưu lại được, nhưng Logging thì ghi trực tiếp vào file cứng!
"""

import os      # Thư viện tương tác với hệ thống tệp và thư mục (tạo thư mục, nối đường dẫn...)
import sys     # Thư viện hệ thống của Python
import logging # Thư viện ghi log tiêu chuẩn của Python

# =========================================================================
# XÁC ĐỊNH THƯ MỤC LƯU TRỮ DỮ LIỆU ĐỂ TRÁNH LỖI PHÂN QUYỀN
# =========================================================================
# Khi đóng gói ứng dụng bằng PyInstaller (thành file .exe chạy độc lập):
# - sys.frozen sẽ có giá trị là True.
# - Nếu người dùng cài ứng dụng vào thư mục hệ thống (như C:\Program Files), ứng dụng sẽ
#   không có quyền ghi file (Write Permission) trực tiếp tại thư mục đó.
# - Giải pháp: Sử dụng thư mục người dùng cá nhân (User Profile Directory - ký hiệu là "~")
#   để tạo một thư mục ghi dữ liệu an toàn tên là "SmartAttend_Data".
if getattr(sys, 'frozen', False):
    # Đường dẫn lưu dữ liệu: C:\Users\<Tên_User>\SmartAttend_Data
    _BASE_DIR = os.path.join(os.path.expanduser("~"), "SmartAttend_Data")
else:
    # Nếu chạy mã nguồn Python thông thường (.py): 
    # Lấy đường dẫn cha của thư mục chứa file này (thư mục gốc của project)
    _BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Xác định đường dẫn thư mục lưu log: thư mục "data" nằm bên trong thư mục gốc
_LOG_DIR = os.path.join(_BASE_DIR, "data")
# Xác định đường dẫn file log cụ thể: data/app.log
_LOG_FILE = os.path.join(_LOG_DIR, "app.log")


def setup_logger(name="qlsv"):
    """
    Tạo, thiết lập cấu hình và trả về đối tượng Logger.
    
    Tham số:
      - name (str): Tên phân vùng ghi log (giúp phân biệt log này xuất phát từ file nào). Mặc định là "qlsv".
      
    Cách thiết lập:
      - File handler: Ghi TẤT CẢ các cấp độ log (từ DEBUG trở lên) vào file data/app.log để lập trình viên xem lại.
      - Console handler: Chỉ hiển thị các cảnh báo nghiêm trọng (từ WARNING trở lên) ra terminal màn hình.
    """
    # Tạo thư mục chứa log (thư mục data) nếu nó chưa tồn tại trên ổ cứng. 
    # exist_ok=True nghĩa là nếu thư mục đã có sẵn thì bỏ qua, không báo lỗi.
    os.makedirs(_LOG_DIR, exist_ok=True)

    # Lấy đối tượng logger theo tên truyền vào
    logger = logging.getLogger(name)

    # TRÁNH TRÙNG HÀNDLER:
    # Nếu hàm setup_logger được gọi nhiều lần trên cùng một logger, Python có thể tự động
    # thêm trùng các bộ ghi log (handlers), dẫn đến việc 1 dòng log bị ghi lặp lại nhiều lần.
    # Kiểm tra: nếu logger này đã được cấu hình trước đó rồi (đã có handlers), trả về luôn.
    if logger.handlers:
        return logger

    # Thiết lập cấp độ log cơ sở thấp nhất là DEBUG (cho phép thu thập tất cả các loại log)
    logger.setLevel(logging.DEBUG)

    # ─── 1. FILE HANDLER (Bộ ghi log ra file cứng) ───
    # Sử dụng FileHandler để ghi log trực tiếp vào đường dẫn file cấu hình.
    # encoding="utf-8" cực kỳ quan trọng để lưu được tiếng Việt không bị lỗi font ký tự lạ.
    fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)  # File log sẽ ghi tất cả từ DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Định dạng chuỗi log lưu vào file:
    # - %(asctime)s: Thời gian xảy ra sự kiện (năm-tháng-ngày giờ:phút:giây)
    # - %(levelname)-8s: Cấp độ log (INFO, DEBUG...), căn lề trái tối đa 8 ký tự
    # - %(module)s.%(funcName)s: Tên file code và tên hàm phát sinh log này
    # - %(message)s: Nội dung thông điệp log
    fmt_file = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(module)s.%(funcName)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(fmt_file)  # Gán định dạng này vào File Handler

    # ─── 2. CONSOLE HANDLER (Bộ in log ra terminal) ───
    # Sử dụng StreamHandler để xuất log ra màn hình console của lập trình viên.
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)  # Chỉ hiển thị log từ mức WARNING trở lên (như cảnh báo lỗi, crash ứng dụng)
    
    # Định dạng log trên console: Ngắn gọn, có icon cảnh báo dễ quan sát
    fmt_console = logging.Formatter("  ⚠️ [%(levelname)s] %(message)s")
    ch.setFormatter(fmt_console)  # Gán định dạng này vào Console Handler

    # Đăng ký (add) cả hai bộ ghi log trên vào đối tượng logger chính
    logger.addHandler(fh)
    logger.addHandler(ch)

    # Trả về đối tượng logger đã được cấu hình hoàn chỉnh
    return logger
