"""
controllers/gui_controller_congthuc.py
=======================================
Controller kết nối Model (congthuc.py) và View (gui_view_congthuc.py).
Chứa toàn bộ logic điều khiển (business logic) và xử lý sự kiện giao diện.
"""

import tkinter as tk
from tkinter import messagebox
import pandas as pd
from models import congthuc as model
import views.gui_view_congthuc as view
from utils.logger import setup_logger

# Logger riêng cho tầng Controller
logger = setup_logger("ctrl_congthuc")

# ─── TRẠNG THÁI TOÀN CỤC CỦA ỨNG DỤNG ──────────────────────────────────────────
app_df   = pd.DataFrame()  # DataFrame công thức đang lưu trong bộ nhớ
app_ui   = {}              # Dict chứa tất cả widget giao diện
app_root = None            # Cửa sổ Tkinter chính
active_detail_windows = {} # Các cửa sổ chi tiết đang mở: {ten_mon: window_object}


# ─── HÀM TRỢ GIÚP NỘI BỘ ───────────────────────────────────────────────────────

def _tai_du_lieu():
    """Tải dữ liệu mới nhất từ DB, áp dụng bộ lọc và cập nhật toàn bộ giao diện."""
    global app_df

    app_df, ok = model.lay_danh_sach()
    if not ok:
        messagebox.showerror("Lỗi", "Không thể tải dữ liệu công thức từ cơ sở dữ liệu.")
        return

    # Lọc và hiển thị bảng chính
    display_df = _apply_filter(app_df.copy())
    view.hien_thi_bang(app_ui, display_df)

    # Cập nhật thanh trạng thái theo dữ liệu đang lọc
    stats = model.thong_ke(display_df)
    view.cap_nhat_status(app_ui, stats)

    # Cập nhật trang thống kê theo toàn bộ dữ liệu
    stats_all = model.thong_ke(app_df)
    view.cap_nhat_trang_thong_ke(app_ui, stats_all)


def _apply_filter(df):
    """
    Lọc DataFrame theo loại món và từ khóa tìm kiếm (hỗ trợ tiếng Việt không dấu).

    Tham số:
      df (DataFrame): Bản sao dữ liệu cần lọc.
    Trả về:
      DataFrame đã lọc.
    """
    import unicodedata

    if df is None or df.empty:
        return df

    # Lọc theo loại món ăn từ Combobox
    loai = app_ui["cbo_filter"].get()
    if loai and loai != "Tất cả":
        df = df[df["loai_mon"] == loai]

    # Lọc theo từ khóa tìm kiếm
    keyword = app_ui["ent_search"].get().strip()
    if keyword:

        def remove_accents(input_str):
            """Xóa dấu tiếng Việt, chuẩn hóa chữ đ/Đ thành d/D.
            Dùng NFC trước để đồng nhất ký tự từ các bộ gõ tiếng Việt khác nhau,
            sau đó NFKD để tách dấu ra khỏi ký tự gốc."""
            if not isinstance(input_str, str):
                input_str = str(input_str)
            # Bước 1: NFC để chuẩn hóa về dạng hợp thành (phòng trường hợp bộ gõ gửi dạng NFD)
            s = unicodedata.normalize('NFC', input_str)
            # Bước 2: NFKD để phân tách ký tự có dấu thành ký tự gốc + combining marks
            s = unicodedata.normalize('NFKD', s)
            # Bước 3: Loại bỏ các combining marks (dấu thanh, dấu mũ, v.v.)
            s = "".join([c for c in s if not unicodedata.combining(c)])
            # Bước 4: Xử lý riêng chữ đ/Đ (không bị NFKD phân tách)
            return s.replace('đ', 'd').replace('Đ', 'D')

        # Chuẩn hóa NFC cho từ khóa người dùng nhập rồi mới lowercase
        keyword_normalized = unicodedata.normalize('NFC', keyword).lower()

        # Tách từ khóa thành từng từ để tìm kiếm AND logic (mỗi từ phải xuất hiện)
        kw_parts = [remove_accents(k) for k in keyword_normalized.split()]

        def normalize_col(series):
            """Chuẩn hóa cột pandas: chuyển sang str, xóa dấu, đưa về chữ thường."""
            return series.astype(str).apply(lambda x: remove_accents(x.lower()))

        # Chỉ tìm kiếm trên cột tên món ăn (ten_mon)
        # Không tìm trong nguyen_lieu để tránh trả về các món có nguyên liệu trùng từ khóa
        search_series = normalize_col(df["ten_mon"])

        # AND logic: tất cả từ khóa phải xuất hiện trong chuỗi tổng hợp
        mask = pd.Series([True] * len(df), index=df.index)
        for kw in kw_parts:
            mask = mask & search_series.str.contains(kw, regex=False, na=False)

        df = df[mask]

    return df


