"""
views/gui_view_congthuc.py
==========================
Giao diện GUI Tkinter cho bài toán Quản lý Công thức Nấu ăn.
Được thiết kế lại theo phong cách Dashboard hiện đại:
- Sidebar bên trái điều hướng linh hoạt.
- Content area bên phải chứa các trang tĩnh: Trang chủ (danh sách món), Thống kê (dashboard vẽ biểu đồ trực tiếp), Giới thiệu.
- Giao diện phẳng mịn, bo góc mềm mại, đổ bóng nhẹ, tông tím/xanh hiện đại.
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

# ─── Màu sắc chủ đạo (Modern Palette) ────────────────
COLOR_BG        = "#F8FAFC"  # Nền ứng dụng (Slate 50 - siêu sáng và sạch)
COLOR_SURFACE   = "#FFFFFF"  # Nền các thẻ card, bảng, sidebar (Trắng tinh khôi)
COLOR_PANEL     = "#F1F5F9"  # Nền phụ (Slate 100)
COLOR_BORDER    = "#E2E8F0"  # Màu viền (Slate 200)

COLOR_ACCENT    = "#7C3AED"  # Tím chủ đạo (Violet 600 - nút chính, active sidebar)
COLOR_ACCENT_BG = "#F5F3FF"  # Nền tím nhạt (Violet 50)
COLOR_ACCENT2   = "#059669"  # Xanh lục (Emerald 600 - tìm kiếm, điểm nhấn phụ)
COLOR_ACCENT2_BG= "#ECFDF5"  # Nền xanh lục nhạt

COLOR_WARN      = "#D97706"  # Vàng cam cảnh báo
COLOR_WARN_BG   = "#FEF3C7"  # Nền vàng nhạt
COLOR_DANGER    = "#DC2626"  # Đỏ nguy hiểm (nút xóa)
COLOR_DANGER_BG = "#FEF2F2"  # Nền đỏ nhạt

COLOR_TEXT      = "#1E293B"  # Chữ chính (Slate 800)
COLOR_MUTED     = "#64748B"  # Chữ phụ/nhạt (Slate 500)
COLOR_ROW_ODD   = "#FFFFFF"  # Bảng dòng lẻ
COLOR_ROW_EVEN  = "#F8FAFC"  # Bảng dòng chẵn
COLOR_SEL       = "#EDE9FE"  # Dòng được chọn trên bảng (tím nhạt)


def _btn_style(style):
    """Cấu hình style cho các nút bấm ttk để đồng bộ với theme mới."""
    style.configure("Action.TButton",
        font=("Segoe UI", 9, "bold"),
        foreground="#ffffff",
        background=COLOR_ACCENT,
        borderwidth=0, relief="flat", padding=(12, 6))
    style.map("Action.TButton",
        background=[("active", "#6D28D9"), ("pressed", "#5B21B6")])

    style.configure("Danger.TButton",
        font=("Segoe UI", 9, "bold"),
        foreground="#ffffff",
        background=COLOR_DANGER,
        borderwidth=0, relief="flat", padding=(12, 6))
    style.map("Danger.TButton",
        background=[("active", "#B91C1C"), ("pressed", "#991B1B")])

    style.configure("Neutral.TButton",
        font=("Segoe UI", 9, "bold"),
        foreground=COLOR_TEXT,
        background=COLOR_PANEL,
        borderwidth=0, relief="flat", padding=(12, 6))
    style.map("Neutral.TButton",
        background=[("active", "#E2E8F0")])

    style.configure("Search.TButton",
        font=("Segoe UI", 9, "bold"),
        foreground="#ffffff",
        background=COLOR_ACCENT2,
        borderwidth=0, relief="flat", padding=(10, 5))
    style.map("Search.TButton",
        background=[("active", "#047857")])


def sort_treeview(tree, col, reverse):
    """Sắp xếp Treeview khi click tiêu đề cột."""
    if col == "Chọn":
        return
    data = [(tree.set(k, col), k) for k in tree.get_children("")]
    try:
        # Thử sắp xếp theo số thực nếu là cột thời gian hoặc STT
        data.sort(key=lambda t: float(t[0]), reverse=reverse)
    except ValueError:
        # Nếu là chuỗi chữ thì sắp xếp theo bảng chữ cái không phân biệt hoa thường
        data.sort(key=lambda t: t[0].lower(), reverse=reverse)
    for i, (_, k) in enumerate(data):
        tree.move(k, "", i)
    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))


def switch_page(ui, page_name):
    """Chuyển đổi linh hoạt giữa các trang trong Content Area chính."""
    # Ẩn tất cả các trang
    ui["page_trang_chu"].pack_forget()
    ui["page_thong_ke"].pack_forget()
    ui["page_gioi_thieu"].pack_forget()

    # Reset trạng thái các nút menu sidebar về mặc định
    for btn in [ui["btn_trangchu"], ui["btn_thongke"], ui["btn_about"]]:
        btn.config(bg=COLOR_SURFACE, fg=COLOR_MUTED)

    # Hiển thị trang được chọn và làm nổi bật nút menu tương ứng
    if page_name == "trang_chu":
        ui["page_trang_chu"].pack(fill=tk.BOTH, expand=True)
        ui["btn_trangchu"].config(bg=COLOR_ACCENT_BG, fg=COLOR_ACCENT)
    elif page_name == "thong_ke":
        ui["page_thong_ke"].pack(fill=tk.BOTH, expand=True)
        ui["btn_thongke"].config(bg=COLOR_ACCENT_BG, fg=COLOR_ACCENT)
    elif page_name == "about":
        ui["page_gioi_thieu"].pack(fill=tk.BOTH, expand=True)
        ui["btn_about"].config(bg=COLOR_ACCENT_BG, fg=COLOR_ACCENT)


def tao_giao_dien_chinh(root):
    """
    Tạo giao diện chính của ứng dụng Quản lý Công thức Nấu ăn theo cấu trúc Dashboard:
    - Sidebar bên trái.
    - Content area bên phải với 3 trang chuyển đổi tĩnh.
    """
    root.title("🍳 Quản lý Công thức Nấu ăn - Dashboard")
    root.geometry("1280x760")
    root.minsize(1020, 660)
    root.configure(bg=COLOR_BG)

    # Icon ứng dụng
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
        background=COLOR_SURFACE,
        fieldbackground=COLOR_SURFACE,
        foreground=COLOR_TEXT,
        rowheight=32,
        borderwidth=0)
    
    style.configure("Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        background=COLOR_PANEL,
        foreground=COLOR_TEXT,
        relief="flat", padding=8)
    
    style.map("Treeview",
        background=[
            ("selected", COLOR_SEL),
            ("active",   COLOR_BG),
        ],
        foreground=[
            ("selected", COLOR_ACCENT),
            ("active",   COLOR_TEXT),
        ])
        
    style.map("Treeview.Heading",
        background=[("active", COLOR_BORDER)],
        foreground=[("active", COLOR_TEXT)])

    ui = {}

    # ═══════════════════════════════════════════════════
    # ─── SIDEBAR BÊN TRÁI (SIDEBAR) ────────────────────
    # ═══════════════════════════════════════════════════
    sidebar = tk.Frame(root, bg=COLOR_SURFACE, width=230, highlightbackground=COLOR_BORDER, highlightthickness=1)
    sidebar.pack(side=tk.LEFT, fill=tk.Y)
    sidebar.pack_propagate(False)

    # Logo / Brand ứng dụng
    brand_f = tk.Frame(sidebar, bg=COLOR_SURFACE, pady=24)
    brand_f.pack(fill=tk.X)
    tk.Label(brand_f, text="🍳  SmartRecipe", font=("Segoe UI", 16, "bold"), bg=COLOR_SURFACE, fg=COLOR_ACCENT).pack()
    tk.Label(brand_f, text="Quản lý Công thức Nấu ăn", font=("Segoe UI", 8, "bold"), bg=COLOR_SURFACE, fg=COLOR_MUTED).pack(pady=(2, 0))

    # Vạch chia nhẹ
    tk.Frame(sidebar, bg=COLOR_BORDER, height=1).pack(fill=tk.X, padx=16, pady=(0, 16))

    # Helper tạo nút Menu Sidebar
    def make_sidebar_btn(text, icon):
        btn = tk.Button(sidebar, text=f"  {icon}   {text}", font=("Segoe UI", 10, "bold"),
                        bg=COLOR_SURFACE, fg=COLOR_MUTED, anchor="w", padx=20, pady=12,
                        borderwidth=0, relief="flat", activebackground=COLOR_ACCENT_BG, activeforeground=COLOR_ACCENT,
                        cursor="hand2")
        btn.pack(fill=tk.X, padx=12, pady=4)
        return btn

    ui["btn_trangchu"] = make_sidebar_btn("Trang chủ", "🏠")
    ui["btn_thongke"] = make_sidebar_btn("Thống kê", "📊")
    ui["btn_about"] = make_sidebar_btn("Giới thiệu", "ℹ️")

    # Bản quyền nhỏ ở chân Sidebar
    footer_f = tk.Frame(sidebar, bg=COLOR_SURFACE, pady=16)
    footer_f.pack(side=tk.BOTTOM, fill=tk.X)
    tk.Label(footer_f, text="© 2026 Nhóm 3 - LTPT BTL", font=("Segoe UI", 8), bg=COLOR_SURFACE, fg=COLOR_MUTED).pack()

    # ═══════════════════════════════════════════════════
    # ─── VÙNG NỘI DUNG CHÍNH (CONTENT AREA - PHẢI) ─────
    # ═══════════════════════════════════════════════════
    content_area = tk.Frame(root, bg=COLOR_BG)
    content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ───────────────────────────────────────────────────
    # 🏠 1. TRANG CHỦ (Danh sách công thức)
    # ───────────────────────────────────────────────────
    page_trang_chu = tk.Frame(content_area, bg=COLOR_BG)
    ui["page_trang_chu"] = page_trang_chu

    # Header Trang chủ (Chứa ô tìm kiếm và bộ lọc)
    header_trang_chu = tk.Frame(page_trang_chu, bg=COLOR_SURFACE, height=60, highlightbackground=COLOR_BORDER, highlightthickness=1)
    header_trang_chu.pack(fill=tk.X)
    header_trang_chu.pack_propagate(False)

    tk.Label(header_trang_chu, text="Danh Sách Công Thức Nấu Ăn", font=("Segoe UI", 12, "bold"), bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(side=tk.LEFT, padx=18)

    # Vùng lọc & tìm kiếm bên phải header
    f_filter_search = tk.Frame(header_trang_chu, bg=COLOR_SURFACE)
    f_filter_search.pack(side=tk.RIGHT, padx=18)

    tk.Label(f_filter_search, text="Lọc loại:", bg=COLOR_SURFACE, fg=COLOR_MUTED, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
    ui["cbo_filter"] = ttk.Combobox(f_filter_search, values=["Tất cả"] + LOAI_MON_LIST, state="readonly", width=12, font=("Segoe UI", 9))
    ui["cbo_filter"].set("Tất cả")
    ui["cbo_filter"].pack(side=tk.LEFT, padx=4)

    tk.Frame(f_filter_search, bg=COLOR_BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=4)

    ui["ent_search"] = ttk.Entry(f_filter_search, width=20, font=("Segoe UI", 9))
    ui["ent_search"].pack(side=tk.LEFT, padx=4)

    ui["btn_search"] = ttk.Button(f_filter_search, text="Tìm", style="Search.TButton")
    ui["btn_search"].pack(side=tk.LEFT, padx=2)

    ui["btn_clear"] = ttk.Button(f_filter_search, text="✖", style="Neutral.TButton", width=3)
    ui["btn_clear"].pack(side=tk.LEFT, padx=2)

    # Vùng chứa bảng + thanh công cụ con
    body_trang_chu = tk.Frame(page_trang_chu, bg=COLOR_BG, padx=20, pady=16)
    body_trang_chu.pack(fill=tk.BOTH, expand=True)

    # Thanh công cụ con (Thêm, Sửa, Xóa nằm trực tiếp trên trang chủ)
    toolbar_sub = tk.Frame(body_trang_chu, bg=COLOR_BG)
    toolbar_sub.pack(fill=tk.X, pady=(0, 10))

    ui["btn_them"] = ttk.Button(toolbar_sub, text="＋ Thêm công thức", style="Action.TButton")
    ui["btn_them"].pack(side=tk.LEFT, padx=(0, 6))

    ui["btn_sua"] = ttk.Button(toolbar_sub, text="✏ Sửa công thức", style="Neutral.TButton")
    ui["btn_sua"].pack(side=tk.LEFT, padx=6)

    ui["btn_xoa"] = ttk.Button(toolbar_sub, text="🗑 Xóa", style="Danger.TButton")
    ui["btn_xoa"].pack(side=tk.LEFT, padx=6)

    # Bảng Treeview bọc trong khung Card
    table_card = tk.Frame(body_trang_chu, bg=COLOR_SURFACE, highlightbackground=COLOR_BORDER, highlightthickness=1)
    table_card.pack(fill=tk.BOTH, expand=True)

    cols = ["Chọn", "STT", "Tên món", "Loại món", "TG (phút)"]
    ui["cols"] = cols

    tree = ttk.Treeview(table_card, columns=cols, show="headings")
    ui["tree"] = tree

    col_widths = {"Chọn": 55, "STT": 60, "Tên món": 450, "Loại món": 180, "TG (phút)": 130}
    col_anchor = {"Chọn": tk.CENTER, "STT": tk.CENTER, "Tên món": tk.W, "Loại món": tk.CENTER, "TG (phút)": tk.CENTER}
    for col in cols:
        if col == "Chọn":
            tree.heading(col, text="☐")
        else:
            tree.heading(col, text=col, command=lambda _c=col: sort_treeview(tree, _c, False))
        tree.column(col, width=col_widths.get(col, 120), anchor=col_anchor.get(col, tk.W), minwidth=40)

    tree.tag_configure("odd",  background=COLOR_ROW_ODD,  foreground=COLOR_TEXT)
    tree.tag_configure("even", background=COLOR_ROW_EVEN, foreground=COLOR_TEXT)

    # Thanh cuộn dọc của bảng
    scrollbar_y = ttk.Scrollbar(table_card, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Thanh trạng thái (Status Bar)
    frame_status = tk.Frame(page_trang_chu, bg=COLOR_SURFACE, pady=10, padx=20, highlightbackground=COLOR_BORDER, highlightthickness=1)
    frame_status.pack(fill=tk.X)

    ui["lbl_tong"] = tk.Label(frame_status, text="Tổng: 0 công thức", font=("Segoe UI", 10, "bold"), bg=COLOR_SURFACE, fg=COLOR_TEXT)
    ui["lbl_tong"].pack(side=tk.LEFT, padx=12)

    ui["lbl_tg_tb"] = tk.Label(frame_status, text="TG chuẩn bị TB: — phút", font=("Segoe UI", 10), bg=COLOR_SURFACE, fg=COLOR_MUTED)
    ui["lbl_tg_tb"].pack(side=tk.LEFT, padx=12)

    tk.Label(frame_status, text="💡 Click đúp vào dòng để xem chi tiết hướng dẫn nấu", font=("Segoe UI", 9, "italic"), bg=COLOR_SURFACE, fg=COLOR_MUTED).pack(side=tk.RIGHT, padx=12)

    # ───────────────────────────────────────────────────
    # 📊 2. TRANG THỐNG KÊ (Dashboard trực tiếp)
    # ───────────────────────────────────────────────────
    page_thong_ke = tk.Frame(content_area, bg=COLOR_BG)
    ui["page_thong_ke"] = page_thong_ke

    header_thong_ke = tk.Frame(page_thong_ke, bg=COLOR_SURFACE, height=60, highlightbackground=COLOR_BORDER, highlightthickness=1)
    header_thong_ke.pack(fill=tk.X)
    header_thong_ke.pack_propagate(False)
    tk.Label(header_thong_ke, text="📊  Báo Cáo & Phân Tích Thống Kê", font=("Segoe UI", 12, "bold"), bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(side=tk.LEFT, padx=18)

    body_thong_ke = tk.Frame(page_thong_ke, bg=COLOR_BG, padx=20, pady=16)
    body_thong_ke.pack(fill=tk.BOTH, expand=True)

    # Thẻ thông số tổng quan số lượng (4 Cards)
    frame_cards = tk.Frame(body_thong_ke, bg=COLOR_BG)
    frame_cards.pack(fill=tk.X, pady=(0, 16))

    def create_stat_card(parent_frame, title, color_accent, row, col):
        card = tk.Frame(parent_frame, bg=COLOR_SURFACE, highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.grid(row=row, column=col, sticky="ew", padx=6, pady=4)
        
        # Vạch màu bên trái thẻ card để trang trí chuyên nghiệp
        indicator = tk.Frame(card, bg=color_accent, width=4)
        indicator.pack(side=tk.LEFT, fill=tk.Y)
        
        info_f = tk.Frame(card, bg=COLOR_SURFACE, padx=12, pady=10)
        info_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(info_f, text=title, font=("Segoe UI", 9, "bold"), bg=COLOR_SURFACE, fg=COLOR_MUTED).pack(anchor="w")
        lbl_val = tk.Label(info_f, text="—", font=("Segoe UI", 16, "bold"), bg=COLOR_SURFACE, fg=COLOR_TEXT)
        lbl_val.pack(anchor="w", pady=(4, 0))
        return lbl_val

    frame_cards.columnconfigure(0, weight=1)
    frame_cards.columnconfigure(1, weight=1)
    frame_cards.columnconfigure(2, weight=1)
    frame_cards.columnconfigure(3, weight=1)

    ui["lbl_stats_tong"] = create_stat_card(frame_cards, "Tổng số công thức:", COLOR_ACCENT, 0, 0)
    ui["lbl_stats_tb"]   = create_stat_card(frame_cards, "Thời gian chuẩn bị TB:", COLOR_ACCENT2, 0, 1)
    ui["lbl_stats_min"]  = create_stat_card(frame_cards, "Chuẩn bị nhanh nhất:", COLOR_WARN, 0, 2)
    ui["lbl_stats_max"]  = create_stat_card(frame_cards, "Chuẩn bị lâu nhất:", COLOR_DANGER, 0, 3)

    # Vùng chứa biểu đồ vẽ Matplotlib
    chart_card = tk.Frame(body_thong_ke, bg=COLOR_SURFACE, highlightbackground=COLOR_BORDER, highlightthickness=1)
    chart_card.pack(fill=tk.BOTH, expand=True)
    ui["stats_container"] = chart_card

    # ───────────────────────────────────────────────────
    # ℹ️ 3. TRANG GIỚI THIỆU (Giới thiệu / About)
    # ───────────────────────────────────────────────────
    page_gioi_thieu = tk.Frame(content_area, bg=COLOR_BG)
    ui["page_gioi_thieu"] = page_gioi_thieu

    header_gioi_thieu = tk.Frame(page_gioi_thieu, bg=COLOR_SURFACE, height=60, highlightbackground=COLOR_BORDER, highlightthickness=1)
    header_gioi_thieu.pack(fill=tk.X)
    header_gioi_thieu.pack_propagate(False)
    tk.Label(header_gioi_thieu, text="ℹ️  Giới Thiệu Ứng Dụng", font=("Segoe UI", 12, "bold"), bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(side=tk.LEFT, padx=18)

    body_about = tk.Frame(page_gioi_thieu, bg=COLOR_BG, padx=20, pady=24)
    body_about.pack(fill=tk.BOTH, expand=True)

    # Khung Card giới thiệu
    about_card = tk.Frame(body_about, bg=COLOR_SURFACE, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=40, pady=40)
    about_card.pack(fill=tk.BOTH, expand=True)

    tk.Label(about_card, text="🍳  PHẦN MỀM QUẢN LÝ CÔNG THỨC NẤU ĂN", font=("Segoe UI", 18, "bold"), bg=COLOR_SURFACE, fg=COLOR_ACCENT).pack(pady=(0, 16))
    
    sep_f = tk.Frame(about_card, bg=COLOR_BORDER, height=1)
    sep_f.pack(fill=tk.X, pady=(0, 24))

    # Thông tin chi tiết
    def add_info_row(parent, label, value):
        row = tk.Frame(parent, bg=COLOR_SURFACE, pady=6)
        row.pack(fill=tk.X)
        tk.Label(row, text=f"•  {label}", font=("Segoe UI", 10, "bold"), bg=COLOR_SURFACE, fg=COLOR_MUTED, width=18, anchor="w").pack(side=tk.LEFT)
        tk.Label(row, text=value, font=("Segoe UI", 10), bg=COLOR_SURFACE, fg=COLOR_TEXT, anchor="w").pack(side=tk.LEFT, padx=10)

    info_container = tk.Frame(about_card, bg=COLOR_SURFACE)
    info_container.pack(fill=tk.X)

    add_info_row(info_container, "Phiên bản", "1.0.0 (Dashboard Edition)")
    add_info_row(info_container, "Nhóm thực hiện", "Nhóm 3 – LTPT BTL 2026-1")
    add_info_row(info_container, "Trường đào tạo", "Trường Đại học Hạ Long (UHL)")
    add_info_row(info_container, "Ngày phát hành", "10/05/2026")
    add_info_row(info_container, "Công nghệ sử dụng", "Python, Tkinter (GUI), SQLite3 (DB), Pandas & NumPy, Matplotlib")

    tk.Frame(about_card, bg=COLOR_BORDER, height=1).pack(fill=tk.X, pady=24)

    # Mô tả thêm
    desc_txt = (
        "Ứng dụng hỗ trợ ghi nhớ, lưu trữ thông tin, tìm kiếm thông minh đa từ khóa không dấu "
        "và phân tích thống kê chi tiết các công thức nấu ăn. Giao diện được tối ưu hóa cho trải nghiệm "
        "người dùng mượt mà, trực quan và hiện đại."
    )
    tk.Label(about_card, text=desc_txt, font=("Segoe UI", 10, "italic"), bg=COLOR_SURFACE, fg=COLOR_MUTED, wraplength=680, justify="center").pack(pady=10)

    # Thiết lập trang mặc định ban đầu là Trang chủ
    switch_page(ui, "trang_chu")

    return ui


# ─── Hiển thị dữ liệu lên bảng ───────────────────────

def hien_thi_bang(ui, df):
    """Xóa dữ liệu cũ và nạp lại từ DataFrame vào bảng Treeview."""
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
    """Cập nhật các số liệu ở thanh trạng thái dưới bảng Trang chủ."""
    tong = stats.get("tong_ct", 0)
    tg_tb = stats.get("tg_trung_binh", 0)
    ui["lbl_tong"].config(text=f"Tổng: {tong} công thức")
    ui["lbl_tg_tb"].config(
        text=f"TG chuẩn bị TB: {tg_tb:.1f} phút" if tong else "TG chuẩn bị TB: — phút")


def cap_nhat_trang_thong_ke(ui, stats):
    """Cập nhật dữ liệu số lớn và vẽ lại 2 biểu đồ trực tiếp trên trang Thống kê tĩnh."""
    # 1. Cập nhật các card số liệu
    ui["lbl_stats_tong"].config(text=str(stats.get("tong_ct", 0)))
    ui["lbl_stats_tb"].config(text=f"{stats.get('tg_trung_binh', 0):.1f} phút" if stats.get("tong_ct", 0) else "—")
    ui["lbl_stats_min"].config(text=f"{stats.get('tg_min', 0)} phút" if stats.get("tong_ct", 0) else "—")
    ui["lbl_stats_max"].config(text=f"{stats.get('tg_max', 0)} phút" if stats.get("tong_ct", 0) else "—")
    
    # 2. Xóa biểu đồ cũ trong container
    for widget in ui["stats_container"].winfo_children():
        widget.destroy()
        
    if not stats or stats.get("tong_ct", 0) == 0:
        tk.Label(ui["stats_container"], text="Chưa có dữ liệu để lập biểu đồ thống kê.",
                 font=("Segoe UI", 11, "italic"), bg=COLOR_SURFACE, fg=COLOR_MUTED).pack(pady=60)
        return
        
    # 3. Vẽ 2 biểu đồ Matplotlib mới
    plt.style.use("default")
    # Tạo 1 Figure chứa 2 Subplots song song ngang
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), facecolor=COLOR_SURFACE)
    fig.subplots_adjust(bottom=0.25, wspace=0.35)
    
    # ── Biểu đồ cột 1 (Thời gian chuẩn bị theo loại món)
    tg_loai = stats.get("tg_theo_loai", {})
    if tg_loai:
        labels1 = list(tg_loai.keys())
        values1 = list(tg_loai.values())
        bars = ax1.bar(labels1, values1, color=COLOR_ACCENT, width=0.55)
        ax1.set_title("TG Chuẩn bị TB theo Loại (phút)", color=COLOR_TEXT, pad=12, fontname="Segoe UI", fontsize=10, fontweight="bold")
        ax1.tick_params(axis='x', rotation=30, colors=COLOR_MUTED, labelsize=8)
        ax1.tick_params(axis='y', colors=COLOR_MUTED, labelsize=8)
        ax1.set_facecolor("#FCFAFF") # Màu nền trong biểu đồ cột rất nhẹ
        ax1.grid(axis='y', linestyle='--', alpha=0.3)
        # Bỏ đường viền đen trên/phải biểu đồ cột
        for spine in ["top", "right"]:
            ax1.spines[spine].set_visible(False)
        ax1.spines["left"].set_color(COLOR_BORDER)
        ax1.spines["bottom"].set_color(COLOR_BORDER)
        
        # Thêm text giá trị lên đỉnh cột
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', color=COLOR_TEXT, fontsize=8)
    else:
        ax1.text(0.5, 0.5, "Không có dữ liệu", ha='center', va='center')
        ax1.set_title("TG Chuẩn bị TB theo Loại")

    # ── Biểu đồ quạt 2 (Top 7 nguyên liệu phổ biến nhất)
    top_nl = stats.get("top_nguyen_lieu", {})
    if top_nl:
        labels2 = list(top_nl.keys())[:7] # Lấy top 7
        values2 = list(top_nl.values())[:7]
        wedges, texts, autotexts = ax2.pie(values2, labels=labels2, autopct='%1.1f%%',
                                           startangle=90, textprops=dict(color=COLOR_TEXT, fontsize=8),
                                           colors=plt.cm.plasma(np.linspace(0.2, 0.8, len(labels2))))
        ax2.set_title("Top 7 Nguyên liệu phổ biến", color=COLOR_TEXT, pad=12, fontname="Segoe UI", fontsize=10, fontweight="bold")
    else:
        ax2.text(0.5, 0.5, "Không có dữ liệu", ha='center', va='center')
        ax2.set_title("Top Nguyên liệu phổ biến")

    # Đưa Figure của Matplotlib vào Widget Tkinter
    canvas = FigureCanvasTkAgg(fig, master=ui["stats_container"])
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    # Giải phóng memory Matplotlib khi đóng widget
    def _on_destroy_canvas(event):
        plt.close(fig)
    canvas_widget.bind("<Destroy>", _on_destroy_canvas)


# ─── Form Thêm / Sửa Công Thức (Pop-up nâng cấp) ──────

def _make_field_label(parent, text):
    """Tạo label nhãn trường nhập liệu chuẩn."""
    tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"),
             bg=COLOR_SURFACE, fg=COLOR_MUTED, anchor="w").pack(anchor="w", pady=(10, 3))

def _make_entry(parent, width=None):
    """Tạo Entry đẹp với border highlight."""
    frm = tk.Frame(parent, bg=COLOR_BORDER, padx=1, pady=1)
    frm.pack(fill=tk.X)
    e = tk.Entry(frm, font=("Segoe UI", 10), relief="flat",
                 bg=COLOR_SURFACE, fg=COLOR_TEXT, insertbackground=COLOR_ACCENT)
    e.pack(fill=tk.X, padx=8, pady=6)
    def _focus_in(ev): frm.config(bg=COLOR_ACCENT)
    def _focus_out(ev): frm.config(bg=COLOR_BORDER)
    e.bind("<FocusIn>", _focus_in)
    e.bind("<FocusOut>", _focus_out)
    return e

def _make_text(parent, height=4):
    """Tạo Text đẹp với border highlight."""
    frm = tk.Frame(parent, bg=COLOR_BORDER, padx=1, pady=1)
    frm.pack(fill=tk.X)
    t = tk.Text(frm, font=("Segoe UI", 10), height=height, relief="flat",
                bg=COLOR_SURFACE, fg=COLOR_TEXT, insertbackground=COLOR_ACCENT,
                wrap="word")
    t.pack(fill=tk.X, padx=8, pady=6)
    def _focus_in(ev): frm.config(bg=COLOR_ACCENT)
    def _focus_out(ev): frm.config(bg=COLOR_BORDER)
    t.bind("<FocusIn>", _focus_in)
    t.bind("<FocusOut>", _focus_out)
    return t

def _make_section(parent, title, icon=""):
    """Tạo card section có tiêu đề."""
    card = tk.Frame(parent, bg=COLOR_SURFACE,
                    highlightbackground=COLOR_BORDER, highlightthickness=1)
    card.pack(fill=tk.X, pady=(0, 12))
    # Header section
    hdr = tk.Frame(card, bg=COLOR_PANEL, padx=14, pady=8)
    hdr.pack(fill=tk.X)
    tk.Label(hdr, text=f"{icon}  {title}" if icon else title,
             font=("Segoe UI", 10, "bold"), bg=COLOR_PANEL, fg=COLOR_TEXT).pack(anchor="w")
    # Body section
    body = tk.Frame(card, bg=COLOR_SURFACE, padx=14, pady=4)
    body.pack(fill=tk.X)
    return body


def hien_thi_form(parent, is_edit=False, current_data=None):
    """Hiển thị dialog nhập liệu Thêm / Sửa công thức - layout 2 cột hiện đại."""
    top = tk.Toplevel(parent)
    top.title("Sửa Công thức" if is_edit else "Thêm Công thức mới")
    top.configure(bg=COLOR_BG)
    top.resizable(True, True)
    top.grab_set()

    result = []



    # ── SCROLLABLE BODY ──────────────────────────────────
    wrap = tk.Frame(top, bg=COLOR_BG)
    wrap.pack(fill=tk.BOTH, expand=True)

    cv = tk.Canvas(wrap, bg=COLOR_BG, highlightthickness=0)
    sb = ttk.Scrollbar(wrap, orient="vertical", command=cv.yview)
    cv.configure(yscrollcommand=sb.set)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    body = tk.Frame(cv, bg=COLOR_BG, padx=20, pady=16)
    body_win = cv.create_window((0, 0), window=body, anchor="nw")

    def _on_body_resize(e): cv.configure(scrollregion=cv.bbox("all"))
    def _on_cv_resize(e):   cv.itemconfig(body_win, width=e.width)
    def _on_wheel(e):       cv.yview_scroll(int(-1*(e.delta/120)), "units")
    body.bind("<Configure>", _on_body_resize)
    cv.bind("<Configure>", _on_cv_resize)
    cv.bind_all("<MouseWheel>", _on_wheel)

    # ── 2 CỘT CHÍNH ──────────────────────────────────────
    body.columnconfigure(0, weight=1)
    body.columnconfigure(1, weight=1)

    col_left  = tk.Frame(body, bg=COLOR_BG)
    col_right = tk.Frame(body, bg=COLOR_BG)
    col_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    col_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

    # ─── CỘT TRÁI: Thông tin cơ bản ────────────────────
    sec_info = _make_section(col_left, "Thông Tin Cơ Bản", "🍽")

    _make_field_label(sec_info, "Tên món ăn  *")
    ent_ten = _make_entry(sec_info)

    _make_field_label(sec_info, "Loại món ăn  *")
    frm_cbo = tk.Frame(sec_info, bg=COLOR_BORDER, padx=1, pady=1)
    frm_cbo.pack(fill=tk.X)
    cbo_loai = ttk.Combobox(frm_cbo, values=LOAI_MON_LIST, state="readonly",
                             font=("Segoe UI", 10))
    cbo_loai.set(LOAI_MON_LIST[0])
    cbo_loai.pack(fill=tk.X, padx=6, pady=5)

    _make_field_label(sec_info, "Thời gian chuẩn bị  (phút)  *")
    ent_tg = _make_entry(sec_info)

    _make_field_label(sec_info, "Hình ảnh món ăn")
    frm_img_outer = tk.Frame(sec_info, bg=COLOR_BORDER, padx=1, pady=1)
    frm_img_outer.pack(fill=tk.X)
    frm_img_inner = tk.Frame(frm_img_outer, bg=COLOR_SURFACE)
    frm_img_inner.pack(fill=tk.X)
    ent_img = tk.Entry(frm_img_inner, font=("Segoe UI", 9), relief="flat",
                       bg=COLOR_SURFACE, fg=COLOR_TEXT)
    ent_img.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 4), pady=6)

    def on_choose_img():
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            ent_img.delete(0, tk.END)
            ent_img.insert(0, path)

    tk.Button(frm_img_inner, text="📂", font=("Segoe UI", 10),
              bg=COLOR_PANEL, fg=COLOR_TEXT, relief="flat",
              cursor="hand2", command=on_choose_img,
              padx=8, pady=4).pack(side=tk.RIGHT, padx=4, pady=4)

    # Section nguyên liệu & định lượng (cột trái, dưới)
    sec_nl = _make_section(col_left, "Nguyên Liệu & Định Lượng", "🥬")

    _make_field_label(sec_nl, "Nguyên liệu  (ngăn cách bằng  |  )")
    txt_nl = _make_text(sec_nl, height=3)

    _make_field_label(sec_nl, "Định lượng    (ngăn cách bằng  |  )")
    txt_dl = _make_text(sec_nl, height=3)

    # ─── CỘT PHẢI: Nội dung chi tiết ──────────────────
    sec_cl = _make_section(col_right, "Hướng Dẫn Thực Hiện", "🍳")
    _make_field_label(sec_cl, "Cách làm  (mỗi bước 1 dòng)")
    txt_cl = _make_text(sec_cl, height=10)

    sec_ly = _make_section(col_right, "Lưu Ý Khi Nấu", "💡")
    _make_field_label(sec_ly, "Lưu ý  (mỗi ý 1 dòng)")
    txt_ly = _make_text(sec_ly, height=6)

    # ── FOOTER: Thông báo lỗi + Nút bấm ────────────────
    footer = tk.Frame(top, bg=COLOR_SURFACE,
                      highlightbackground=COLOR_BORDER, highlightthickness=1)
    footer.pack(fill=tk.X, side=tk.BOTTOM)

    lbl_err = tk.Label(footer, text="", font=("Segoe UI", 9, "bold"),
                       bg=COLOR_SURFACE, fg=COLOR_DANGER)
    lbl_err.pack(side=tk.LEFT, padx=20, pady=14)

    f_btns = tk.Frame(footer, bg=COLOR_SURFACE)
    f_btns.pack(side=tk.RIGHT, padx=16, pady=10)

    # ── ĐIỀN DỮ LIỆU CŨ KHI SỬA ─────────────────────────
    if is_edit and current_data:
        ent_ten.insert(0, current_data.get("ten_mon", ""))
        cbo_loai.set(current_data.get("loai_mon", LOAI_MON_LIST[0]))
        txt_nl.insert("1.0", current_data.get("nguyen_lieu", ""))
        txt_dl.insert("1.0", current_data.get("dinh_luong", ""))
        ent_tg.insert(0, str(current_data.get("thoi_gian", 0)))
        txt_cl.insert("1.0", str(current_data.get("cach_lam", "")))
        txt_ly.insert("1.0", str(current_data.get("luu_y", "")))
        ent_img.insert(0, str(current_data.get("hinh_anh", "")))

    # ── VALIDATE & LƯU ───────────────────────────────────
    def on_luu():
        ten    = ent_ten.get().strip()
        loai   = cbo_loai.get()
        nl     = txt_nl.get("1.0", tk.END).strip()
        dl     = txt_dl.get("1.0", tk.END).strip()
        tg_str = ent_tg.get().strip()
        cl     = txt_cl.get("1.0", tk.END).strip()
        ly     = txt_ly.get("1.0", tk.END).strip()
        img    = ent_img.get().strip()

        checks = [
            (not ten,   "⚠  Tên món ăn không được để trống!",    ent_ten),
            (not loai,  "⚠  Vui lòng chọn Loại món ăn!",          None),
            (not tg_str,"⚠  Vui lòng nhập Thời gian chuẩn bị!",  ent_tg),
        ]
        for cond, msg, widget in checks:
            if cond:
                lbl_err.config(text=msg)
                if widget: widget.focus_set()
                return
        try:
            tg = int(tg_str)
            if tg < 0: raise ValueError
        except ValueError:
            lbl_err.config(text="⚠  Thời gian chuẩn bị phải là số nguyên >= 0!")
            ent_tg.focus_set()
            return

        result.append({"ten_mon": ten, "loai_mon": loai,
                        "nguyen_lieu": nl, "dinh_luong": dl,
                        "thoi_gian": tg, "cach_lam": cl,
                        "luu_y": ly, "hinh_anh": img})
        top.destroy()

    # Nút HỦY
    tk.Button(f_btns, text="Hủy bỏ", font=("Segoe UI", 10, "bold"),
              bg=COLOR_PANEL, fg=COLOR_TEXT, relief="flat",
              activebackground=COLOR_BORDER, cursor="hand2",
              padx=18, pady=8, command=top.destroy).pack(side=tk.LEFT, padx=(0, 10))
    # Nút LƯU
    tk.Button(f_btns, text="💾  Lưu lại", font=("Segoe UI", 10, "bold"),
              bg=COLOR_ACCENT, fg="#FFFFFF", relief="flat",
              activebackground="#6D28D9", cursor="hand2",
              padx=18, pady=8, command=on_luu).pack(side=tk.LEFT)

    # ── KÍCH THƯỚC & CĂN GIỮA ───────────────────────────
    W, H = 980, 660
    sx = parent.winfo_x() + (parent.winfo_width()  - W) // 2
    sy = parent.winfo_y() + (parent.winfo_height() - H) // 2
    top.geometry(f"{W}x{H}+{sx}+{sy}")

    def _on_destroy(event):
        if event.widget == top:
            cv.unbind_all("<MouseWheel>")
    top.bind("<Destroy>", _on_destroy)

    top.wait_window()
    return result[0] if result else None




# ─── Cửa sổ chi tiết món ăn ──────────────────────────

def hien_thi_chi_tiet(parent, data):
    """Hien thi cua so phu dang Card cuon duoc xem chi tiet mon an."""

    top = tk.Toplevel(parent)
    top.title(f"📖 Công thức: {data.get('ten_mon', '')}")
    top.configure(bg=COLOR_BG)
    top.geometry("840x700")
    top.minsize(660, 500)
    top.grab_set()

    # Khung cuộn Canvas
    canvas = tk.Canvas(top, bg=COLOR_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
    main = tk.Frame(canvas, bg=COLOR_BG)

    canvas.configure(yscrollcommand = scrollbar.set)
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

    # ── Tên món ăn lớn nổi bật ──
    tk.Label(main, text=data.get("ten_mon", ""), font=("Segoe UI", 22, "bold"),
             bg=COLOR_BG, fg=COLOR_ACCENT, wraplength=760, justify="left").pack(anchor="w", padx=24, pady=(24, 4))

    # Đường trang trí
    sep_line = tk.Frame(main, bg=COLOR_ACCENT, height=2)
    sep_line.pack(fill=tk.X, padx=24, pady=(0, 12))

    # Badges thông tin nhanh
    f_badge = tk.Frame(main, bg=COLOR_BG)
    f_badge.pack(anchor="w", padx=24, pady=(0, 12))
    
    def make_badge(parent, text, bg_col, text_col):
        tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"),
                 bg=bg_col, fg=text_col, padx=12, pady=5).pack(side=tk.LEFT, padx=(0, 10))

    make_badge(f_badge, f"📂  {data.get('loai_mon', 'Khác')}", COLOR_ACCENT_BG, COLOR_ACCENT)
    def format_time(minutes):
        try:
            mins = int(minutes)
        except (ValueError, TypeError):
            return "Không rõ"
        if mins <= 0:
            return "Không rõ"
        if mins < 60:
            return f"{mins} phút"
        hours, rem = divmod(mins, 60)
        if rem == 0:
            return f"{hours} giờ"
        return f"{hours} giờ {rem} phút"

    make_badge(f_badge, f"⏱  {format_time(data.get('thoi_gian', 0))}", COLOR_ACCENT2_BG, COLOR_ACCENT2)

    # ── Bảng Nguyên liệu & Định lượng ──
    tk.Label(main, text="🥬  Nguyên liệu & Định lượng", font=("Segoe UI", 14, "bold"),
             bg=COLOR_BG, fg=COLOR_TEXT).pack(anchor="w", padx=24, pady=(18, 6))

    nl_raw = str(data.get("nguyen_lieu", "")).strip()
    dl_raw = str(data.get("dinh_luong", "")).strip()
    nl_items = [s.strip() for s in nl_raw.split("|") if s.strip()] if nl_raw else []
    dl_items = [s.strip() for s in dl_raw.split("|") if s.strip()] if dl_raw else []

    if nl_items:
        ing_container = tk.Frame(main, bg=COLOR_SURFACE, highlightbackground=COLOR_BORDER, highlightthickness=1)
        ing_container.pack(fill=tk.X, padx=24, pady=(0, 4))

        # Header của bảng nguyên liệu
        header_f = tk.Frame(ing_container, bg=COLOR_PANEL)
        header_f.pack(fill=tk.X)
        tk.Label(header_f, text=" STT", font=("Segoe UI", 9, "bold"), bg=COLOR_PANEL, fg=COLOR_MUTED, width=6, anchor="center").pack(side=tk.LEFT, padx=(4, 0))
        tk.Label(header_f, text="Nguyên liệu cần có", font=("Segoe UI", 9, "bold"), bg=COLOR_PANEL, fg=COLOR_MUTED, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12, pady=6)
        tk.Label(header_f, text="Định lượng chính xác", font=("Segoe UI", 9, "bold"), bg=COLOR_PANEL, fg=COLOR_MUTED, width=20, anchor="center").pack(side=tk.RIGHT, padx=12)

        # Duyệt qua các nguyên liệu
        for i, nl in enumerate(nl_items):
            dl = dl_items[i] if i < len(dl_items) else "—"
            row_bg = COLOR_ROW_ODD if i % 2 == 0 else COLOR_ROW_EVEN
            row_f = tk.Frame(ing_container, bg=row_bg)
            row_f.pack(fill=tk.X)
            
            tk.Label(row_f, text=str(i + 1), font=("Segoe UI", 9), bg=row_bg, fg=COLOR_MUTED, width=6, anchor="center").pack(side=tk.LEFT, padx=(4, 0))
            tk.Label(row_f, text=nl, font=("Segoe UI", 9), bg=row_bg, fg=COLOR_TEXT, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12, pady=5)
            tk.Label(row_f, text=dl, font=("Segoe UI", 9, "bold"), bg=row_bg, fg=COLOR_ACCENT2, width=20, anchor="center").pack(side=tk.RIGHT, padx=12, pady=5)
    else:
        tk.Label(main, text="Chưa có thông tin nguyên liệu chi tiết.", font=("Segoe UI", 10, "italic"), bg=COLOR_BG, fg=COLOR_MUTED).pack(anchor="w", padx=34, pady=4)

    # ── Ảnh minh họa (nếu có) ──
    img_path = str(data.get("hinh_anh", "")).strip()
    if img_path and os.path.exists(img_path):
        try:
            img = Image.open(img_path)
            img.thumbnail((480, 280))
            photo = ImageTk.PhotoImage(img)
            lbl_img = tk.Label(main, image=photo, bg=COLOR_BG)
            lbl_img.image = photo
            lbl_img.pack(anchor="w", padx=24, pady=12)
        except Exception:
            pass

    # ── Hướng dẫn cách nấu (Tách từng dòng thành thẻ) ──
    tk.Label(main, text="🍳  Hướng dẫn từng bước thực hiện", font=("Segoe UI", 14, "bold"),
             bg=COLOR_BG, fg=COLOR_TEXT).pack(anchor="w", padx=24, pady=(18, 6))

    cach_lam_raw = str(data.get("cach_lam", "")).strip()
    step_lines = [s.strip() for s in cach_lam_raw.splitlines() if s.strip()]

    if not step_lines and not cach_lam_raw:
        tk.Label(main, text="Chưa có hướng dẫn các bước nấu cụ thể.", font=("Segoe UI", 10, "italic"), bg=COLOR_BG, fg=COLOR_MUTED).pack(anchor="w", padx=34, pady=4)
    else:
        lines_to_show = step_lines if step_lines else [cach_lam_raw]
        step_num = 0
        for line in lines_to_show:
            import re
            # Tự động loại bỏ tiền tố số bước nếu người dùng đã tự đánh
            clean = re.sub(r'^(bước\s*\d+[:\.]?|\d+[:\.])\s*', '', line, flags=re.IGNORECASE).strip()
            if not clean:
                continue
            step_num += 1

            # Thẻ Card của mỗi bước nấu ăn
            card = tk.Frame(main, bg=COLOR_SURFACE, highlightbackground=COLOR_BORDER, highlightthickness=1)
            card.pack(fill=tk.X, padx=24, pady=5)

            # Số bước tròn màu tím đẹp mắt
            badge_frame = tk.Frame(card, bg=COLOR_ACCENT, width=32, height=32)
            badge_frame.pack(side=tk.LEFT, padx=(12, 0), pady=10)
            badge_frame.pack_propagate(False)
            
            tk.Label(badge_frame, text=str(step_num), font=("Segoe UI", 10, "bold"), bg=COLOR_ACCENT, fg="#FFFFFF").place(relx=0.5, rely=0.5, anchor="center")

            # Mô tả chi tiết bước làm
            tk.Label(card, text=clean, font=("Segoe UI", 10), bg=COLOR_SURFACE, fg=COLOR_TEXT,
                     justify="left", wraplength=700, anchor="w").pack(side=tk.LEFT, padx=14, pady=10, fill=tk.X, expand=True)

    # ── Ghi chú / Lưu ý nổi bật ──
    tk.Label(main, text="💡  Lưu ý quan trọng khi nấu", font=("Segoe UI", 14, "bold"),
             bg=COLOR_BG, fg=COLOR_WARN).pack(anchor="w", padx=24, pady=(20, 6))

    note_panel = tk.Frame(main, bg=COLOR_WARN_BG, highlightbackground=COLOR_WARN, highlightthickness=1)
    note_panel.pack(fill=tk.X, padx=24, pady=(0, 24))

    luu_y_raw = str(data.get("luu_y", "")).strip()
    luu_y_lines = [s.strip() for s in luu_y_raw.splitlines() if s.strip()]

    if luu_y_lines:
        for note in luu_y_lines:
            tk.Label(note_panel, text=f"⚠   {note}", font=("Segoe UI", 10),
                     bg=COLOR_WARN_BG, fg=COLOR_WARN, justify="left", wraplength=730, anchor="w").pack(anchor="w", padx=16, pady=5)
    else:
        # Các lưu ý cơ bản mặc định
        default_notes = [
            "Đảm bảo chuẩn bị đủ dụng cụ và sơ chế nguyên liệu sạch sẽ trước khi thực hiện.",
            "Nêm nếm và điều chỉnh lượng gia vị (ớt, muối, đường) phù hợp với khẩu vị gia đình.",
            "Luôn theo dõi sát nhiệt độ bếp và thời gian đun nấu để món ăn chín hoàn hảo.",
        ]
        for note in default_notes:
            tk.Label(note_panel, text=f"▸   {note}", font=("Segoe UI", 9),
                     bg=COLOR_WARN_BG, fg=COLOR_WARN, justify="left", wraplength=730, anchor="w").pack(anchor="w", padx=16, pady=4.5)

    # Khoảng trống đáy
    tk.Label(main, text="", bg=COLOR_BG).pack(pady=6)

    def _on_destroy(event):
        if event.widget == top:
            canvas.unbind_all("<MouseWheel>")
    top.bind("<Destroy>", _on_destroy)

    return top

