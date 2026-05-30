"""
models/congthuc.py
==================
Model quản lý Công thức Nấu ăn bằng SQLite3.
Sử dụng SQLite3 để lưu trữ dữ liệu bền vững (thay cho tệp CSV cũ),
đồng thời kết hợp thư viện Pandas và NumPy để xử lý, tính toán và trả kết quả về cho Controller.

Ghi chú :
- Model chịu trách nhiệm làm việc trực tiếp với dữ liệu (Database). Nó KHÔNG quan tâm
  giao diện hiển thị thế nào (View) hay người dùng bấm nút gì (Controller).
- SQLite3 là một hệ quản trị cơ sở dữ liệu quan hệ siêu nhẹ, lưu toàn bộ dữ liệu vào một file duy nhất trên ổ cứng.
- Pandas (pd) giúp quản lý bảng dữ liệu dưới dạng DataFrame (giống như bảng Excel trong bộ nhớ RAM).
- NumPy (np) dùng để xử lý các phép toán và mảng số học tốc độ cao cực kỳ mạnh mẽ.
"""

import os            # Thư viện quản lý tệp và thư mục hệ thống
import sqlite3       # Thư viện kết nối và thao tác với cơ sở dữ liệu SQLite3
import pandas as pd  # Thư viện xử lý phân tích dữ liệu dạng bảng
import numpy as np   # Thư viện tính toán số học trên mảng dữ liệu lớn
from utils.logger import setup_logger # Nhập hàm cấu hình ghi log

# Khởi tạo bộ ghi log riêng cho phân vùng Model
logger = setup_logger("congthuc")

# ─── ĐƯỜNG DẪN FILE DATABASE ─────────────────────────────────────────────
# Lấy đường dẫn thư mục gốc của project (nơi chứa file main.py)
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# Xác định file database lưu trữ dữ liệu nấu ăn tại: data/congthuc.db
FILE_DB = os.path.join(_BASE_DIR, "data", "congthuc.db")

# ─── DANH SÁCH LOẠI MÓN ĂN (DÙNG ĐỂ KHỞI TẠO VÀ LỌC) ──────────────────────
LOAI_MON_LIST = ["Khai vị", "Món chính", "Tráng miệng", "Đồ uống", "Khác"]

# ─── DANH SÁCH CỘT CỦA BẢNG ──────────────────────────────────────────────
# Dùng để đồng bộ định dạng dữ liệu trả về cho View giống hệt phiên bản CSV cũ, tránh lỗi giao diện
COLS_DB = ["ten_mon", "loai_mon", "nguyen_lieu", "dinh_luong", "thoi_gian", "cach_lam", "hinh_anh", "luu_y"]