# ─── XỬ LÝ SỰ KIỆN GIAO DIỆN ────────────────────────────────────────────────────

def on_trangchu():
    """Chuyển sang màn hình Trang chủ."""
    logger.info("Chuyển sang Trang chủ.")
    view.switch_page(app_ui, "trang_chu")


def on_thongke():
    """Tính toán thống kê và chuyển sang màn hình Dashboard."""
    logger.info("Chuyển sang màn hình Thống kê.")
    stats = model.thong_ke(app_df)
    view.cap_nhat_trang_thong_ke(app_ui, stats)
    view.switch_page(app_ui, "thong_ke")


def on_about():
    """Chuyển sang màn hình Giới thiệu nhóm."""
    logger.info("Chuyển sang màn hình Giới thiệu.")
    view.switch_page(app_ui, "about")


def on_search(*_):
    """Lọc và vẽ lại bảng khi người dùng bấm Tìm hoặc nhấn Enter."""
    logger.info("Thực hiện tìm kiếm.")
    display_df = _apply_filter(app_df.copy())
    view.hien_thi_bang(app_ui, display_df)
    stats = model.thong_ke(display_df)
    view.cap_nhat_status(app_ui, stats)


def on_clear_search():
    """Xóa bộ lọc tìm kiếm và tải lại toàn bộ dữ liệu."""
    logger.info("Xóa bộ lọc tìm kiếm.")
    app_ui["ent_search"].delete(0, tk.END)  # Xóa ô tìm kiếm
    app_ui["cbo_filter"].set("Tất cả")      # Đặt lại Combobox về mặc định
    _tai_du_lieu()


def on_them():
    """Mở form thêm công thức mới và lưu vào DB nếu hợp lệ."""
    global app_df
    logger.info("Mở Form thêm công thức.")
    data = view.hien_thi_form(app_root, is_edit=False)
    if data:
        app_df, ok, msg = model.them_cong_thuc(app_df, data)
        if ok:
            _tai_du_lieu()
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Lỗi", msg)


