"""
controllers/gui_controller_congthuc.py
=======================================
Controller kết nối Model (congthuc) và View (gui_view_congthuc).
Thiết kế module-level (không dùng class) theo pattern của dự án.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
from models import congthuc as model
import views.gui_view_congthuc as view
from utils.logger import setup_logger

logger = setup_logger("ctrl_congthuc")

# ─── Module-level state ──────────────────────────────
app_df   = pd.DataFrame()
app_ui   = {}
app_root = None


# ─── Internal helpers ────────────────────────────────

def _tai_du_lieu():
    """Tải dữ liệu từ model và áp dụng bộ lọc rồi hiển thị."""
    global app_df
    app_df, ok = model.lay_danh_sach()
    if not ok:
        messagebox.showerror("Lỗi", "Không thể tải dữ liệu công thức.")
        return

    display_df = _apply_filter(app_df.copy())
    view.hien_thi_bang(app_ui, display_df)

    stats = model.thong_ke(display_df)
    view.cap_nhat_status(app_ui, stats)


def _apply_filter(df):
    """Lọc DataFrame theo từ khóa tìm kiếm và loại món."""
    if df is None or df.empty:
        return df

    loai = app_ui["cbo_filter"].get()
    if loai and loai != "Tất cả":
        df = df[df["loai_mon"] == loai]

    keyword = app_ui["ent_search"].get().strip().lower()
    if keyword:
        mask = df.apply(
            lambda r: r.astype(str).str.lower().str.contains(keyword).any(), axis=1)
        df = df[mask]

    return df


# ─── Event handlers ──────────────────────────────────

def on_search(*_):
    logger.info("Tìm kiếm.")
    display_df = _apply_filter(app_df.copy())
    view.hien_thi_bang(app_ui, display_df)
    stats = model.thong_ke(display_df)
    view.cap_nhat_status(app_ui, stats)


def on_clear_search():
    logger.info("Xóa bộ lọc.")
    app_ui["ent_search"].delete(0, tk.END)
    app_ui["cbo_filter"].set("Tất cả")
    _tai_du_lieu()


def on_them():
    global app_df
    logger.info("Mở form Thêm công thức.")
    data = view.hien_thi_form(app_root, is_edit=False)
    if data:
        app_df, ok, msg = model.them_cong_thuc(app_df, data)
        if ok:
            _tai_du_lieu()
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Lỗi", msg)


def on_sua():
    global app_df
    logger.info("Mở form Sửa công thức.")
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
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Lỗi", msg)


def on_xoa():
    global app_df
    logger.info("Xóa công thức.")
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
            _tai_du_lieu()
        else:
            messagebox.showerror("Lỗi", msg)


def on_import():
    global app_df
    logger.info("Import CSV.")
    filepath = filedialog.askopenfilename(
        title="Chọn file CSV công thức",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
    if not filepath:
        return
    try:
        df_import = pd.read_csv(filepath, dtype=str)
        required = {"ten_mon", "loai_mon", "thoi_gian"}
        if not required.issubset(df_import.columns):
            messagebox.showerror("Lỗi",
                f"File CSV phải có các cột: {', '.join(required)}")
            return
        count = 0
        for _, row in df_import.iterrows():
            data = {
                "ten_mon":     row.get("ten_mon", ""),
                "loai_mon":    row.get("loai_mon", "Khác"),
                "nguyen_lieu": row.get("nguyen_lieu", ""),
                "dinh_luong":  row.get("dinh_luong", ""),
                "thoi_gian":   row.get("thoi_gian", 0),
            }
            app_df, ok, _ = model.them_cong_thuc(app_df, data)
            if ok:
                count += 1
        _tai_du_lieu()
        messagebox.showinfo("Thành công", f"Đã import {count} công thức từ file.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể import: {e}")


def on_export():
    logger.info("Export CSV.")
    filepath = filedialog.asksaveasfilename(
        title="Lưu file CSV công thức",
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        initialfile="congthuc_export.csv")
    if not filepath:
        return
    try:
        app_df.to_csv(filepath, index=False, encoding="utf-8-sig")
        messagebox.showinfo("Thành công", f"Đã lưu tại:\n{filepath}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")


def on_thongke():
    logger.info("Mở cửa sổ thống kê.")
    stats = model.thong_ke(app_df)
    view.hien_thi_thong_ke(app_root, stats)


def on_about():
    logger.info("Mở About.")
    messagebox.showinfo("Giới thiệu",
        "🍳 PHẦN MỀM: QUẢN LÝ CÔNG THỨC NẤU ĂN\n"
        "─────────────────────────────────────\n"
        "🔹 Phiên bản  : 1.0.0\n"
        "🔹 Nhóm       : Nhóm 3 – LTPT BTL 2026-1\n"
        "🔹 Trường     : Đại học Hạ Long (UHL)\n"
        "🔹 Phát hành  : 10/05/2026\n"
        "─────────────────────────────────────\n"
        "Ứng dụng hỗ trợ lưu trữ, tìm kiếm\n"
        "và thống kê các công thức nấu ăn.")


def on_single_click(event):
    """Toggle checkbox khi click vào cột Chọn."""
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
    """Double-click vào dòng -> mở form sửa luôn."""
    tree = app_ui["tree"]
    if tree.identify_region(event.x, event.y) != "cell":
        return
    iid = tree.identify_row(event.y)
    if not iid:
        return
    # Đánh dấu dòng được chọn rồi gọi on_sua
    for i in tree.get_children():
        vals = list(tree.item(i, "values"))
        vals[0] = "☐"
        tree.item(i, values=vals)
    vals = list(tree.item(iid, "values"))
    vals[0] = "☑"
    tree.item(iid, values=vals)
    on_sua()


# ─── Bind events ─────────────────────────────────────

def _bind_events():
    app_ui["btn_them"].config(command=on_them)
    app_ui["btn_sua"].config(command=on_sua)
    app_ui["btn_xoa"].config(command=on_xoa)
    app_ui["btn_import"].config(command=on_import)
    app_ui["btn_export"].config(command=on_export)
    app_ui["btn_thongke"].config(command=on_thongke)
    app_ui["btn_about"].config(command=on_about)
    app_ui["btn_search"].config(command=on_search)
    app_ui["btn_clear"].config(command=on_clear_search)
    app_ui["ent_search"].bind("<Return>", on_search)
    app_ui["cbo_filter"].bind("<<ComboboxSelected>>", on_search)

    tree = app_ui["tree"]
    tree.bind("<ButtonRelease-1>", on_single_click)
    tree.bind("<Double-1>", on_double_click)


# ─── Entry point ─────────────────────────────────────

def chay_ung_dung():
    """Khởi chạy ứng dụng Quản lý Công thức Nấu ăn."""
    global app_root, app_ui
    logger.info("Khởi động Quản lý Công thức Nấu ăn (GUI)")
    app_root = tk.Tk()
    app_ui = view.tao_giao_dien_chinh(app_root)
    _bind_events()
    _tai_du_lieu()
    app_root.mainloop()
    logger.info("Thoát ứng dụng Công thức Nấu ăn (GUI)")