def khoi_tao_db():
    """
    Tạo cơ sở dữ liệu và bảng 'congthuc' nếu chúng chưa tồn tại trên ổ cứng.
    Đồng thời tự động chuyển đổi dữ liệu (Migration) từ file CSV cũ sang Database
    nếu người dùng chạy ứng dụng lần đầu tiên.
    """
    # 1. Tạo thư mục chứa file Database (thư mục data) nếu chưa có
    os.makedirs(os.path.dirname(FILE_DB), exist_ok=True)
    
    # Kiểm tra xem file database đã tồn tại từ trước hay chưa
    db_exists = os.path.exists(FILE_DB)
    
    # Kết nối tới SQLite Database (nếu file chưa có, SQLite sẽ tự động tạo file trống mới)
    conn = sqlite3.connect(FILE_DB)
    try:
        cursor = conn.cursor()  # Tạo đối tượng con trỏ (cursor) để thực thi các câu lệnh SQL
        
        # 2. Tạo bảng 'congthuc' nếu bảng này chưa tồn tại
        # Các kiểu dữ liệu cơ bản trong SQLite:
        # - INTEGER: Số nguyên (dùng cho ID tự tăng, thời gian chuẩn bị)
        # - TEXT: Chuỗi văn bản (tên món, cách làm, nguyên liệu...)
        # - PRIMARY KEY AUTOINCREMENT: Khóa chính tự động tăng giá trị khi thêm mới dòng
        # - UNIQUE NOT NULL: Bắt buộc phải có dữ liệu và không được phép trùng lặp tên món ăn
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS congthuc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten_mon TEXT UNIQUE NOT NULL,
                loai_mon TEXT NOT NULL,
                nguyen_lieu TEXT,
                dinh_luong TEXT,
                thoi_gian INTEGER DEFAULT 0,
                cach_lam TEXT DEFAULT '',
                hinh_anh TEXT DEFAULT '',
                luu_y TEXT DEFAULT ''
            )
        ''')
        
        # 3. AUTO-MIGRATION (Cập nhật cấu trúc bảng cho phiên bản cũ):
        # Nếu người dùng có sẵn file database từ phiên bản cũ thiếu các cột như "cach_lam",
        # "hinh_anh", "luu_y" thì đoạn code bên dưới sẽ dùng câu lệnh 'ALTER TABLE'
        # để thêm cột tự động mà không làm mất dữ liệu cũ của họ.
        try:
            cursor.execute('ALTER TABLE congthuc ADD COLUMN cach_lam TEXT DEFAULT ""')
        except sqlite3.OperationalError:
            pass # Lỗi xảy ra nếu cột đã tồn tại từ trước -> Bỏ qua an toàn!
            
        try:
            cursor.execute('ALTER TABLE congthuc ADD COLUMN hinh_anh TEXT DEFAULT ""')
        except sqlite3.OperationalError:
            pass # Cột đã tồn tại -> Bỏ qua
            
        try:
            cursor.execute('ALTER TABLE congthuc ADD COLUMN luu_y TEXT DEFAULT ""')
        except sqlite3.OperationalError:
            pass # Cột đã tồn tại -> Bỏ qua

        conn.commit()  # Xác nhận lưu các thay đổi cấu trúc bảng vào DB
        
        # 4. CHUYỂN DỮ LIỆU TỪ FILE CSV CŨ SANG DB (Chạy duy nhất 1 lần khi khởi tạo DB mới):
        csv_file = os.path.join(os.path.dirname(FILE_DB), "congthuc.csv")
        if not db_exists and os.path.exists(csv_file):
            try:
                # Đọc file CSV bằng thư viện Pandas, mã hóa tiếng Việt "utf-8-sig"
                # dtype=str đảm bảo đọc tất cả dữ liệu dưới dạng chữ để xử lý lỗi giá trị rỗng dễ hơn
                df_csv = pd.read_csv(csv_file, encoding="utf-8-sig", dtype=str)
                
                # Duyệt từng dòng dữ liệu trong file CSV cũ
                for _, row in df_csv.iterrows():
                    try:
                        # Xử lý giá trị thời gian an toàn
                        thoi_gian_val = row.get("thoi_gian", 0)
                        if pd.isna(thoi_gian_val) or str(thoi_gian_val).strip() == "":
                            thoi_gian_val = 0
                        
                        # Chèn dữ liệu từ dòng CSV vào bảng SQLite
                        cursor.execute('''
                            INSERT INTO congthuc (ten_mon, loai_mon, nguyen_lieu, dinh_luong, thoi_gian, cach_lam, hinh_anh)
                            VALUES (?, ?, ?, ?, ?, '', '')
                        ''', (
                            str(row.get("ten_mon", "")).strip(),
                            str(row.get("loai_mon", "Khác")).strip(),
                            str(row.get("nguyen_lieu", "")).strip(),
                            str(row.get("dinh_luong", "")).strip(),
                            int(float(thoi_gian_val)) # Chuyển đổi an toàn sang số nguyên
                        ))
                    except sqlite3.IntegrityError:
                        pass # Bỏ qua dòng này nếu tên món đã tồn tại (tránh trùng lặp UNIQUE constraint)
                
                conn.commit()  # Xác nhận lưu lại toàn bộ bản ghi đã chuyển đổi thành công
                logger.info("Đã migrate dữ liệu từ congthuc.csv sang congthuc.db thành công.")
            except Exception as e:
                logger.error(f"Lỗi migrate CSV sang DB: {e}")
    finally:
        conn.close()  # Khối finally ĐẢM BẢO kết nối cơ sở dữ liệu luôn được đóng lại, giải phóng tài nguyên hệ thống


def lay_danh_sach():
    """
    Đọc dữ liệu tất cả công thức từ SQLite DB và trả về dưới dạng Pandas DataFrame.
    DataFrame giúp các tầng View/Controller dễ dàng thực hiện tìm kiếm, lọc và hiển thị.
    
    Trả về:
      - (DataFrame, bool): Trả về bảng dữ liệu và trạng thái thành công (True/False)
    """
    khoi_tao_db()  # Đảm bảo cơ sở dữ liệu luôn sẵn sàng trước khi truy vấn
    conn = sqlite3.connect(FILE_DB)
    try:
        # Sử dụng hàm tiện ích của Pandas để đọc trực tiếp câu lệnh SQL SELECT và chuyển thành DataFrame
        df = pd.read_sql_query("SELECT ten_mon, loai_mon, nguyen_lieu, dinh_luong, thoi_gian, cach_lam, hinh_anh, luu_y FROM congthuc", conn)
    except Exception as e:
        logger.error(f"Lỗi đọc DB: {e}")
        return pd.DataFrame(), False  # Trả về DataFrame rỗng và trạng thái lỗi
    finally:
        conn.close()  # Đóng kết nối cơ sở dữ liệu an toàn

    # Nếu cơ sở dữ liệu trống trơn (chưa có món ăn nào)
    if df.empty:
        return df, True

    # 5. CHUẨN HÓA DỮ LIỆU ĐỂ TRÁNH LỖI PHẦN MỀM:
    # Duyệt qua từng cột bắt buộc. Nếu cột nào bị thiếu, ta khởi tạo nó là chuỗi rỗng.
    # fillna("") thay thế các giá trị Null/None (NaN) bằng chuỗi rỗng "".
    # astype(str) ép tất cả kiểu dữ liệu chuỗi về định dạng string chuẩn để tránh lỗi ký tự đặc biệt.
    for col in COLS_DB:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).replace("nan", "")

    # Ép kiểu dữ liệu cột "thoi_gian" về dạng số nguyên (integer). 
    # errors="coerce" sẽ biến các giá trị không hợp lệ (như chữ cái) thành NaN, sau đó fillna(0) biến chúng thành số 0.
    df["thoi_gian"] = pd.to_numeric(df["thoi_gian"], errors="coerce").fillna(0).astype(int)

    return df, True


def them_cong_thuc(df, data):
    """
    Thêm một công thức món ăn mới vào SQLite Database.
    
    Tham số:
      - df (DataFrame): Danh sách dữ liệu công thức hiện tại trên bộ nhớ RAM.
      - data (dict): Bộ từ điển chứa thông tin món mới nhập từ form giao diện.
      
    Trả về:
      - (DataFrame, bool, str): DataFrame mới cập nhật, trạng thái thành công, thông báo kết quả.
    """
    # Lấy và làm sạch dữ liệu chuỗi đầu vào (bỏ khoảng trắng thừa ở hai đầu bằng .strip())
    ten_mon = str(data.get("ten_mon", "")).strip()
    if not ten_mon:
        return df, False, "Tên món ăn không được để trống!"

    loai_mon = str(data.get("loai_mon", "Khác")).strip()
    nguyen_lieu = str(data.get("nguyen_lieu", "")).strip()
    dinh_luong = str(data.get("dinh_luong", "")).strip()
    cach_lam = str(data.get("cach_lam", "")).strip()
    hinh_anh = str(data.get("hinh_anh", "")).strip()
    luu_y = str(data.get("luu_y", "")).strip()

    # Bắt lỗi kiểm tra giá trị thời gian chuẩn bị
    try:
        thoi_gian = int(data.get("thoi_gian", 0))
        if thoi_gian < 0:
            return df, False, "Thời gian chuẩn bị phải >= 0!"
    except (ValueError, TypeError):
        return df, False, "Thời gian chuẩn bị phải là số nguyên!"

    conn = sqlite3.connect(FILE_DB)
    try:
        cursor = conn.cursor()
        
        # 6. PHÒNG CHỐNG SQL INJECTION BẰNG PARAMETERIZED QUERY (?):
        # KHÔNG BAO GIỜ cộng chuỗi SQL như: "INSERT VALUES ('" + ten_mon + "')" vì tin tặc có thể nhập mã độc phá hủy DB.
        # Hãy dùng các ký hiệu chấm hỏi "?" làm tham số đại diện, SQLite sẽ tự động lọc và xử lý chuỗi cực kỳ an toàn!
        cursor.execute('''
            INSERT INTO congthuc (ten_mon, loai_mon, nguyen_lieu, dinh_luong, thoi_gian, cach_lam, hinh_anh, luu_y)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ten_mon, loai_mon, nguyen_lieu, dinh_luong, thoi_gian, cach_lam, hinh_anh, luu_y))
        
        conn.commit()  # Lưu thay đổi vĩnh viễn vào ổ cứng
        logger.info(f"Đã thêm công thức vào DB: {ten_mon}")
        
        # Đọc lại toàn bộ dữ liệu mới nhất từ Database để trả về cho Controller đồng bộ
        new_df, _ = lay_danh_sach()
        return new_df, True, f"Thêm công thức '{ten_mon}' thành công!"
        
    except sqlite3.IntegrityError:
        # Lỗi xảy ra khi vi phạm ràng buộc dữ liệu (ví dụ: tên món ăn bị trùng lặp vì cột ten_mon có thuộc tính UNIQUE)
        return df, False, f"Công thức '{ten_mon}' đã tồn tại!"
    except Exception as e:
        logger.error(f"Lỗi thêm vào DB: {e}")
        return df, False, f"Lỗi cơ sở dữ liệu: {e}"
    finally:
        conn.close()  # Giải phóng kết nối DB