def on_sua():
    """Mở form sửa công thức đang chọn và đồng bộ cửa sổ chi tiết nếu đang mở."""
    global app_df
    logger.info("Mở Form sửa công thức.")
    tree = app_ui["tree"]

    # Ưu tiên lấy dòng đang được tick checkbox, sau đó mới xét dòng đang bôi đen
    checked = [iid for iid in tree.get_children()
               if tree.item(iid, "values")[0] == "☑"]
    if not checked:
        checked = list(tree.selection())

    if not checked:
        messagebox.showwarning("Cảnh báo",
            "Vui lòng tích chọn (☑) hoặc bấm chọn 1 công thức trên bảng để sửa!")
        return

    if len(checked) > 1:
        messagebox.showwarning("Cảnh báo",
            "Chỉ được phép chọn duy nhất 1 công thức để sửa tại một thời điểm!")
        return

    # vals[0]: dấu check, vals[1]: STT, vals[2]: tên món
    vals = tree.item(checked[0], "values")
    ten_mon = vals[2]

    row = app_df[app_df["ten_mon"] == ten_mon]
    if row.empty:
        messagebox.showerror("Lỗi", "Không tìm thấy công thức nấu ăn tương ứng!")
        return

    current_data = row.iloc[0].to_dict()
    data = view.hien_thi_form(app_root, is_edit=True, current_data=current_data)
    if data:
        app_df, ok, msg = model.sua_cong_thuc(app_df, ten_mon, data)
        if ok:
            _tai_du_lieu()

            # Nếu cửa sổ chi tiết của món này đang mở, đóng và mở lại với dữ liệu mới
            if ten_mon in active_detail_windows:
                old_win = active_detail_windows.pop(ten_mon, None)
                if old_win and old_win.winfo_exists():
                    old_win.destroy()

                ten_moi = data.get("ten_mon", ten_mon)
                new_data, d_ok = model.lay_chi_tiet(ten_moi)
                if d_ok:
                    new_win = view.hien_thi_chi_tiet(app_root, new_data)
                    if new_win:
                        active_detail_windows[ten_moi] = new_win
                        new_win.bind("<Destroy>", lambda e, name=ten_moi, w=new_win:
                            active_detail_windows.pop(name, None) if (e.widget == w) else None)

            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Lỗi", msg)


def on_xoa():
    """Xóa các công thức đã tick chọn và đóng các cửa sổ chi tiết liên quan."""
    global app_df
    logger.info("Xóa các công thức đã chọn.")
    tree = app_ui["tree"]

    # Thu thập tên các món ăn được tick checkbox
    ten_list = [tree.item(iid, "values")[2]
                for iid in tree.get_children()
                if tree.item(iid, "values")[0] == "☑"]

    if not ten_list:
        messagebox.showwarning("Cảnh báo",
            "Vui lòng tick chọn (☑) ít nhất 1 công thức trên bảng để xóa!")
        return

    if messagebox.askyesno("Xác nhận",
                           f"Bạn có chắc chắn muốn xóa {len(ten_list)} công thức nấu ăn đã chọn?"):
        app_df, ok, msg = model.xoa_cong_thuc(app_df, ten_list)
        if ok:
            # Đóng các cửa sổ chi tiết của các món vừa bị xóa
            for ten in ten_list:
                win = active_detail_windows.pop(ten, None)
                if win and win.winfo_exists():
                    win.destroy()

            _tai_du_lieu()
            messagebox.showinfo("Thành công", "Đã xóa công thức nấu ăn thành công!")
        else:
            messagebox.showerror("Lỗi", msg)


def on_single_click(event):
    """
    Xử lý click chuột trên bảng:
    - Click vào tiêu đề cột 'Chọn': tick/untick toàn bộ dòng.
    - Click vào ô 'Chọn' của một dòng: đảo trạng thái checkbox dòng đó.
    """
    tree = app_ui["tree"]
    region  = tree.identify_region(event.x, event.y)   # Vùng click: heading, cell, row...
    col_str = tree.identify_column(event.x)             # Cột click dạng "#1", "#2"...
    if not col_str:
        return
    col_idx  = int(col_str.replace("#", "")) - 1        # Chuyển thành chỉ số 0-indexed
    col_name = app_ui["cols"][col_idx]                  # Lấy tên cột tương ứng

    # Click vào tiêu đề cột "Chọn" → chọn/bỏ chọn tất cả dòng
    if region == "heading" and col_name == "Chọn":
        cur      = tree.heading("Chọn", "text")
        new_mark = "☑" if "☐" in cur else "☐"
        tree.heading("Chọn", text=new_mark)
        for iid in tree.get_children():
            vals    = list(tree.item(iid, "values"))
            vals[0] = new_mark
            tree.item(iid, values=vals)
        return

    # Click vào ô checkbox của một dòng → đảo trạng thái dòng đó
    if region == "cell" and col_name == "Chọn":
        iid = tree.identify_row(event.y)
        if iid:
            vals    = list(tree.item(iid, "values"))
            vals[0] = "☑" if vals[0] == "☐" else "☐"
            tree.item(iid, values=vals)


