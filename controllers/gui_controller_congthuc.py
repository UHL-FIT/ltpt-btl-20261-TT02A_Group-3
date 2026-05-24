"""
controllers/gui_controller_congthuc.py
=======================================
Controller kết nối Model (congthuc) và View (gui_view_congthuc).
Quản lý luồng điều hướng của hệ thống Dashboard và các sự kiện GUI.
"""

import tkinter as tk
from tkinter import messagebox
import pandas as pd
from models import congthuc as model
import views.gui_view_congthuc as view
from utils.logger import setup_logger

logger = setup_logger("ctrl_congthuc")

# ─── Module-level state ──────────────────────────────
app_df   = pd.DataFrame()
app_ui   = {}
app_root = None
active_detail_windows = {}  # Lưu trữ các cửa sổ chi tiết đang mở: {ten_mon: window_object}



# ─── Internal helpers ────────────────────────────────

def _tai_du_lieu():
    """Tải dữ liệu từ model, áp dụng bộ lọc hiển thị bảng chính và đồng bộ thống kê."""
    global app_df
    app_df, ok = model.lay_danh_sach()
    if not ok:
        messagebox.showerror("Lỗi", "Không thể tải dữ liệu công thức.")
        return

    # 1. Cập nhật bảng ở Trang chủ
    display_df = _apply_filter(app_df.copy())
    view.hien_thi_bang(app_ui, display_df)

    # 2. Cập nhật thanh trạng thái
    stats = model.thong_ke(display_df)
    view.cap_nhat_status(app_ui, stats)

    # 3. Đồng bộ vẽ lại trang thống kê tĩnh
    stats_all = model.thong_ke(app_df)
    view.cap_nhat_trang_thong_ke(app_ui, stats_all)


def _apply_filter(df):
    """Lọc DataFrame theo từ khóa tìm kiếm và loại món."""
    import unicodedata
    
    if df is None or df.empty:
        return df

    loai = app_ui["cbo_filter"].get()
    if loai and loai != "Tất cả":
        df = df[df["loai_mon"] == loai]

    keyword = app_ui["ent_search"].get().strip().lower()
    if keyword:
        # Hàm con hỗ trợ xóa dấu tiếng Việt và chữ 'đ'
        def remove_accents(input_str):
            if not isinstance(input_str, str):
                input_str = str(input_str)
            s = unicodedata.normalize('NFKD', input_str)
            s = "".join([c for c in s if not unicodedata.combining(c)])
            return s.replace('đ', 'd').replace('Đ', 'D')
        
        # Tách từ khóa để tìm kiếm thông minh (AND logic)
        kw_parts = [remove_accents(k) for k in keyword.split()]
        
        def check_row(row):
            # Gom tất cả các cột thành 1 chuỗi dài, xóa dấu và đưa về chữ thường
            row_str = remove_accents(" ".join(row.astype(str)).lower())
            # Kiểm tra xem TẤT CẢ các từ khóa có nằm trong chuỗi này không
            return all(k in row_str for k in kw_parts)
            
        mask = df.apply(check_row, axis=1)
        df = df[mask]

    return df


# ─── Event handlers ──────────────────────────────────

def on_trangchu():
    """Chuyển sang màn hình Trang chủ (danh sách công thức)."""
    logger.info("Chuyển sang Trang chủ.")
    view.switch_page(app_ui, "trang_chu")


def on_thongke():
    """Cập nhật dữ liệu và chuyển sang màn hình Thống kê tĩnh."""
    logger.info("Chuyển sang màn hình Thống kê.")
    stats = model.thong_ke(app_df)
    view.cap_nhat_trang_thong_ke(app_ui, stats)
    view.switch_page(app_ui, "thong_ke")


def on_about():
    """Chuyển sang màn hình Giới thiệu/About tĩnh."""
    logger.info("Chuyển sang màn hình Giới thiệu.")
    view.switch_page(app_ui, "about")