def sua_cong_thuc(df, old_ten, data):
    """
    Cập nhật (Sửa) thông tin một công thức đã tồn tại trong SQLite Database.
    
    Tham số:
      - df (DataFrame): Danh sách dữ liệu công thức hiện tại.
      - old_ten (str): Tên hiện tại của món ăn cần tìm để sửa (Khóa tìm kiếm dòng).
      - data (dict): Bộ dữ liệu thông tin mới cần cập nhật đè lên.
    """
    ten_moi = str(data.get("ten_mon", "")).strip()
    if not ten_moi:
        return df, False, "Tên món ăn không được để trống!"

    loai_mon = str(data.get("loai_mon", "Khác")).strip()
    nguyen_lieu = str(data.get("nguyen_lieu", "")).strip()
    dinh_luong = str(data.get("dinh_luong", "")).strip()
    cach_lam = str(data.get("cach_lam", "")).strip()
    hinh_anh = str(data.get("hinh_anh", "")).strip()
    luu_y = str(data.get("luu_y", "")).strip()

    try:
        thoi_gian = int(data.get("thoi_gian", 0))
        if thoi_gian < 0:
            return df, False, "Thời gian chuẩn bị phải >= 0!"
    except (ValueError, TypeError):
        return df, False, "Thời gian chuẩn bị phải là số nguyên!"

    conn = sqlite3.connect(FILE_DB)
    try:
        cursor = conn.cursor()
        
        # Thực hiện câu lệnh cập nhật cơ sở dữ liệu UPDATE ... SET ... WHERE ...
        # Dùng old_ten để định vị chính xác món ăn cũ cần cập nhật.
        cursor.execute('''
            UPDATE congthuc
            SET ten_mon = ?, loai_mon = ?, nguyen_lieu = ?, dinh_luong = ?, thoi_gian = ?, cach_lam = ?, hinh_anh = ?, luu_y = ?
            WHERE ten_mon = ?
        ''', (ten_moi, loai_mon, nguyen_lieu, dinh_luong, thoi_gian, cach_lam, hinh_anh, luu_y, old_ten))
        
        # cursor.rowcount trả về số lượng dòng bị ảnh hưởng bởi câu lệnh SQL vừa rồi.
        # Nếu bằng 0 nghĩa là không tìm thấy món ăn nào có tên trùng với old_ten để sửa.
        if cursor.rowcount == 0:
            return df, False, f"Không tìm thấy công thức '{old_ten}'!"
            
        conn.commit()
        logger.info(f"Đã sửa công thức trong DB: {old_ten} -> {ten_moi}")
        
        # Tải danh sách mới nhất và trả về
        new_df, _ = lay_danh_sach()
        return new_df, True, f"Sửa công thức '{ten_moi}' thành công!"
        
    except sqlite3.IntegrityError:
        # Trường hợp người dùng đổi tên món mới trùng lặp với một tên món ăn khác đang có sẵn trong DB
        return df, False, f"Công thức '{ten_moi}' đã tồn tại!"
    except Exception as e:
        logger.error(f"Lỗi sửa trong DB: {e}")
        return df, False, f"Lỗi cơ sở dữ liệu: {e}"
    finally:
        conn.close()


