"""
models/congthuc.py
==================
Model quản lý Công thức Nấu ăn.
Sử dụng pandas để đọc/ghi CSV và numpy để thống kê.

Các trường dữ liệu:
    ten_mon     : Tên món ăn
    loai_mon    : Loại món ăn (Khai vị, Món chính, Tráng miệng, Đồ uống, Khác)
    nguyen_lieu : Nguyên liệu (chuỗi, ngăn cách bằng dấu |)
    dinh_luong  : Định lượng (chuỗi, ngăn cách bằng dấu |)
    thoi_gian   : Thời gian chuẩn bị (phút)
"""

import os
import sys
import shutil
import pandas as pd
import numpy as np
from utils.logger import setup_logger

logger = setup_logger("congthuc")

# ─── Đường dẫn file CSV ──────────────────────────────
if getattr(sys, "frozen", False):
    _USER_DIR = os.path.join(os.path.expanduser("~"), "SmartAttend_Data")
    _BASE_DIR = _USER_DIR

    _INSTALL_DATA = os.path.join(os.path.dirname(sys.executable), "data")
    _USER_DATA = os.path.join(_BASE_DIR, "data")

    if not os.path.exists(_USER_DATA):
        os.makedirs(_USER_DATA, exist_ok=True)
        for f in ["congthuc.csv"]:
            src = os.path.join(_INSTALL_DATA, f)
            dst = os.path.join(_USER_DATA, f)
            if os.path.exists(src):
                shutil.copy2(src, dst)
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(__file__))

FILE_CONGTHUC = os.path.join(_BASE_DIR, "data", "congthuc.csv")

# ─── Danh sách loại món ăn ───────────────────────────
LOAI_MON_LIST = ["Khai vị", "Món chính", "Tráng miệng", "Đồ uống", "Khác"]

# ─── Cột của CSV ─────────────────────────────────────
COLS_CSV = ["ten_mon", "loai_mon", "nguyen_lieu", "dinh_luong", "thoi_gian"]


def khoi_tao_csv():
    """
    Tạo file CSV rỗng nếu chưa tồn tại.
    """
    os.makedirs(os.path.dirname(FILE_CONGTHUC), exist_ok=True)
    if not os.path.exists(FILE_CONGTHUC):
        df_empty = pd.DataFrame(columns=COLS_CSV)
        df_empty.to_csv(FILE_CONGTHUC, index=False, encoding="utf-8-sig")
        logger.info(f"Đã tạo file mới: {FILE_CONGTHUC}")


def lay_danh_sach():
    """
    Đọc dữ liệu công thức từ CSV.

    Returns:
        tuple: (pandas.DataFrame, bool trạng thái thành công)
    """
    khoi_tao_csv()
    try:
        df = pd.read_csv(FILE_CONGTHUC, encoding="utf-8-sig", dtype=str)
    except Exception as e:
        logger.error(f"Lỗi đọc file: {e}")
        return pd.DataFrame(), False

    if df.empty:
        return df, True

    # Đảm bảo đầy đủ cột
    for col in COLS_CSV:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).replace("nan", "")

    # Ép kiểu thời gian về số
    df["thoi_gian"] = pd.to_numeric(df["thoi_gian"], errors="coerce").fillna(0).astype(int)

    return df, True


def luu_danh_sach(df):
    """
    Ghi DataFrame xuống CSV.

    Args:
        df (pandas.DataFrame): Dữ liệu cần lưu.

    Returns:
        bool: True nếu thành công.
    """
    try:
        df_save = df[COLS_CSV].copy()
        df_save.to_csv(FILE_CONGTHUC, index=False, encoding="utf-8-sig")
        logger.debug(f"Ghi file congthuc.csv ({len(df)} dòng)")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi ghi file: {e}")
        return False


def them_cong_thuc(df, data):
    """
    Thêm công thức mới vào DataFrame.

    Args:
        df (pandas.DataFrame): Bảng dữ liệu hiện tại.
        data (dict): Thông tin công thức (ten_mon, loai_mon, nguyen_lieu, dinh_luong, thoi_gian).

    Returns:
        tuple: (DataFrame mới, bool trạng thái, str thông báo)
    """
    ten_mon = str(data.get("ten_mon", "")).strip()
    if not ten_mon:
        return df, False, "Tên món ăn không được để trống!"

    if not df.empty and ten_mon.lower() in df["ten_mon"].str.lower().values:
        return df, False, f"Công thức '{ten_mon}' đã tồn tại!"

    loai_mon = str(data.get("loai_mon", "Khác")).strip()
    nguyen_lieu = str(data.get("nguyen_lieu", "")).strip()
    dinh_luong = str(data.get("dinh_luong", "")).strip()

    try:
        thoi_gian = int(data.get("thoi_gian", 0))
        if thoi_gian < 0:
            return df, False, "Thời gian chuẩn bị phải >= 0!"
    except (ValueError, TypeError):
        return df, False, "Thời gian chuẩn bị phải là số nguyên!"

    row = {
        "ten_mon": ten_mon,
        "loai_mon": loai_mon,
        "nguyen_lieu": nguyen_lieu,
        "dinh_luong": dinh_luong,
        "thoi_gian": thoi_gian,
    }

    df_new = pd.DataFrame([row])
    df = pd.concat([df, df_new], ignore_index=True)
    luu_danh_sach(df)
    logger.info(f"Đã thêm công thức: {ten_mon}")
    return df, True, f"Thêm công thức '{ten_mon}' thành công!"


