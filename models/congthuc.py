"""
models/congthuc.py
==================
Model quản lý Công thức Nấu ăn bằng SQLite3.
Sử dụng SQLite3 để lưu trữ (thay cho CSV) và dùng pandas, numpy để tính toán và trả về Controller.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
from utils.logger import setup_logger

logger = setup_logger("congthuc")

# ─── Đường dẫn file Database ──────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FILE_DB = os.path.join(_BASE_DIR, "data", "congthuc.db")

# ─── Danh sách loại món ăn ───────────────────────────
LOAI_MON_LIST = ["Khai vị", "Món chính", "Tráng miệng", "Đồ uống", "Khác"]

# ─── Cột của bảng (tương tự như cũ để tương thích View)
COLS_DB = ["ten_mon", "loai_mon", "nguyen_lieu", "dinh_luong", "thoi_gian", "cach_lam", "hinh_anh", "luu_y"]


def khoi_tao_db():
    """
    Tạo database và bảng nếu chưa tồn tại.
    Đồng thời tự động chuyển đổi (migrate) dữ liệu từ file CSV cũ sang DB nếu có.
    """
    os.makedirs(os.path.dirname(FILE_DB), exist_ok=True)
    db_exists = os.path.exists(FILE_DB)
    
    conn = sqlite3.connect(FILE_DB)
    try:
        cursor = conn.cursor()
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
        
        # Auto-migration cho DB cũ: Thêm cột cach_lam và hinh_anh nếu chưa có
        try:
            cursor.execute('ALTER TABLE congthuc ADD COLUMN cach_lam TEXT DEFAULT ""')
        except sqlite3.OperationalError:
            pass # Cột đã tồn tại
            
        try:
            cursor.execute('ALTER TABLE congthuc ADD COLUMN hinh_anh TEXT DEFAULT ""')
        except sqlite3.OperationalError:
            pass # Cột đã tồn tại

        try:
            cursor.execute('ALTER TABLE congthuc ADD COLUMN luu_y TEXT DEFAULT ""')
        except sqlite3.OperationalError:
            pass # Cột đã tồn tại

        conn.commit()
        
        # Tự động migrate dữ liệu từ file CSV cũ sang Database (chỉ chạy 1 lần khi tạo DB mới)
        csv_file = os.path.join(os.path.dirname(FILE_DB), "congthuc.csv")
        if not db_exists and os.path.exists(csv_file):
            try:
                df_csv = pd.read_csv(csv_file, encoding="utf-8-sig", dtype=str)
                for _, row in df_csv.iterrows():
                    try:
                        thoi_gian_val = row.get("thoi_gian", 0)
                        if pd.isna(thoi_gian_val) or str(thoi_gian_val).strip() == "":
                            thoi_gian_val = 0
                        
                        cursor.execute('''
                            INSERT INTO congthuc (ten_mon, loai_mon, nguyen_lieu, dinh_luong, thoi_gian, cach_lam, hinh_anh)
                            VALUES (?, ?, ?, ?, ?, '', '')
                        ''', (
                            str(row.get("ten_mon", "")).strip(),
                            str(row.get("loai_mon", "Khác")).strip(),
                            str(row.get("nguyen_lieu", "")).strip(),
                            str(row.get("dinh_luong", "")).strip(),
                            int(float(thoi_gian_val))
                        ))
                    except sqlite3.IntegrityError:
                        pass # Bỏ qua nếu món đã tồn tại
                conn.commit()
                logger.info("Đã migrate dữ liệu từ congthuc.csv sang congthuc.db thành công.")
            except Exception as e:
                logger.error(f"Lỗi migrate CSV sang DB: {e}")
    finally:
        conn.close()


def lay_danh_sach():
    """
    Đọc dữ liệu công thức từ SQLite DB và trả về dưới dạng Pandas DataFrame 
    để các tầng View/Controller dễ hiển thị.
    """
    khoi_tao_db()
    conn = sqlite3.connect(FILE_DB)
    try:
        df = pd.read_sql_query("SELECT ten_mon, loai_mon, nguyen_lieu, dinh_luong, thoi_gian, cach_lam, hinh_anh, luu_y FROM congthuc", conn)
    except Exception as e:
        logger.error(f"Lỗi đọc DB: {e}")
        return pd.DataFrame(), False
    finally:
        conn.close()

    if df.empty:
        return df, True

    # Đảm bảo định dạng chuẩn như lúc trước dùng CSV
    for col in COLS_DB:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).replace("nan", "")

    # Ép kiểu thời gian về số nguyên
    df["thoi_gian"] = pd.to_numeric(df["thoi_gian"], errors="coerce").fillna(0).astype(int)

    return df, True


def them_cong_thuc(df, data):
    """
    Thêm công thức mới thẳng vào SQLite Database.
    """
    ten_mon = str(data.get("ten_mon", "")).strip()
    if not ten_mon:
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
        cursor.execute('''
            INSERT INTO congthuc (ten_mon, loai_mon, nguyen_lieu, dinh_luong, thoi_gian, cach_lam, hinh_anh, luu_y)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ten_mon, loai_mon, nguyen_lieu, dinh_luong, thoi_gian, cach_lam, hinh_anh, luu_y))
        conn.commit()
        logger.info(f"Đã thêm công thức vào DB: {ten_mon}")
        
        # Lấy danh sách mới nhất từ DB trả về
        new_df, _ = lay_danh_sach()
        return new_df, True, f"Thêm công thức '{ten_mon}' thành công!"
    except sqlite3.IntegrityError:
        return df, False, f"Công thức '{ten_mon}' đã tồn tại!"
    except Exception as e:
        logger.error(f"Lỗi thêm vào DB: {e}")
        return df, False, f"Lỗi cơ sở dữ liệu: {e}"
    finally:
        conn.close()


def sua_cong_thuc(df, old_ten, data):
    """
    Cập nhật thông tin công thức trong SQLite Database.
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
        cursor.execute('''
            UPDATE congthuc
            SET ten_mon = ?, loai_mon = ?, nguyen_lieu = ?, dinh_luong = ?, thoi_gian = ?, cach_lam = ?, hinh_anh = ?, luu_y = ?
            WHERE ten_mon = ?
        ''', (ten_moi, loai_mon, nguyen_lieu, dinh_luong, thoi_gian, cach_lam, hinh_anh, luu_y, old_ten))
        
        if cursor.rowcount == 0:
            return df, False, f"Không tìm thấy công thức '{old_ten}'!"
            
        conn.commit()
        logger.info(f"Đã sửa công thức trong DB: {old_ten} -> {ten_moi}")
        
        new_df, _ = lay_danh_sach()
        return new_df, True, f"Sửa công thức '{ten_moi}' thành công!"
    except sqlite3.IntegrityError:
        return df, False, f"Công thức '{ten_moi}' đã tồn tại!"
    except Exception as e:
        logger.error(f"Lỗi sửa trong DB: {e}")
        return df, False, f"Lỗi cơ sở dữ liệu: {e}"
    finally:
        conn.close()


