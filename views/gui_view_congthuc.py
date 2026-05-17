"""
views/gui_view_congthuc.py
==========================
Giao diện GUI Tkinter cho bài toán Quản lý Công thức Nấu ăn.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from models.congthuc import LOAI_MON_LIST
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageTk

# ─── Màu sắc ─────────────────────────────────────────
COLOR_BG        = "#1E1E2E"
COLOR_SURFACE   = "#2A2A3E"
COLOR_PANEL     = "#313145"
COLOR_ACCENT    = "#7C3AED"
COLOR_ACCENT2   = "#10B981"
COLOR_WARN      = "#F59E0B"
COLOR_DANGER    = "#EF4444"
COLOR_TEXT      = "#E2E8F0"
COLOR_MUTED     = "#94A3B8"
COLOR_BORDER    = "#3F3F5A"
COLOR_ROW_ODD   = "#252538"
COLOR_ROW_EVEN  = "#2A2A3E"
COLOR_SEL       = "#4C1D95"


def _btn_style(style):
    """Cấu hình style cho các nút."""
    style.configure("Action.TButton",
        font=("Segoe UI", 9, "bold"),
        foreground=COLOR_TEXT,
        background=COLOR_ACCENT,
        borderwidth=0, relief="flat", padding=(10, 6))
    style.map("Action.TButton",
        background=[("active", "#6D28D9"), ("pressed", "#5B21B6")])

    style.configure("Danger.TButton",
        font=("Segoe UI", 9, "bold"),
        foreground="#fff",
        background=COLOR_DANGER,
        borderwidth=0, relief="flat", padding=(10, 6))
    style.map("Danger.TButton",
        background=[("active", "#DC2626"), ("pressed", "#B91C1C")])

    style.configure("Neutral.TButton",
        font=("Segoe UI", 9),
        foreground=COLOR_TEXT,
        background=COLOR_PANEL,
        borderwidth=0, relief="flat", padding=(10, 6))
    style.map("Neutral.TButton",
        background=[("active", COLOR_BORDER)])

    style.configure("Search.TButton",
        font=("Segoe UI", 9),
        foreground="#fff",
        background=COLOR_ACCENT2,
        borderwidth=0, relief="flat", padding=(8, 5))
    style.map("Search.TButton",
        background=[("active", "#059669")])


def sort_treeview(tree, col, reverse):
    """Sắp xếp Treeview khi click tiêu đề cột."""
    if col == "Chọn":
        return
    data = [(tree.set(k, col), k) for k in tree.get_children("")]
    try:
        data.sort(key=lambda t: float(t[0]), reverse=reverse)
    except ValueError:
        data.sort(key=lambda t: t[0].lower(), reverse=reverse)
    for i, (_, k) in enumerate(data):
        tree.move(k, "", i)
    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))


def tao_giao_dien_chinh(root):
    """
    Tạo giao diện chính của ứng dụng Quản lý Công thức Nấu ăn.

    Returns:
        dict: Các widget tham chiếu.
    """
    import os

    root.title("🍳 Quản lý Công thức Nấu ăn")
    root.geometry("1280x720")
    root.minsize(960, 600)
    root.configure(bg=COLOR_BG)

    # Icon
    try:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ico = os.path.join(base, "assets", "app_icon.ico")
        if os.path.exists(ico):
            root.iconbitmap(default=ico)
    except Exception:
        pass

    # ttk Style
    style = ttk.Style()
    style.theme_use("clam")
    _btn_style(style)
    style.configure("Treeview",
        font=("Segoe UI", 10),
        background=COLOR_ROW_EVEN,
        fieldbackground=COLOR_ROW_EVEN,
        foreground=COLOR_TEXT,
        rowheight=28,
        borderwidth=0)
    style.configure("Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        background=COLOR_SURFACE,
        foreground=COLOR_TEXT,
        relief="flat", padding=6)
    # Fix hover (active state) – theme clam mặc định tô trắng khi di chuột
    style.map("Treeview",
        background=[
            ("selected", COLOR_SEL),
            ("active",   COLOR_PANEL),     # nền hover: tím tối nhẹ
        ],
        foreground=[
            ("selected", "#fff"),
            ("active",   COLOR_TEXT),      # chữ hover: giữ màu sáng
        ])
    style.map("Treeview.Heading",
        background=[
            ("active", COLOR_BORDER),      # heading hover: viền tối
        ],
        foreground=[
            ("active", COLOR_TEXT),
        ])

    ui = {}

    # ═══════════════ HEADER BAR ═══════════════════════
    frame_header = tk.Frame(root, bg=COLOR_ACCENT, height=50)
    frame_header.pack(fill=tk.X)
    frame_header.pack_propagate(False)

    tk.Label(frame_header,
             text="🍳  Quản Lý Công Thức Nấu Ăn",
             font=("Segoe UI", 14, "bold"),
             bg=COLOR_ACCENT, fg="#fff").pack(side=tk.LEFT, padx=18, pady=10)

    # ═══════════════ TOOLBAR ══════════════════════════
    frame_toolbar = tk.Frame(root, bg=COLOR_SURFACE, pady=8, padx=12)
    frame_toolbar.pack(fill=tk.X)

    # --- Nút hành động trái ---
    frame_left = tk.Frame(frame_toolbar, bg=COLOR_SURFACE)
    frame_left.pack(side=tk.LEFT)

    ui["btn_them"] = ttk.Button(frame_left, text="＋ Thêm", style="Action.TButton")
    ui["btn_them"].pack(side=tk.LEFT, padx=3)

    ui["btn_sua"] = ttk.Button(frame_left, text="✏ Sửa", style="Neutral.TButton")
    ui["btn_sua"].pack(side=tk.LEFT, padx=3)

    ui["btn_xoa"] = ttk.Button(frame_left, text="🗑 Xóa", style="Danger.TButton")
    ui["btn_xoa"].pack(side=tk.LEFT, padx=3)

    ttk.Separator(frame_left, orient=tk.VERTICAL).pack(
        side=tk.LEFT, fill=tk.Y, padx=10, pady=4)

    ui["btn_thongke"] = ttk.Button(frame_left, text="📊 Thống kê", style="Neutral.TButton")
    ui["btn_thongke"].pack(side=tk.LEFT, padx=3)

    ui["btn_about"] = ttk.Button(frame_left, text="ℹ️ About", style="Neutral.TButton")
    ui["btn_about"].pack(side=tk.LEFT, padx=3)

    # --- Tìm kiếm bên phải ---
    frame_right = tk.Frame(frame_toolbar, bg=COLOR_SURFACE)
    frame_right.pack(side=tk.RIGHT)

    tk.Label(frame_right, text="Lọc theo loại:", bg=COLOR_SURFACE,
             fg=COLOR_MUTED, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))

    ui["cbo_filter"] = ttk.Combobox(frame_right,
        values=["Tất cả"] + LOAI_MON_LIST,
        state="readonly", width=13,
        font=("Segoe UI", 9))
    ui["cbo_filter"].set("Tất cả")
    ui["cbo_filter"].pack(side=tk.LEFT, padx=4)

    ttk.Separator(frame_right, orient=tk.VERTICAL).pack(
        side=tk.LEFT, fill=tk.Y, padx=8, pady=4)

    tk.Label(frame_right, text="🔍", bg=COLOR_SURFACE,
             fg=COLOR_MUTED, font=("Segoe UI", 11)).pack(side=tk.LEFT)

    ui["ent_search"] = ttk.Entry(frame_right, width=22, font=("Segoe UI", 9))
    ui["ent_search"].pack(side=tk.LEFT, padx=4)

    ui["btn_search"] = ttk.Button(frame_right, text="Tìm", style="Search.TButton")
    ui["btn_search"].pack(side=tk.LEFT, padx=2)

    ui["btn_clear"] = ttk.Button(frame_right, text="✖", style="Neutral.TButton", width=3)
    ui["btn_clear"].pack(side=tk.LEFT, padx=2)

    # ═══════════════ MAIN CONTENT (table) ════════════════
    frame_mid = tk.Frame(root, bg=COLOR_BG, padx=12, pady=6)
    frame_mid.pack(fill=tk.BOTH, expand=True)

    cols = ["Chọn", "STT", "Tên món", "Loại món", "TG (phút)"]
    ui["cols"] = cols

    tree = ttk.Treeview(frame_mid, columns=cols, show="headings")
    ui["tree"] = tree

    col_widths = {
        "Chọn": 50, "STT": 55, "Tên món": 420, "Loại món": 160, "TG (phút)": 110
    }
    col_anchor = {
        "Chọn": tk.CENTER, "STT": tk.CENTER, "Tên món": tk.W,
        "Loại món": tk.CENTER, "TG (phút)": tk.CENTER
    }
    for col in cols:
        if col == "Chọn":
            tree.heading(col, text="☐")
        else:
            tree.heading(col, text=col,
                         command=lambda _c=col: sort_treeview(tree, _c, False))
        tree.column(col, width=col_widths.get(col, 120),
                    anchor=col_anchor.get(col, tk.W),
                    minwidth=40)

    tree.tag_configure("odd",  background=COLOR_ROW_ODD,  foreground=COLOR_TEXT)
    tree.tag_configure("even", background=COLOR_ROW_EVEN, foreground=COLOR_TEXT)
    tree.pack(fill=tk.BOTH, expand=True)

    # ═══════════════ STATUS BAR ═══════════════════════
    frame_status = tk.Frame(root, bg=COLOR_SURFACE, pady=6, padx=14)
    frame_status.pack(fill=tk.X)

    ui["lbl_tong"] = tk.Label(frame_status,
        text="Tổng: 0 công thức",
        font=("Segoe UI", 10, "bold"),
        bg=COLOR_SURFACE, fg=COLOR_TEXT)
    ui["lbl_tong"].pack(side=tk.LEFT, padx=12)

    ui["lbl_tg_tb"] = tk.Label(frame_status,
        text="TG chuẩn bị TB: — phút",
        font=("Segoe UI", 10),
        bg=COLOR_SURFACE, fg=COLOR_MUTED)
    ui["lbl_tg_tb"].pack(side=tk.LEFT, padx=12)

    ui["lbl_hint"] = tk.Label(frame_status,
        text="💡 Double-click vào dòng để xem & sửa chi tiết",
        font=("Segoe UI", 9, "italic"),
        bg=COLOR_SURFACE, fg=COLOR_MUTED)
    ui["lbl_hint"].pack(side=tk.RIGHT, padx=12)

    return ui


# ─── Hiển thị bảng ───────────────────────────────────

def hien_thi_bang(ui, df):
    """Xóa dữ liệu cũ và nạp lại từ DataFrame."""
    tree = ui["tree"]
    tree.heading("Chọn", text="☐")
    for row in tree.get_children():
        tree.delete(row)

    if df is None or df.empty:
        return

    for idx, (_, row) in enumerate(df.iterrows(), start=1):
        tg = row.get("thoi_gian", 0)
        values = [
            "☐",
            str(idx),
            row.get("ten_mon", ""),
            row.get("loai_mon", ""),
            str(tg),
        ]
        tag = "odd" if idx % 2 else "even"
        tree.insert("", tk.END, values=values, tags=(tag,))


def cap_nhat_status(ui, stats):
    """Cập nhật thanh trạng thái phía dưới."""
    tong = stats.get("tong_ct", 0)
    tg_tb = stats.get("tg_trung_binh", 0)
    ui["lbl_tong"].config(text=f"Tổng: {tong} công thức")
    ui["lbl_tg_tb"].config(
        text=f"TG chuẩn bị TB: {tg_tb:.1f} phút" if tong else "TG chuẩn bị TB: — phút")


# ─── Form Thêm / Sửa ─────────────────────────────────

def hien_thi_form(parent, is_edit=False, current_data=None):
    """
    Hiển thị dialog nhập liệu Thêm / Sửa công thức.

    Returns:
        dict | None: Dữ liệu người dùng nhập, hoặc None nếu Hủy.
    """
    top = tk.Toplevel(parent)
    top.title("Sửa Công thức" if is_edit else "Thêm Công thức")
    top.configure(bg=COLOR_BG)
    top.resizable(True, True)
    top.grab_set()

    result = []

    # Tiêu đề form
    tk.Label(top,
             text=("✏  Sửa Công thức" if is_edit else "＋  Thêm Công thức mới"),
             font=("Segoe UI", 13, "bold"),
             bg=COLOR_ACCENT, fg="#fff").pack(fill=tk.X, pady=0)

    main = tk.Frame(top, bg=COLOR_BG, padx=22, pady=16)
    main.pack(fill=tk.BOTH, expand=True)

    # Helper tạo nhãn + widget
    def lbl(txt, row):
        tk.Label(main, text=txt, font=("Segoe UI", 9, "bold"),
                 bg=COLOR_BG, fg=COLOR_MUTED,
                 anchor="w").grid(row=row, column=0, sticky="w", pady=(10, 2))

    lbl("Tên món ăn  (*)", 0)
    ent_ten = ttk.Entry(main, width=48, font=("Segoe UI", 10))
    ent_ten.grid(row=1, column=0, sticky="ew", pady=(0, 2))

    lbl("Loại món ăn  (*)", 2)
    cbo_loai = ttk.Combobox(main, values=LOAI_MON_LIST, state="readonly",
                             font=("Segoe UI", 10), width=46)
    cbo_loai.set(LOAI_MON_LIST[0])
    cbo_loai.grid(row=3, column=0, sticky="ew", pady=(0, 2))

    lbl("Nguyên liệu  (ngăn cách bằng dấu  |  , vd: Gạo | Muối | Nước)", 4)
    txt_nl = tk.Text(main, height=3, width=50, font=("Segoe UI", 10),
                     bg=COLOR_SURFACE, fg=COLOR_TEXT,
                     insertbackground=COLOR_TEXT, relief="flat",
                     highlightthickness=1, highlightcolor=COLOR_ACCENT)
    txt_nl.grid(row=5, column=0, sticky="ew", pady=(0, 2))

    lbl("Định lượng    (ngăn cách bằng dấu  |  , vd: 200g | 5g | 500ml)", 6)
    txt_dl = tk.Text(main, height=3, width=50, font=("Segoe UI", 10),
                     bg=COLOR_SURFACE, fg=COLOR_TEXT,
                     insertbackground=COLOR_TEXT, relief="flat",
                     highlightthickness=1, highlightcolor=COLOR_ACCENT)
    txt_dl.grid(row=7, column=0, sticky="ew", pady=(0, 2))

    lbl("Thời gian chuẩn bị  (phút)  (*)", 8)
    ent_tg = ttk.Entry(main, width=14, font=("Segoe UI", 10))
    ent_tg.grid(row=9, column=0, sticky="w", pady=(0, 2))

    lbl("Cách làm (mỗi bước một dòng)", 10)
    txt_cl = tk.Text(main, height=6, width=50, font=("Segoe UI", 10),
                     bg=COLOR_SURFACE, fg=COLOR_TEXT,
                     insertbackground=COLOR_TEXT, relief="flat",
                     highlightthickness=1, highlightcolor=COLOR_ACCENT)
    txt_cl.grid(row=11, column=0, sticky="ew", pady=(0, 2))

    lbl("💡 Lưu ý khi nấu (mỗi ý một dòng)", 12)
    txt_ly = tk.Text(main, height=4, width=50, font=("Segoe UI", 10),
                     bg=COLOR_SURFACE, fg=COLOR_TEXT,
                     insertbackground=COLOR_TEXT, relief="flat",
                     highlightthickness=1, highlightcolor=COLOR_WARN)
    txt_ly.grid(row=13, column=0, sticky="ew", pady=(0, 2))

    lbl("Hình ảnh (chọn file .png, .jpg)", 14)
    frame_img = tk.Frame(main, bg=COLOR_BG)
    frame_img.grid(row=15, column=0, sticky="ew", pady=(0, 2))
    ent_img = ttk.Entry(frame_img, font=("Segoe UI", 10))
    ent_img.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    def on_choose_img():
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            ent_img.delete(0, tk.END)
            ent_img.insert(0, path)
    ttk.Button(frame_img, text="📂 Chọn", style="Neutral.TButton", command=on_choose_img).pack(side=tk.LEFT)

    main.columnconfigure(0, weight=1)

    # Điền sẵn dữ liệu khi sửa
    if is_edit and current_data:
        ent_ten.insert(0, current_data.get("ten_mon", ""))
        cbo_loai.set(current_data.get("loai_mon", LOAI_MON_LIST[0]))
        nl = current_data.get("nguyen_lieu", "")
        txt_nl.insert("1.0", nl)
        dl = current_data.get("dinh_luong", "")
        txt_dl.insert("1.0", dl)
        ent_tg.insert(0, str(current_data.get("thoi_gian", 0)))
        txt_cl.insert("1.0", str(current_data.get("cach_lam", "")))
        txt_ly.insert("1.0", str(current_data.get("luu_y", "")))
        ent_img.insert(0, str(current_data.get("hinh_anh", "")))

    # Thông báo lỗi
    lbl_err = tk.Label(main, text="", font=("Segoe UI", 9),
                       bg=COLOR_BG, fg=COLOR_DANGER)
    lbl_err.grid(row=16, column=0, sticky="w", pady=(4, 0))

    def on_luu():
        ten = ent_ten.get().strip()
        loai = cbo_loai.get()
        nl = txt_nl.get("1.0", tk.END).strip()
        dl = txt_dl.get("1.0", tk.END).strip()
        tg_str = ent_tg.get().strip()
        cl = txt_cl.get("1.0", tk.END).strip()
        ly = txt_ly.get("1.0", tk.END).strip()
        img = ent_img.get().strip()

        if not ten:
            lbl_err.config(text="⚠ Mời bạn nhập Tên món ăn!")
            ent_ten.focus_set()
            return
        if not loai:
            lbl_err.config(text="⚠ Mời bạn chọn Loại món ăn!")
            return
        if not nl:
            lbl_err.config(text="⚠ Mời bạn nhập Nguyên liệu!")
            txt_nl.focus_set()
            return
        if not dl:
            lbl_err.config(text="⚠ Mời bạn nhập Định lượng!")
            txt_dl.focus_set()
            return
        if not tg_str:
            lbl_err.config(text="⚠ Mời bạn nhập Thời gian chuẩn bị!")
            ent_tg.focus_set()
            return
        try:
            tg = int(tg_str)
            if tg < 0:
                raise ValueError
        except ValueError:
            lbl_err.config(text="⚠ Thời gian phải là số nguyên >= 0!")
            ent_tg.focus_set()
            return

        result.append({
            "ten_mon": ten,
            "loai_mon": loai,
            "nguyen_lieu": nl,
            "dinh_luong": dl,
            "thoi_gian": tg,
            "cach_lam": cl,
            "luu_y": ly,
            "hinh_anh": img,
        })
        top.destroy()

    # Buttons
    frame_btn = tk.Frame(main, bg=COLOR_BG)
    frame_btn.grid(row=17, column=0, sticky="e", pady=(16, 0))

    ttk.Button(frame_btn, text="💾 Lưu", style="Action.TButton",
               command=on_luu).pack(side=tk.LEFT, padx=6)
    ttk.Button(frame_btn, text="Hủy", style="Neutral.TButton",
               command=top.destroy).pack(side=tk.LEFT, padx=6)

    # Canh giữa
    top.update_idletasks()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    px, py = parent.winfo_x(), parent.winfo_y()
    tw, th = top.winfo_reqwidth(), top.winfo_reqheight()
    top.geometry(f"+{px + (pw - tw)//2}+{py + (ph - th)//2}")

    top.wait_window()
    return result[0] if result else None


# ─── Cửa sổ Chi tiết món ăn ──────────────────────────

def hien_thi_chi_tiet(parent, data):
    """Hiển thị cửa sổ xem chi tiết món ăn (hướng dẫn từng bước + lưu ý)."""
    top = tk.Toplevel(parent)
    top.title(f"📖 Chi tiết: {data.get('ten_mon', '')}")
    top.configure(bg=COLOR_BG)
    top.geometry("820x680")
    top.minsize(640, 480)
    top.grab_set()

    # ── Container cuộn được ───────────────────────────
    canvas = tk.Canvas(top, bg=COLOR_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
    main = tk.Frame(canvas, bg=COLOR_BG)

    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas_window = canvas.create_window((0, 0), window=main, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    main.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ── Tên món ──────────────────────────────────────
    tk.Label(main, text=data.get("ten_mon", ""),
             font=("Segoe UI", 24, "bold"),
             bg=COLOR_BG, fg=COLOR_ACCENT,
             wraplength=760, justify="left").pack(anchor="w", padx=24, pady=(22, 4))

    # Đường kẻ trang trí
    sep_line = tk.Frame(main, bg=COLOR_ACCENT, height=3)
    sep_line.pack(fill=tk.X, padx=24, pady=(0, 10))

    # ── Badge thông tin ───────────────────────────────
    f_badge = tk.Frame(main, bg=COLOR_BG)
    f_badge.pack(anchor="w", padx=24, pady=(0, 8))
    tk.Label(f_badge,
             text=f"📂  {data.get('loai_mon', 'Khác')}",
             font=("Segoe UI", 10, "bold"),
             bg=COLOR_SURFACE, fg=COLOR_MUTED,
             padx=12, pady=5).pack(side=tk.LEFT, padx=(0, 10))
    tk.Label(f_badge,
             text=f"⏱  {data.get('thoi_gian', 0)} phút chuẩn bị",
             font=("Segoe UI", 10, "bold"),
             bg=COLOR_SURFACE, fg=COLOR_MUTED,
             padx=12, pady=5).pack(side=tk.LEFT, padx=(0, 10))
    # Badge số khẩu phần ước tính (dựa trên định lượng nếu có)
    tk.Label(f_badge,
             text="👥  Cho ~2–4 người",
             font=("Segoe UI", 10, "bold"),
             bg=COLOR_SURFACE, fg=COLOR_MUTED,
             padx=12, pady=5).pack(side=tk.LEFT)

    # ── Nguyên liệu & Định lượng ─────────────────────
    tk.Label(main, text="🥬  Nguyên liệu & Định lượng",
             font=("Segoe UI", 15, "bold"),
             bg=COLOR_BG, fg=COLOR_ACCENT2).pack(anchor="w", padx=24, pady=(18, 6))

    nl_raw = str(data.get("nguyen_lieu", "")).strip()
    dl_raw = str(data.get("dinh_luong", "")).strip()
    nl_items = [s.strip() for s in nl_raw.split("|") if s.strip()] if nl_raw else []
    dl_items = [s.strip() for s in dl_raw.split("|") if s.strip()] if dl_raw else []

    if nl_items:
        # Container nguyên liệu
        ing_container = tk.Frame(main, bg=COLOR_PANEL,
                                  highlightbackground=COLOR_BORDER,
                                  highlightthickness=1)
        ing_container.pack(fill=tk.X, padx=24, pady=(0, 4))

        # Header bảng
        header_f = tk.Frame(ing_container, bg=COLOR_SURFACE)
        header_f.pack(fill=tk.X)
        tk.Label(header_f, text="  #",
                 font=("Segoe UI", 10, "bold"),
                 bg=COLOR_SURFACE, fg=COLOR_MUTED,
                 width=4, anchor="center").pack(side=tk.LEFT, padx=(4, 0))
        tk.Label(header_f, text="Nguyên liệu",
                 font=("Segoe UI", 10, "bold"),
                 bg=COLOR_SURFACE, fg=COLOR_MUTED,
                 anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12)
        tk.Label(header_f, text="Định lượng",
                 font=("Segoe UI", 10, "bold"),
                 bg=COLOR_SURFACE, fg=COLOR_MUTED,
                 width=18, anchor="center").pack(side=tk.RIGHT, padx=12)

        for i, nl in enumerate(nl_items):
            dl = dl_items[i] if i < len(dl_items) else "—"
            row_bg = COLOR_ROW_ODD if i % 2 == 0 else COLOR_ROW_EVEN
            row_f = tk.Frame(ing_container, bg=row_bg)
            row_f.pack(fill=tk.X)
            tk.Label(row_f, text=str(i + 1),
                     font=("Segoe UI", 10),
                     bg=row_bg, fg=COLOR_MUTED,
                     width=4, anchor="center").pack(side=tk.LEFT, padx=(4, 0))
            tk.Label(row_f, text=nl,
                     font=("Segoe UI", 10),
                     bg=row_bg, fg=COLOR_TEXT,
                     anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12, pady=4)
            tk.Label(row_f, text=dl,
                     font=("Segoe UI", 10, "bold"),
                     bg=row_bg, fg=COLOR_ACCENT2,
                     width=18, anchor="center").pack(side=tk.RIGHT, padx=12, pady=4)
    else:
        tk.Label(main, text="Chưa có thông tin nguyên liệu.",
                 font=("Segoe UI", 11, "italic"),
                 bg=COLOR_BG, fg=COLOR_MUTED).pack(anchor="w", padx=34, pady=4)

    # ── Hình ảnh (nếu có) ─────────────────────────────
    img_path = str(data.get("hinh_anh", "")).strip()
    if img_path and os.path.exists(img_path):
        try:
            img = Image.open(img_path)
            img.thumbnail((500, 320))
            photo = ImageTk.PhotoImage(img)
            lbl_img = tk.Label(main, image=photo, bg=COLOR_BG)
            lbl_img.image = photo
            lbl_img.pack(anchor="w", padx=24, pady=10)
        except Exception:
            tk.Label(main, text="⚠ Không thể tải hình ảnh",
                     fg=COLOR_DANGER, bg=COLOR_BG).pack(anchor="w", padx=24)

    # ── Hướng dẫn thực hiện ───────────────────────────
    tk.Label(main, text="🍳  Hướng dẫn thực hiện",
             font=("Segoe UI", 15, "bold"),
             bg=COLOR_BG, fg=COLOR_TEXT).pack(anchor="w", padx=24, pady=(18, 6))

    cach_lam_raw = str(data.get("cach_lam", "")).strip()

    # Tách từng bước (mỗi dòng = 1 bước)
    step_lines = [s.strip() for s in cach_lam_raw.splitlines() if s.strip()]

    if not step_lines and not cach_lam_raw:
        tk.Label(main,
                 text="Chưa có hướng dẫn cụ thể.",
                 font=("Segoe UI", 11, "italic"),
                 bg=COLOR_BG, fg=COLOR_MUTED).pack(anchor="w", padx=34, pady=4)
    else:
        lines_to_show = step_lines if step_lines else [cach_lam_raw]
        step_num = 0
        for line in lines_to_show:
            # Bỏ tiền tố số bước cũ nếu người dùng đã tự đánh (vd: "1.", "Bước 1:")
            import re
            clean = re.sub(r'^(bước\s*\d+[:\.]?|\d+[:\.])\s*', '', line, flags=re.IGNORECASE).strip()
            if not clean:
                continue
            step_num += 1

            # Card mỗi bước
            card = tk.Frame(main, bg=COLOR_PANEL,
                            highlightbackground=COLOR_BORDER,
                            highlightthickness=1)
            card.pack(fill=tk.X, padx=24, pady=4)

            # Số bước – hình tròn màu accent
            badge_frame = tk.Frame(card, bg=COLOR_ACCENT, width=34, height=34)
            badge_frame.pack(side=tk.LEFT, padx=(12, 0), pady=10)
            badge_frame.pack_propagate(False)
            tk.Label(badge_frame, text=str(step_num),
                     font=("Segoe UI", 11, "bold"),
                     bg=COLOR_ACCENT, fg="#fff").place(relx=0.5, rely=0.5, anchor="center")

            # Nội dung bước
            tk.Label(card, text=clean,
                     font=("Segoe UI", 11),
                     bg=COLOR_PANEL, fg=COLOR_TEXT,
                     justify="left", wraplength=680,
                     anchor="w").pack(side=tk.LEFT, padx=14, pady=10, fill=tk.X, expand=True)

    # ── Lưu ý khi nấu (từ cột luu_y trong DB) ───────────────────────
    tk.Label(main, text="💡  Lưu ý khi nấu",
             font=("Segoe UI", 15, "bold"),
             bg=COLOR_BG, fg=COLOR_WARN).pack(anchor="w", padx=24, pady=(22, 6))

    note_panel = tk.Frame(main, bg="#2D2B1A",
                          highlightbackground=COLOR_WARN,
                          highlightthickness=1)
    note_panel.pack(fill=tk.X, padx=24, pady=(0, 16))

    luu_y_raw = str(data.get("luu_y", "")).strip()
    luu_y_lines = [s.strip() for s in luu_y_raw.splitlines() if s.strip()]

    if luu_y_lines:
        for note in luu_y_lines:
            tk.Label(note_panel,
                     text=f"⚠  {note}",
                     font=("Segoe UI", 11),
                     bg="#2D2B1A", fg=COLOR_WARN,
                     justify="left", wraplength=710,
                     anchor="w").pack(anchor="w", padx=16, pady=5)
    else:
        # Lưu ý mặc định khi chưa có dữ liệu
        default_notes = [
            "Nên chuẩn bị đầy đủ nguyên liệu và dụng cụ trước khi bắt đầu nấu.",
            "Điều chỉnh gia vị theo khẩu vị của gia đình (mặn, nhạt, cay).",
            "Kiểm tra độ chín của thức ăn kỹ lưỡng trước khi dùng.",
            "Các nguyên liệu tươi sống cần được rửa sạch và để ráo nước.",
        ]
        for note in default_notes:
            tk.Label(note_panel,
                     text=f"▸  {note}",
                     font=("Segoe UI", 10),
                     bg="#2D2B1A", fg=COLOR_WARN,
                     justify="left", wraplength=710,
                     anchor="w").pack(anchor="w", padx=16, pady=3)

    tk.Label(main, text="", bg=COLOR_BG).pack(pady=8)

    def _on_destroy(event):
        if event.widget == top:
            canvas.unbind_all("<MouseWheel>")
    top.bind("<Destroy>", _on_destroy)


# ─── Cửa sổ Thống kê ─────────────────────────────────

def hien_thi_thong_ke(parent, stats):
    """Hiển thị cửa sổ thống kê chi tiết với biểu đồ matplotlib."""
    top = tk.Toplevel(parent)
    top.title("📊 Thống kê Công thức Nấu ăn")
    top.configure(bg=COLOR_BG)
    
    # Cho phép resize, định nghĩa kích thước
    top.resizable(True, True)
    top.minsize(850, 650)
    
    top.grab_set()

    tk.Label(top,
             text="📊  Thống kê Công thức Nấu ăn",
             font=("Segoe UI", 13, "bold"),
             bg=COLOR_ACCENT, fg="#fff").pack(fill=tk.X)

    if not stats:
        tk.Label(top, text="\nChưa có dữ liệu để thống kê.",
                 font=("Segoe UI", 11),
                 bg=COLOR_BG, fg=COLOR_MUTED).pack(pady=30, padx=30)
        ttk.Button(top, text="Đóng", style="Neutral.TButton",
                   command=top.destroy).pack(pady=10)
        return

    # Frame chính chứa Canvas và Label tổng quan
    container = tk.Frame(top, bg=COLOR_BG)
    container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Frame hiển thị dạng số (Tổng quan)
    frame_text = tk.Frame(container, bg=COLOR_BG)
    frame_text.pack(fill=tk.X, pady=(0, 15))

    def kv(parent_frame, k, v):
        f = tk.Frame(parent_frame, bg=COLOR_SURFACE, padx=10, pady=8)
        f.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Label(f, text=k, font=("Segoe UI", 9), bg=COLOR_SURFACE,
                 fg=COLOR_MUTED).pack(anchor="w")
        tk.Label(f, text=str(v), font=("Segoe UI", 12, "bold"),
                 bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(anchor="w")

    kv(frame_text, "Tổng số công thức:", stats.get("tong_ct", 0))
    kv(frame_text, "Thời gian TB:", f"{stats.get('tg_trung_binh', 0):.1f} phút")
    kv(frame_text, "Nhanh nhất:", f"{stats.get('tg_min', 0)} phút")
    kv(frame_text, "Lâu nhất:", f"{stats.get('tg_max', 0)} phút")

    # Tạo biểu đồ với Matplotlib
    plt.style.use("dark_background")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), facecolor=COLOR_BG)
    fig.subplots_adjust(bottom=0.2, wspace=0.3)

    # Biểu đồ 1: Thời gian trung bình theo loại món (Bar chart)
    tg_loai = stats.get("tg_theo_loai", {})
    if tg_loai:
        labels1 = list(tg_loai.keys())
        values1 = list(tg_loai.values())
        bars = ax1.bar(labels1, values1, color=COLOR_ACCENT)
        ax1.set_title("TG Chuẩn bị TB theo Loại (phút)", color=COLOR_TEXT, pad=10)
        ax1.tick_params(axis='x', rotation=45, colors=COLOR_MUTED)
        ax1.tick_params(axis='y', colors=COLOR_MUTED)
        ax1.set_facecolor(COLOR_SURFACE)
        ax1.grid(axis='y', linestyle='--', alpha=0.3)
        # Thêm text giá trị lên cột
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', color=COLOR_TEXT, fontsize=9)
    else:
        ax1.text(0.5, 0.5, "Không có dữ liệu", ha='center', va='center')
        ax1.set_title("TG Chuẩn bị TB theo Loại")

    # Biểu đồ 2: Top nguyên liệu (Pie chart)
    top_nl = stats.get("top_nguyen_lieu", {})
    if top_nl:
        labels2 = list(top_nl.keys())[:7]  # Lấy top 7
        values2 = list(top_nl.values())[:7]
        wedges, texts, autotexts = ax2.pie(values2, labels=labels2, autopct='%1.1f%%',
                                           startangle=90, textprops=dict(color=COLOR_TEXT),
                                           colors=plt.cm.viridis(np.linspace(0.2, 0.9, len(labels2))))
        ax2.set_title("Top 7 Nguyên liệu phổ biến", color=COLOR_TEXT, pad=10)
    else:
        ax2.text(0.5, 0.5, "Không có dữ liệu", ha='center', va='center')
        ax2.set_title("Top Nguyên liệu phổ biến")

    # Đưa Figure vào Tkinter
    canvas = FigureCanvasTkAgg(fig, master=container)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)

    # Nút đóng đặt ngoài canvas, ở dưới cùng của cửa sổ popup
    frame_btn = tk.Frame(top, bg=COLOR_BG)
    frame_btn.pack(fill=tk.X, pady=(10, 10))
    
    ttk.Button(frame_btn, text="Đóng", style="Neutral.TButton",
               command=top.destroy).pack()

    # Canh giữa màn hình
    top.update_idletasks()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    px, py = parent.winfo_x(), parent.winfo_y()
    tw, th = top.winfo_reqwidth(), top.winfo_reqheight()
    
    x = px + (pw - tw) // 2
    y = py + (ph - th) // 2
    top.geometry(f"+{x}+{y}")

    # Xóa memory khi đóng cửa sổ
    def _on_destroy(event):
        if event.widget == top:
            plt.close(fig)
             
    top.bind("<Destroy>", _on_destroy)

    top.wait_window()