def xoa_cong_thuc(df, ten_list):
    """
    Xóa hàng loạt các công thức nấu ăn khỏi cơ sở dữ liệu SQLite.
    
    Tham số:
      - df (DataFrame): Danh sách dữ liệu công thức hiện tại.
      - ten_list (list): Danh sách các tên món ăn được tick chọn cần xóa.
    """
    if not ten_list:
        return df, False, "Danh sách trống!"

    conn = sqlite3.connect(FILE_DB)
    try:
        cursor = conn.cursor()
        
        # 7. KỸ THUẬT TẠO CÂU LỆNH SQL DỘNG CHO DANH SÁCH THAM SỐ (WHERE IN):
        # Khi xóa nhiều món, câu lệnh SQL dạng: "DELETE FROM congthuc WHERE ten_mon IN (?, ?, ?)"
        # placeholders sẽ tạo ra chuỗi các dấu hỏi chấm cách nhau bằng dấu phẩy dựa trên độ dài của ten_list.
        # Ví dụ: nếu ten_list có 3 món -> placeholders sẽ là "?,?,?"
        placeholders = ','.join('?' * len(ten_list))
        
        # Thực thi lệnh DELETE động cực kỳ an toàn
        cursor.execute(f'DELETE FROM congthuc WHERE ten_mon IN ({placeholders})', ten_list)
        
        conn.commit()
        logger.info(f"Đã xóa {len(ten_list)} công thức khỏi DB.")
        
        # Đọc danh sách cập nhật mới
        new_df, _ = lay_danh_sach()
        return new_df, True, f"Đã xóa {len(ten_list)} công thức!"
    except Exception as e:
        logger.error(f"Lỗi xóa trong DB: {e}")
        return df, False, f"Lỗi cơ sở dữ liệu: {e}"
    finally:
        conn.close()