def xoa_cong_thuc(df, ten_list):
    """
    Xóa danh sách công thức khỏi SQLite Database.
    """
    if not ten_list:
        return df, False, "Danh sách trống!"

    conn = sqlite3.connect(FILE_DB)
    try:
        cursor = conn.cursor()
        placeholders = ','.join('?' * len(ten_list))
        cursor.execute(f'DELETE FROM congthuc WHERE ten_mon IN ({placeholders})', ten_list)
        conn.commit()
        logger.info(f"Đã xóa {len(ten_list)} công thức khỏi DB.")
        
        new_df, _ = lay_danh_sach()
        return new_df, True, f"Đã xóa {len(ten_list)} công thức!"
    except Exception as e:
        logger.error(f"Lỗi xóa trong DB: {e}")
        return df, False, f"Lỗi cơ sở dữ liệu: {e}"
    finally:
        conn.close()


def thong_ke(df):
    """
    Thống kê dữ liệu trực tiếp trên Pandas DataFrame.
    (Hàm này giữ nguyên do nó tính toán trên kết quả trả về từ lay_danh_sach)
    """
    if df.empty:
        return {}

    thoi_gian_arr = pd.to_numeric(df["thoi_gian"], errors="coerce").fillna(0).values

    stats = {
        "tong_ct": len(df),
        "tg_trung_binh": float(np.mean(thoi_gian_arr)),
        "tg_max": int(np.max(thoi_gian_arr)),
        "tg_min": int(np.min(thoi_gian_arr)),
    }

    tg_theo_loai = {}
    for loai in df["loai_mon"].unique():
        mask = df["loai_mon"] == loai
        arr = pd.to_numeric(df.loc[mask, "thoi_gian"], errors="coerce").fillna(0).values
        tg_theo_loai[loai] = float(np.mean(arr)) if len(arr) > 0 else 0.0
    stats["tg_theo_loai"] = tg_theo_loai

    all_nls = []
    for nl_str in df["nguyen_lieu"]:
        if nl_str and str(nl_str).strip():
            parts = [p.strip() for p in str(nl_str).split("|") if p.strip()]
            all_nls.extend(parts)

    if all_nls:
        nl_series = pd.Series(all_nls)
        top_nl = nl_series.value_counts().head(10)
        stats["top_nguyen_lieu"] = dict(top_nl)
    else:
        stats["top_nguyen_lieu"] = {}

    return stats


def lay_chi_tiet(ten_mon):
    """
    Truy vấn trực tiếp từ cơ sở dữ liệu SQLite để lấy chi tiết của 1 công thức cụ thể theo tên,
    đảm bảo dữ liệu luôn đồng bộ và chính xác nhất.
    """
    khoi_tao_db()
    conn = sqlite3.connect(FILE_DB)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ten_mon, loai_mon, nguyen_lieu, dinh_luong, thoi_gian, cach_lam, hinh_anh, luu_y FROM congthuc WHERE ten_mon = ?", (ten_mon,))
        row = cursor.fetchone()
        if row:
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
        return None, False
    except Exception as e:
        logger.error(f"Lỗi truy vấn chi tiết từ DB: {e}")
        return None, False
    finally:
        conn.close()

