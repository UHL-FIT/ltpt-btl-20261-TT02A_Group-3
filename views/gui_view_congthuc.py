"""
views/gui_view_congthuc.py
==========================
Giao diện GUI Tkinter cho bài toán Quản lý Công thức Nấu ăn.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from models.congthuc import LOAI_MON_LIST

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
    import sys, os

    root.title("🍳 Quản lý Công thức Nấu ăn")
    root.geometry("1280x720")
    root.minsize(960, 600)
    root.configure(bg=COLOR_BG)

    # Icon
    try:
        base = sys._MEIPASS if getattr(sys, "frozen", False) else \
               os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    style.map("Treeview",
        background=[("selected", COLOR_SEL)],
        foreground=[("selected", "#fff")])

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

    ui["btn_import"] = ttk.Button(frame_left, text="📂 Import CSV", style="Neutral.TButton")
    ui["btn_import"].pack(side=tk.LEFT, padx=3)

    ui["btn_export"] = ttk.Button(frame_left, text="💾 Export CSV", style="Neutral.TButton")
    ui["btn_export"].pack(side=tk.LEFT, padx=3)

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

    # ═══════════════ MAIN CONTENT (table + scrollbar) ═
    frame_mid = tk.Frame(root, bg=COLOR_BG, padx=12, pady=6)
    frame_mid.pack(fill=tk.BOTH, expand=True)

    scroll_y = ttk.Scrollbar(frame_mid)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    scroll_x = ttk.Scrollbar(frame_mid, orient=tk.HORIZONTAL)
    scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    cols = ["Chọn", "STT", "Tên món", "Loại món", "Nguyên liệu", "Định lượng", "TG (phút)"]
    ui["cols"] = cols

    tree = ttk.Treeview(frame_mid, columns=cols, show="headings",
                        yscrollcommand=scroll_y.set,
                        xscrollcommand=scroll_x.set)
    ui["tree"] = tree
    scroll_y.config(command=tree.yview)
    scroll_x.config(command=tree.xview)

    col_widths = {
        "Chọn": 45, "STT": 45, "Tên món": 200, "Loại món": 110,
        "Nguyên liệu": 280, "Định lượng": 200, "TG (phút)": 90
    }
    col_anchor = {
        "Chọn": tk.CENTER, "STT": tk.CENTER, "Tên món": tk.W,
        "Loại món": tk.CENTER, "Nguyên liệu": tk.W,
        "Định lượng": tk.W, "TG (phút)": tk.CENTER
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
        nl = row.get("nguyen_lieu", "")
        dl = row.get("dinh_luong", "")
        tg = row.get("thoi_gian", 0)
        values = [
            "☐",
            str(idx),
            row.get("ten_mon", ""),
            row.get("loai_mon", ""),
            nl.replace("|", " | ") if nl else "",
            dl.replace("|", " | ") if dl else "",
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

    # Thông báo lỗi
    lbl_err = tk.Label(main, text="", font=("Segoe UI", 9),
                       bg=COLOR_BG, fg=COLOR_DANGER)
    lbl_err.grid(row=10, column=0, sticky="w", pady=(4, 0))

    def on_luu():
        ten = ent_ten.get().strip()
        loai = cbo_loai.get()
        nl = txt_nl.get("1.0", tk.END).strip()
        dl = txt_dl.get("1.0", tk.END).strip()
        tg_str = ent_tg.get().strip()

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
        })
        top.destroy()

    # Buttons
    frame_btn = tk.Frame(main, bg=COLOR_BG)
    frame_btn.grid(row=11, column=0, sticky="e", pady=(16, 0))

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


# ─── Cửa sổ Thống kê ─────────────────────────────────

def hien_thi_thong_ke(parent, stats):
    """Hiển thị cửa sổ thống kê chi tiết."""
    top = tk.Toplevel(parent)
    top.title("📊 Thống kê Công thức Nấu ăn")
    top.configure(bg=COLOR_BG)
    top.resizable(True, True)
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
        top.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        tw, th = top.winfo_reqwidth(), top.winfo_reqheight()
        top.geometry(f"+{px + (pw - tw)//2}+{py + (ph - th)//2}")
        return

    main = tk.Frame(top, bg=COLOR_BG, padx=20, pady=14)
    main.pack(fill=tk.BOTH, expand=True)

    def section(txt):
        tk.Label(main, text=txt,
                 font=("Segoe UI", 11, "bold"),
                 bg=COLOR_BG, fg=COLOR_ACCENT).pack(anchor="w", pady=(12, 4))

    def kv(k, v):
        f = tk.Frame(main, bg=COLOR_SURFACE, padx=10, pady=6)
        f.pack(fill=tk.X, pady=2)
        tk.Label(f, text=k, font=("Segoe UI", 9), bg=COLOR_SURFACE,
                 fg=COLOR_MUTED, width=32, anchor="w").pack(side=tk.LEFT)
        tk.Label(f, text=str(v), font=("Segoe UI", 10, "bold"),
                 bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(side=tk.LEFT)

    section("Tổng quan")
    kv("Tổng số công thức:", stats.get("tong_ct", 0))
    kv("Thời gian TB (tất cả):", f"{stats.get('tg_trung_binh', 0):.1f} phút")
    kv("Thời gian ngắn nhất:", f"{stats.get('tg_min', 0)} phút")
    kv("Thời gian dài nhất:", f"{stats.get('tg_max', 0)} phút")

    section("⏱  Thời gian chuẩn bị trung bình theo Loại món")
    tg_loai = stats.get("tg_theo_loai", {})
    if tg_loai:
        for loai, tg in sorted(tg_loai.items(), key=lambda x: -x[1]):
            kv(f"  {loai}:", f"{tg:.1f} phút")
    else:
        tk.Label(main, text="  (Không có dữ liệu)",
                 bg=COLOR_BG, fg=COLOR_MUTED,
                 font=("Segoe UI", 9, "italic")).pack(anchor="w")

    section("🧄  Top nguyên liệu được dùng nhiều nhất")
    top_nl = stats.get("top_nguyen_lieu", {})
    if top_nl:
        for i, (nl, cnt) in enumerate(list(top_nl.items())[:10], 1):
            kv(f"  #{i}  {nl}:", f"{cnt} lần")
    else:
        tk.Label(main, text="  (Không có dữ liệu)",
                 bg=COLOR_BG, fg=COLOR_MUTED,
                 font=("Segoe UI", 9, "italic")).pack(anchor="w")

    ttk.Button(main, text="Đóng", style="Neutral.TButton",
               command=top.destroy).pack(pady=(18, 4))

    top.update_idletasks()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    px, py = parent.winfo_x(), parent.winfo_y()
    tw, th = top.winfo_reqwidth(), top.winfo_reqheight()
    top.geometry(f"+{px+(pw-tw)//2}+{py+(ph-th)//2}")
    top.wait_window()