def thong_ke(df):
    """
    Tính toán phân tích số liệu thống kê chi tiết của danh sách công thức hiện tại.
    Hàm này sử dụng sức mạnh tính toán thần tốc của Pandas và NumPy trên bộ nhớ.
    
    Tham số:
      - df (DataFrame): DataFrame cần tính toán thống kê (có thể là bảng toàn bộ hoặc bảng đã lọc).
      
    Trả về:
      - dict: Từ điển chứa các kết quả thống kê (Tổng số món, thời gian chuẩn bị TB/Max/Min, nguyên liệu phổ biến...)
    """
    # Nếu bảng rỗng, trả về từ điển trống
    if df.empty:
        return {}

    # Chuyển đổi cột thời gian của DataFrame thành một mảng NumPy chuyên dụng (numpy array) để tính toán nhanh
    thoi_gian_arr = pd.to_numeric(df["thoi_gian"], errors="coerce").fillna(0).values

    # 8. SỬ DỤNG NUMPY TÍNH TOÁN CÁC CHỈ SỐ:
    # - np.mean(): Tính giá trị trung bình cộng
    # - np.max(): Tìm giá trị lớn nhất trong mảng
    # - np.min(): Tìm giá trị nhỏ nhất trong mảng
    stats = {
        "tong_ct": len(df),                                 # Đếm số lượng hàng dữ liệu trong DataFrame
        "tg_trung_binh": float(np.mean(thoi_gian_arr)),    # Ép kiểu về số thực (float) chuẩn Python
        "tg_max": int(np.max(thoi_gian_arr)),              # Tìm thời gian nấu lâu nhất
        "tg_min": int(np.min(thoi_gian_arr)),              # Tìm thời gian nấu nhanh nhất
    }

    # 9. TÍNH THỜI GIAN TRUNG BÌNH THEO TỪNG LOẠI MÓN ĂN (Món chính, Khai vị...):
    tg_theo_loai = {}
    # df["loai_mon"].unique() trả về danh sách các giá trị duy nhất trong cột loai_mon (không bị trùng lặp)
    for loai in df["loai_mon"].unique():
        # Mask là một bộ lọc True/False để xác định những hàng nào thỏa mãn điều kiện loại món
        mask = df["loai_mon"] == loai
        # Lọc ra các dòng thuộc loại món này, lấy cột thời gian chuyển thành mảng số NumPy
        arr = pd.to_numeric(df.loc[mask, "thoi_gian"], errors="coerce").fillna(0).values
        # Tính trung bình cộng của riêng loại món này
        tg_theo_loai[loai] = float(np.mean(arr)) if len(arr) > 0 else 0.0
    stats["tg_theo_loai"] = tg_theo_loai

    # 10. TÌM TOP NGUYÊN LIỆU ĐƯỢC SỬ DỤNG NHIỀU NHẤT:
    all_nls = []
    # Duyệt qua chuỗi nguyên liệu của từng món ăn (các nguyên liệu ngăn cách nhau bởi dấu gạch đứng "|")
    for nl_str in df["nguyen_lieu"]:
        if nl_str and str(nl_str).strip():
            # Tách chuỗi nguyên liệu thành danh sách các từ, loại bỏ khoảng trắng dư thừa
            parts = [p.strip() for p in str(nl_str).split("|") if p.strip()]
            all_nls.extend(parts)  # Thêm danh sách nguyên liệu của món này vào danh sách tổng

    if all_nls:
        # Chuyển danh sách nguyên liệu tổng thành một đối tượng Series của Pandas
        nl_series = pd.Series(all_nls)
        # .value_counts() sẽ đếm tần suất xuất hiện của từng nguyên liệu
        # .head(10) sẽ lấy ra 10 nguyên liệu có tần suất xuất hiện nhiều nhất (Top 10)
        top_nl = nl_series.value_counts().head(10)
        stats["top_nguyen_lieu"] = dict(top_nl)  # Chuyển kết quả thành từ điển chuẩn
    else:
        stats["top_nguyen_lieu"] = {}

    return stats