def on_search(*_):
    """Thực hiện tìm kiếm và cập nhật dữ liệu."""
    logger.info("Thực hiện tìm kiếm.")
    display_df = _apply_filter(app_df.copy())
    view.hien_thi_bang(app_ui, display_df)
    stats = model.thong_ke(display_df)
    view.cap_nhat_status(app_ui, stats)


def on_clear_search():
    """Xóa từ khóa tìm kiếm và bộ lọc về mặc định."""
    logger.info("Xóa bộ lọc tìm kiếm.")
    app_ui["ent_search"].delete(0, tk.END)
    app_ui["cbo_filter"].set("Tất cả")
    _tai_du_lieu()


def on_them():
    """Mở Form nhập liệu thêm công thức mới."""
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
    """Mở Form sửa công thức được chọn."""
    global app_df
    logger.info("Mở Form sửa công thức.")
    tree = app_ui["tree"]

    checked = [iid for iid in tree.get_children()
               if tree.item(iid, "values")[0] == "☑"]
    if not checked:
        checked = list(tree.selection())
    if not checked:
        messagebox.showwarning("Cảnh báo",
            "Vui lòng chọn (☑) hoặc bấm chọn 1 công thức để sửa!")
        return
    if len(checked) > 1:
        messagebox.showwarning("Cảnh báo",
            "Chỉ được chọn 1 công thức để sửa!")
        return

    vals = tree.item(checked[0], "values")
    ten_mon = vals[2]
    row = app_df[app_df["ten_mon"] == ten_mon]
    if row.empty:
        messagebox.showerror("Lỗi", "Không tìm thấy công thức!")
        return

    current_data = row.iloc[0].to_dict()
    data = view.hien_thi_form(app_root, is_edit=True, current_data=current_data)
    if data:
        app_df, ok, msg = model.sua_cong_thuc(app_df, ten_mon, data)
        if ok:
            _tai_du_lieu()
            
            # Đồng bộ: Cập nhật cửa sổ chi tiết nếu món ăn đang được xem
            if ten_mon in active_detail_windows:
                old_win = active_detail_windows.pop(ten_mon, None)
                if old_win and old_win.winfo_exists():
                    old_win.destroy()
                
                # Mở lại cửa sổ chi tiết mới với dữ liệu cập nhật từ DB
                ten_moi = data.get("ten_mon", ten_mon)
                new_data, d_ok = model.lay_chi_tiet(ten_moi)
                if d_ok:
                    new_win = view.hien_thi_chi_tiet(app_root, new_data)
                    if new_win:
                        active_detail_windows[ten_moi] = new_win
                        new_win.bind("<Destroy>", lambda e, name=ten_moi, w=new_win: active_detail_windows.pop(name, None) if (e.widget == w) else None)
            
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Lỗi", msg)


def on_xoa():
    """Xóa các công thức đã tick chọn."""
    global app_df
    logger.info("Xóa các công thức đã chọn.")
    tree = app_ui["tree"]
    ten_list = [tree.item(iid, "values")[2]
                for iid in tree.get_children()
                if tree.item(iid, "values")[0] == "☑"]
    if not ten_list:
        messagebox.showwarning("Cảnh báo",
            "Vui lòng tick (☑) ít nhất 1 công thức để xóa!")
        return
    if messagebox.askyesno("Xác nhận",
                           f"Bạn có chắc muốn xóa {len(ten_list)} công thức đã chọn?"):
        app_df, ok, msg = model.xoa_cong_thuc(app_df, ten_list)
        if ok:
            # Đồng bộ: Tự động đóng cửa sổ chi tiết của các món ăn đã bị xóa khỏi DB
            for ten in ten_list:
                win = active_detail_windows.pop(ten, None)
                if win and win.winfo_exists():
                    win.destroy()
            _tai_du_lieu()
            messagebox.showinfo("Thành công", "Đã xóa công thức nấu ăn thành công!")
        else:
            messagebox.showerror("Lỗi", msg)


