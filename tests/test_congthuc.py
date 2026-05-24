"""
tests/test_congthuc.py
======================
Unit Test cho Model Quản lý Công thức Nấu ăn.
Kiểm tra các hàm CRUD và thống kê trong models/congthuc.py.
"""

import os
import sys
import unittest
import tempfile
import pandas as pd

# Đảm bảo import được từ thư mục gốc project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Patch FILE_DB trước khi test để chạy độc lập
import tempfile
temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
temp_db_path = temp_db.name
temp_db.close()

import models.congthuc as model
model.FILE_DB = temp_db_path
# Khởi tạo db mới tinh cho môi trường test
model.khoi_tao_db()



def _make_df(*rows):
    """Helper tạo DataFrame mẫu từ danh sách dict."""
    if not rows:
        return pd.DataFrame(columns=model.COLS_DB)
    df = pd.DataFrame(list(rows))
    df["thoi_gian"] = pd.to_numeric(df["thoi_gian"], errors="coerce").fillna(0).astype(int)
    return df


class TestThemCongThuc(unittest.TestCase):
    """Kiểm tra hàm them_cong_thuc()"""

    def setUp(self):
        import sqlite3
        conn = sqlite3.connect(model.FILE_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM congthuc")
        conn.commit()
        conn.close()
        self.df = pd.DataFrame(columns=model.COLS_DB)

    def test_them_thanh_cong(self):
        data = {"ten_mon": "Phở bò", "loai_mon": "Món chính",
                "nguyen_lieu": "Bún | Thịt", "dinh_luong": "200g | 100g", "thoi_gian": 30}
        df, ok, msg = model.them_cong_thuc(self.df.copy(), data)
        self.assertTrue(ok)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["ten_mon"], "Phở bò")

    def test_them_ten_trong(self):
        data = {"ten_mon": "  ", "loai_mon": "Món chính",
                "nguyen_lieu": "", "dinh_luong": "", "thoi_gian": 10}
        df, ok, msg = model.them_cong_thuc(self.df.copy(), data)
        self.assertFalse(ok)
        self.assertIn("trống", msg.lower())

    def test_them_trung_ten(self):
        data = {"ten_mon": "Bánh mì", "loai_mon": "Khai vị",
                "nguyen_lieu": "Bột", "dinh_luong": "200g", "thoi_gian": 10}
        df, ok, _ = model.them_cong_thuc(self.df.copy(), data)
        self.assertTrue(ok)
        df2, ok2, msg2 = model.them_cong_thuc(df, data)
        self.assertFalse(ok2)
        self.assertIn("tồn tại", msg2)

    def test_them_thoi_gian_am(self):
        data = {"ten_mon": "Chè", "loai_mon": "Tráng miệng",
                "nguyen_lieu": "Đậu", "dinh_luong": "100g", "thoi_gian": -5}
        df, ok, msg = model.them_cong_thuc(self.df.copy(), data)
        self.assertFalse(ok)

    def test_them_thoi_gian_khong_phai_so(self):
        data = {"ten_mon": "Canh", "loai_mon": "Món chính",
                "nguyen_lieu": "Rau", "dinh_luong": "100g", "thoi_gian": "abc"}
        df, ok, msg = model.them_cong_thuc(self.df.copy(), data)
        self.assertFalse(ok)