def sua_cong_thuc(df, old_ten, data):
    """
    Cập nhật thông tin công thức đã có.

    Args:
        df (pandas.DataFrame): Bảng dữ liệu hiện tại.
        old_ten (str): Tên món cũ.
        data (dict): Dữ liệu mới.

    Returns:
        tuple: (DataFrame mới, bool trạng thái, str thông báo)
    """
    idx = df.index[df["ten_mon"].str.lower() == old_ten.lower()]
    if len(idx) == 0:
        return df, False, f"Không tìm thấy công thức '{old_ten}'!"

    ten_moi = str(data.get("ten_mon", "")).strip()
    if not ten_moi:
        return df, False, "Tên món ăn không được để trống!"

    if ten_moi.lower() != old_ten.lower() and (
        not df.empty and ten_moi.lower() in df["ten_mon"].str.lower().values
    ):
        return df, False, f"Công thức '{ten_moi}' đã tồn tại!"

    try:
        thoi_gian = int(data.get("thoi_gian", 0))
        if thoi_gian < 0:
            return df, False, "Thời gian chuẩn bị phải >= 0!"
    except (ValueError, TypeError):
        return df, False, "Thời gian chuẩn bị phải là số nguyên!"

    df.loc[idx, "ten_mon"] = ten_moi
    df.loc[idx, "loai_mon"] = str(data.get("loai_mon", "Khác")).strip()
    df.loc[idx, "nguyen_lieu"] = str(data.get("nguyen_lieu", "")).strip()
    df.loc[idx, "dinh_luong"] = str(data.get("dinh_luong", "")).strip()
    df.loc[idx, "thoi_gian"] = thoi_gian

    luu_danh_sach(df)
    logger.info(f"Đã sửa công thức: {old_ten} -> {ten_moi}")
    return df, True, f"Sửa công thức '{ten_moi}' thành công!"


def xoa_cong_thuc(df, ten_list):
    """
    Xóa các công thức theo danh sách tên.

    Args:
        df (pandas.DataFrame): Bảng dữ liệu hiện tại.
        ten_list (list): Danh sách tên món cần xóa.

    Returns:
        tuple: (DataFrame mới, bool trạng thái, str thông báo)
    """
    if not ten_list:
        return df, False, "Danh sách trống!"

    df = df[~df["ten_mon"].isin(ten_list)].reset_index(drop=True)
    luu_danh_sach(df)
    logger.info(f"Đã xóa {len(ten_list)} công thức.")
    return df, True, f"Đã xóa {len(ten_list)} công thức!"


def thong_ke(df):
    """
    Thống kê:
      - Tổng số công thức
      - Thời gian chuẩn bị trung bình theo từng loại món
      - Top 10 nguyên liệu được dùng nhiều nhất

    Args:
        df (pandas.DataFrame): Bảng dữ liệu hiện tại.

    Returns:
        dict: Kết quả thống kê.
    """
    if df.empty:
        return {}

    # Đảm bảo thoi_gian là số
    thoi_gian_arr = pd.to_numeric(df["thoi_gian"], errors="coerce").fillna(0).values

    stats = {
        "tong_ct": len(df),
        "tg_trung_binh": float(np.mean(thoi_gian_arr)),
        "tg_max": int(np.max(thoi_gian_arr)),
        "tg_min": int(np.min(thoi_gian_arr)),
    }

    # Thời gian trung bình theo loại món
    tg_theo_loai = {}
    for loai in df["loai_mon"].unique():
        mask = df["loai_mon"] == loai
        arr = pd.to_numeric(df.loc[mask, "thoi_gian"], errors="coerce").fillna(0).values
        tg_theo_loai[loai] = float(np.mean(arr)) if len(arr) > 0 else 0.0
    stats["tg_theo_loai"] = tg_theo_loai

    # Thống kê nguyên liệu phổ biến
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