def on_single_click(event):
    """Bật/tắt checkbox khi click vào cột Chọn."""
    tree = app_ui["tree"]
    region = tree.identify_region(event.x, event.y)
    col_str = tree.identify_column(event.x)
    if not col_str:
        return
    col_idx = int(col_str.replace("#", "")) - 1
    col_name = app_ui["cols"][col_idx]

    # Click vào heading Chọn -> chọn/bỏ chọn tất cả
    if region == "heading" and col_name == "Chọn":
        cur = tree.heading("Chọn", "text")
        new_mark = "☑" if "☐" in cur else "☐"
        tree.heading("Chọn", text=new_mark)
        for iid in tree.get_children():
            vals = list(tree.item(iid, "values"))
            vals[0] = new_mark
            tree.item(iid, values=vals)
        return

    # Click vào cell Chọn -> toggle dòng đó
    if region == "cell" and col_name == "Chọn":
        iid = tree.identify_row(event.y)
        if iid:
            vals = list(tree.item(iid, "values"))
            vals[0] = "☑" if vals[0] == "☐" else "☐"
            tree.item(iid, values=vals)


def on_double_click(event):
    """Double-click vào dòng -> mở màn hình xem chi tiết món ăn trực tiếp từ DB."""
    tree = app_ui["tree"]
    if tree.identify_region(event.x, event.y) != "cell":
        return
    iid = tree.identify_row(event.y)
    if not iid:
        return
    
    vals = list(tree.item(iid, "values"))
    ten_mon = vals[2]
    
    # Đồng bộ: Nếu cửa sổ chi tiết của món này đã mở rồi thì chỉ mang nó lên trước (lift)
    if ten_mon in active_detail_windows:
        win = active_detail_windows[ten_mon]
        if win and win.winfo_exists():
            win.lift()
            win.focus_set()
            return
            
    # Lấy dữ liệu mới nhất trực tiếp từ cơ sở dữ liệu SQLite để xem chi tiết
    current_data, ok = model.lay_chi_tiet(ten_mon)
    if not ok:
        messagebox.showerror("Lỗi", "Không thể lấy chi tiết công thức từ cơ sở dữ liệu!")
        return
        
    new_win = view.hien_thi_chi_tiet(app_root, current_data)
    if new_win:
        active_detail_windows[ten_mon] = new_win
        new_win.bind("<Destroy>", lambda e, name=ten_mon, w=new_win: active_detail_windows.pop(name, None) if (e.widget == w) else None)


# ─── Bind events ─────────────────────────────────────

def _bind_events():
    # Điều hướng Sidebar trái
    app_ui["btn_trangchu"].config(command=on_trangchu)
    app_ui["btn_thongke"].config(command=on_thongke)
    app_ui["btn_about"].config(command=on_about)
    
    # Thao tác Trang chủ
    app_ui["btn_them"].config(command=on_them)
    app_ui["btn_sua"].config(command=on_sua)
    app_ui["btn_xoa"].config(command=on_xoa)
    app_ui["btn_search"].config(command=on_search)
    app_ui["btn_clear"].config(command=on_clear_search)
    app_ui["ent_search"].bind("<Return>", on_search)
    app_ui["cbo_filter"].bind("<<ComboboxSelected>>", on_search)

    # Thao tác trên bảng chính
    tree = app_ui["tree"]
    tree.bind("<ButtonRelease-1>", on_single_click)
    tree.bind("<Double-1>", on_double_click)


# ─── Entry point ─────────────────────────────────────

def chay_ung_dung():
    """Khởi chạy ứng dụng Quản lý Công thức Nấu ăn."""
    global app_root, app_ui
    logger.info("Khởi động Quản lý Công thức Nấu ăn Dashboard (GUI)")
    app_root = tk.Tk()
    app_ui = view.tao_giao_dien_chinh(app_root)
    _bind_events()
    _tai_du_lieu()
    app_root.mainloop()
    logger.info("Thoát ứng dụng Công thức Nấu ăn Dashboard (GUI)")