def on_double_click(event):
    """
    Mở cửa sổ chi tiết khi double-click vào dòng trên bảng.
    Nếu cửa sổ đã mở, chỉ đưa nó lên foreground thay vì mở mới.
    """
    tree = app_ui["tree"]

    if tree.identify_region(event.x, event.y) != "cell":
        return
    iid = tree.identify_row(event.y)
    if not iid:
        return

    vals    = list(tree.item(iid, "values"))
    ten_mon = vals[2]  # Cột 2 là tên món ăn

    # Nếu cửa sổ chi tiết đã mở → đưa lên foreground
    if ten_mon in active_detail_windows:
        win = active_detail_windows[ten_mon]
        if win and win.winfo_exists():
            win.lift()
            win.focus_set()
            return

    # Lấy dữ liệu chi tiết từ DB và mở cửa sổ mới
    current_data, ok = model.lay_chi_tiet(ten_mon)
    if not ok:
        messagebox.showerror("Lỗi", "Không thể lấy chi tiết công thức từ cơ sở dữ liệu SQLite!")
        return

    new_win = view.hien_thi_chi_tiet(app_root, current_data)
    if new_win:
        active_detail_windows[ten_mon] = new_win
        # Khi cửa sổ bị đóng, tự động xóa khỏi danh sách đang mở
        new_win.bind("<Destroy>", lambda e, name=ten_mon, w=new_win:
            active_detail_windows.pop(name, None) if (e.widget == w) else None)


# ─── GÁN SỰ KIỆN VÀO WIDGET ─────────────────────────────────────────────────────

def _bind_events():
    """Gán các hàm xử lý sự kiện vào widget tương ứng trên giao diện."""
    # Điều hướng sidebar
    app_ui["btn_trangchu"].config(command=on_trangchu)
    app_ui["btn_thongke"].config(command=on_thongke)
    app_ui["btn_about"].config(command=on_about)

    # Thao tác CRUD và tìm kiếm
    app_ui["btn_them"].config(command=on_them)
    app_ui["btn_sua"].config(command=on_sua)
    app_ui["btn_xoa"].config(command=on_xoa)
    app_ui["btn_search"].config(command=on_search)
    app_ui["btn_clear"].config(command=on_clear_search)

    # Phím tắt và sự kiện thay đổi bộ lọc
    app_ui["ent_search"].bind("<Return>", on_search)                  # Enter → tìm ngay
    app_ui["cbo_filter"].bind("<<ComboboxSelected>>", on_search)      # Đổi loại món → tìm ngay

    # Sự kiện click trên bảng Treeview
    tree = app_ui["tree"]
    tree.bind("<ButtonRelease-1>", on_single_click)  # Click đơn → xử lý checkbox
    tree.bind("<Double-1>", on_double_click)         # Click đúp → xem chi tiết


# ─── ĐIỂM KHỞI CHẠY CHÍNH ───────────────────────────────────────────────────────

def chay_ung_dung():
    """Khởi chạy ứng dụng Quản lý Công thức Nấu ăn."""
    global app_root, app_ui
    logger.info("Khởi động Quản lý Công thức Nấu ăn Dashboard (GUI)")

    app_root = tk.Tk()                                  # Tạo cửa sổ Tkinter gốc
    app_ui   = view.tao_giao_dien_chinh(app_root)       # Khởi tạo toàn bộ giao diện
    _bind_events()                                      # Gán sự kiện vào widget
    _tai_du_lieu()                                      # Tải dữ liệu ban đầu từ DB

    app_root.mainloop()                                 # Vòng lặp sự kiện chính

    logger.info("Thoát ứng dụng Công thức Nấu ăn Dashboard (GUI)")