class TestSuaCongThuc(unittest.TestCase):
    """Kiểm tra hàm sua_cong_thuc()"""

    def setUp(self):
        import sqlite3
        conn = sqlite3.connect(model.FILE_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM congthuc")
        conn.commit()
        conn.close()
        data = {"ten_mon": "Phở bò", "loai_mon": "Món chính",
                "nguyen_lieu": "Bún", "dinh_luong": "200g", "thoi_gian": 30}
        df = pd.DataFrame(columns=model.COLS_DB)
        self.df, _, _ = model.them_cong_thuc(df, data)

    def test_sua_thanh_cong(self):
        new_data = {"ten_mon": "Phở gà", "loai_mon": "Món chính",
                    "nguyen_lieu": "Bún | Gà", "dinh_luong": "200g | 300g", "thoi_gian": 45}
        df, ok, msg = model.sua_cong_thuc(self.df.copy(), "Phở bò", new_data)
        self.assertTrue(ok)
        self.assertEqual(df.iloc[0]["ten_mon"], "Phở gà")
        self.assertEqual(int(df.iloc[0]["thoi_gian"]), 45)

    def test_sua_khong_ton_tai(self):
        new_data = {"ten_mon": "X", "loai_mon": "Khác",
                    "nguyen_lieu": "", "dinh_luong": "", "thoi_gian": 0}
        df, ok, msg = model.sua_cong_thuc(self.df.copy(), "KHONG_TON_TAI", new_data)
        self.assertFalse(ok)

    def test_sua_ten_trong(self):
        new_data = {"ten_mon": "", "loai_mon": "Khác",
                    "nguyen_lieu": "", "dinh_luong": "", "thoi_gian": 10}
        df, ok, msg = model.sua_cong_thuc(self.df.copy(), "Phở bò", new_data)
        self.assertFalse(ok)


class TestXoaCongThuc(unittest.TestCase):
    """Kiểm tra hàm xoa_cong_thuc()"""

    def setUp(self):
        import sqlite3
        conn = sqlite3.connect(model.FILE_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM congthuc")
        conn.commit()
        conn.close()
        df = pd.DataFrame(columns=model.COLS_DB)
        for ten, loai, tg in [
            ("Phở bò", "Món chính", 30),
            ("Bánh mì", "Khai vị", 10),
            ("Chè", "Tráng miệng", 45),
        ]:
            data = {"ten_mon": ten, "loai_mon": loai,
                    "nguyen_lieu": "", "dinh_luong": "", "thoi_gian": tg}
            df, _, _ = model.them_cong_thuc(df, data)
        self.df = df

    def test_xoa_mot(self):
        df, ok, msg = model.xoa_cong_thuc(self.df.copy(), ["Phở bò"])
        self.assertTrue(ok)
        self.assertEqual(len(df), 2)
        self.assertNotIn("Phở bò", df["ten_mon"].values)

    def test_xoa_nhieu(self):
        df, ok, msg = model.xoa_cong_thuc(self.df.copy(), ["Phở bò", "Chè"])
        self.assertTrue(ok)
        self.assertEqual(len(df), 1)

    def test_xoa_danh_sach_rong(self):
        df, ok, msg = model.xoa_cong_thuc(self.df.copy(), [])
        self.assertFalse(ok)
        self.assertEqual(len(df), 3)


class TestThongKe(unittest.TestCase):
    """Kiểm tra hàm thong_ke()"""

    def setUp(self):
        import sqlite3
        conn = sqlite3.connect(model.FILE_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM congthuc")
        conn.commit()
        conn.close()
        df = pd.DataFrame(columns=model.COLS_DB)
        rows = [
            ("Phở bò",   "Món chính",    "Bún | Thịt bò | Hành", "200g | 300g | 50g", 60),
            ("Bún bò",   "Món chính",    "Bún | Thịt bò | Sả",   "200g | 300g | 30g", 120),
            ("Chè đậu",  "Tráng miệng",  "Đậu xanh | Đường",     "200g | 100g",        45),
            ("Sinh tố",  "Đồ uống",      "Bơ | Sữa",             "2 quả | 200ml",       5),
        ]
        for ten, loai, nl, dl, tg in rows:
            data = {"ten_mon": ten, "loai_mon": loai,
                    "nguyen_lieu": nl, "dinh_luong": dl, "thoi_gian": tg}
            df, _, _ = model.them_cong_thuc(df, data)
        self.df = df

    def test_thong_ke_tong(self):
        stats = model.thong_ke(self.df)
        self.assertEqual(stats["tong_ct"], 4)

    def test_thoi_gian_trung_binh(self):
        stats = model.thong_ke(self.df)
        # (60 + 120 + 45 + 5) / 4 = 57.5
        self.assertAlmostEqual(stats["tg_trung_binh"], 57.5, places=1)

    def test_thoi_gian_theo_loai(self):
        stats = model.thong_ke(self.df)
        tg_loai = stats["tg_theo_loai"]
        # Món chính: (60 + 120) / 2 = 90
        self.assertAlmostEqual(tg_loai["Món chính"], 90.0, places=1)
        # Tráng miệng: 45
        self.assertAlmostEqual(tg_loai["Tráng miệng"], 45.0, places=1)

    def test_top_nguyen_lieu(self):
        stats = model.thong_ke(self.df)
        top = stats["top_nguyen_lieu"]
        # "Bún" xuất hiện 2 lần, "Thịt bò" 2 lần
        self.assertIn("Bún", top)
        self.assertIn("Thịt bò", top)
        self.assertEqual(top["Bún"], 2)
        self.assertEqual(top["Thịt bò"], 2)

    def test_thong_ke_rong(self):
        df_empty = pd.DataFrame(columns=model.COLS_DB)
        stats = model.thong_ke(df_empty)
        self.assertEqual(stats, {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