def lay_chi_tiet(ten_mon):
    """
    Truy vấn trực tiếp từ cơ sở dữ liệu SQLite để lấy chi tiết của 1 công thức cụ thể theo tên.
    Hàm này cực kỳ quan trọng để đảm bảo khi người dùng click đúp mở tab chi tiết xem món ăn,
    dữ liệu hiển thị luôn đồng bộ, chính xác và mới nhất theo thời gian thực (real-time).
    
    Tham số:
      - ten_mon (str): Tên món ăn cần truy vấn.
      
    Trả về:
      - (dict, bool): Bộ từ điển chi tiết món và trạng thái tìm thấy thành công.
    """
    khoi_tao_db()
    conn = sqlite3.connect(FILE_DB)
    try:
        cursor = conn.cursor()
        # SELECT chính xác các thông tin cần hiển thị
        cursor.execute("SELECT ten_mon, loai_mon, nguyen_lieu, dinh_luong, thoi_gian, cach_lam, hinh_anh, luu_y FROM congthuc WHERE ten_mon = ?", (ten_mon,))
        row = cursor.fetchone()  # .fetchone() lấy ra duy nhất một dòng kết quả tìm thấy đầu tiên
        
        if row:
            # Tạo bộ từ điển chứa thông tin món ăn được gán nhãn rõ ràng
            # row[0] tương ứng với ten_mon, row[1] với loai_mon,...
            # "or """: Đề phòng dữ liệu trong cơ sở dữ liệu bị rỗng (None/Null) thì thay bằng chuỗi trống tránh lỗi crash GUI
            return {
                "ten_mon": row[0],
                "loai_mon": row[1],
                "nguyen_lieu": row[2] or "",
                "dinh_luong": row[3] or "",
                "thoi_gian": int(row[4] or 0),
                "cach_lam": row[5] or "",
                "hinh_anh": row[6] or "",
                "luu_y": row[7] or ""
            }, True
        return None, False  # Không tìm thấy món ăn nào khớp với tên
    except Exception as e:
        logger.error(f"Lỗi truy vấn chi tiết từ DB: {e}")
        return None, False
    finally:
        conn.close()  # Luôn luôn đóng kết nối DB
