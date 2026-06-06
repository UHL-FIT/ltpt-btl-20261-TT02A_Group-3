"""
views/gui_view_congthuc.py
==========================
Giao diện đồ họa người dùng (GUI) sử dụng thư viện chuẩn Tkinter cho Quản lý Công thức Nấu ăn.
Được thiết kế tỉ mỉ theo phong cách Dashboard hiện đại, phẳng, bo góc mềm mại và đổ bóng nhẹ:
- Sidebar bên trái điều hướng linh hoạt qua các tab màn hình.
- Content area bên phải chứa các trang chuyển đổi động: Trang chủ, Thống kê (biểu đồ trực quan Matplotlib), Giới thiệu.
- Tông màu chủ đạo là Tím (Violet) kết hợp Xanh lục (Emerald) tạo cảm giác cực kỳ premium và sạch sẽ.

Ghi chú cho người mới học:
- Tầng View chỉ chịu trách nhiệm hiển thị giao diện đồ họa. Nó vẽ ra các nút, các ô nhập chữ và bảng biểu.
- View KHÔNG xử lý logic nghiệp vụ hay đọc ghi cơ sở dữ liệu. Khi có hành động click nút, View sẽ thông báo 
  cho Controller giải quyết.
- Tkinter sử dụng mô hình Frame lồng nhau để thiết kế bố cục (Layout). 'pack' và 'grid' là 2 bộ quản lý
  bố cục cực kỳ phổ biến để xếp các ô trên màn hình.
"""

import tkinter as tk            # Thư viện thiết kế giao diện chuẩn của Python
from tkinter import ttk, messagebox, filedialog # Nhập các widget nâng cấp (Combobox, Entry, Treeview, hộp thoại chọn file)
import os                       # Thư viện quản lý đường dẫn file
from models.congthuc import LOAI_MON_LIST # Nhập danh sách loại món ăn để điền vào Combobox bộ lọc
import matplotlib
matplotlib.use("TkAgg")         # Cấu hình Matplotlib sử dụng backend TkAgg để tích hợp biểu đồ vào cửa sổ Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # Lớp cầu nối vẽ biểu đồ lên Widget của Tkinter
import matplotlib.pyplot as plt # Thư viện vẽ biểu đồ Matplotlib quen thuộc
import numpy as np              # Thư viện toán học
from PIL import Image, ImageTk  # Thư viện gối Pillow hỗ trợ xử lý hình ảnh (PNG, JPG) hiển thị trên giao diện

# =========================================================================
# ─── BẢNG MÀU SẮC HIỆN ĐẠI (MODERN COLOR PALETTE) ────────────────────────
# =========================================================================
# Thiết kế giao diện hiện đại bắt đầu từ việc lựa chọn màu sắc hài hòa.
# Tránh dùng các màu thô như đỏ chóe, xanh nõn chuối. Hãy chọn các tông màu Pastel dễ chịu:
COLOR_BG        = "#F8FAFC"  # Nền ứng dụng chính (Slate 50 - màu xám nhạt cực sạch)
COLOR_SURFACE   = "#FFFFFF"  # Nền các thẻ card thông tin, bảng danh sách, thanh sidebar (Trắng tinh khiết)
COLOR_PANEL     = "#F1F5F9"  # Nền phụ cho tiêu đề cột, khung đệm (Slate 100)
COLOR_BORDER    = "#E2E8F0"  # Màu các đường viền chia cắt (Slate 200)

COLOR_ACCENT    = "#7C3AED"  # Tím chủ đạo (Violet 600) - Dùng cho nút bấm chính, tab Menu đang hoạt động
COLOR_ACCENT_BG = "#F5F3FF"  # Nền màu tím siêu nhạt (Violet 50) - Dùng tô nền nút menu active
COLOR_ACCENT2   = "#059669"  # Xanh ngọc lục bảo (Emerald 600) - Dùng cho nút Tìm kiếm, chỉ số thành công
COLOR_ACCENT2_BG= "#ECFDF5"  # Nền xanh lục nhạt

COLOR_WARN      = "#D97706"  # Màu vàng cam cảnh báo (Amber 600) - Dùng cho ghi chú nấu ăn
COLOR_WARN_BG   = "#FEF3C7"  # Nền vàng nhạt
COLOR_DANGER    = "#DC2626"  # Màu đỏ nguy hiểm (Red 600) - Dùng cho nút Xóa công thức
COLOR_DANGER_BG = "#FEF2F2"  # Nền đỏ nhạt

COLOR_TEXT      = "#1E293B"  # Chữ chính (Slate 800) - Màu xám tối giúp đọc chữ lâu không bị mỏi mắt
COLOR_MUTED     = "#64748B"  # Chữ phụ nhạt hơn (Slate 500) - Dùng cho nhãn phụ, bản quyền
COLOR_ROW_ODD   = "#FFFFFF"  # Màu nền dòng lẻ của bảng danh sách (Trắng)
COLOR_ROW_EVEN  = "#F8FAFC"  # Màu nền dòng chẵn của bảng danh sách (Xám rất nhẹ)
COLOR_SEL       = "#EDE9FE"  # Màu nền khi người dùng click chọn dòng trên bảng (Tím nhạt)


def _btn_style(style):
    """
    Định cấu hình các kiểu dáng nút bấm (Styles) bằng ttk.Style()
    giúp tách biệt phần thiết kế giao diện (CSS-like) ra khỏi code layout chính.
    """
    # ─── NÚT HÀNH ĐỘNG CHÍNH (Tím chủ đạo) ───
    style.configure("Action.TButton",
        font=("Segoe UI", 9, "bold"),
        foreground="#ffffff",          # Chữ màu trắng
        background=COLOR_ACCENT,       # Nền màu tím
        borderwidth=0, relief="flat", padding=(12, 6))
    # Hiệu ứng hover chuột (map): khi rà chuột qua (active), đổi sang màu tím đậm hơn
    style.map("Action.TButton",
        background=[("active", "#6D28D9"), ("pressed", "#5B21B6")])

    # ─── NÚT XÓA / NGUY HIỂM (Đỏ nguy hiểm) ───
    style.configure("Danger.TButton",
        font=("Segoe UI", 9, "bold"),
        foreground="#ffffff",
        background=COLOR_DANGER,
        borderwidth=0, relief="flat", padding=(12, 6))
    style.map("Danger.TButton",
        background=[("active", "#B91C1C"), ("pressed", "#991B1B")])

    # ─── NÚT THƯỜNG / TRUNG TÍNH (Xám nhạt) ───
    style.configure("Neutral.TButton",
        font=("Segoe UI", 9, "bold"),
        foreground=COLOR_TEXT,
        background=COLOR_PANEL,
        borderwidth=0, relief="flat", padding=(12, 6))
    style.map("Neutral.TButton",
        background=[("active", "#E2E8F0")])

    # ─── NÚT TÌM KIẾM (Xanh ngọc lục bảo) ───
    style.configure("Search.TButton",
        font=("Segoe UI", 9, "bold"),
        foreground="#ffffff",
        background=COLOR_ACCENT2,
        borderwidth=0, relief="flat", padding=(10, 5))
    style.map("Search.TButton",
        background=[("active", "#047857")])


def sort_treeview(tree, col, reverse):
    """
    Thuật toán sắp xếp dữ liệu trên bảng Treeview khi người dùng click vào tiêu đề cột.
    
    Tham số:
      - tree (Treeview): Đối tượng bảng Treeview cần sắp xếp.
      - col (str): Tên cột được bấm chuột.
      - reverse (bool): Trạng thái đảo ngược sắp xếp (True là giảm dần, False là tăng dần).
    """
    # Không cho phép sắp xếp cột "Chọn" chứa checkbox
    if col == "Chọn":
        return
        
    # Lấy toàn bộ cặp giá trị (giá trị_ở_cell, iid_dòng) có trong bảng Treeview
    data = [(tree.set(k, col), k) for k in tree.get_children("")]
    
    try:
        # THƯỜNG SẮP XẾP SỐ: Thử ép kiểu giá trị cell về dạng số thực (float) để so sánh.
        # Phù hợp cho cột STT hoặc cột Thời gian nấu ăn.
        data.sort(key=lambda t: float(t[0]), reverse=reverse)
    except ValueError:
        # THƯỜNG SẮP XẾP CHỮ: Nếu cell chứa chữ (như tên món ăn, loại món), 
        # ta sắp xếp theo thứ tự chữ cái ABC không phân biệt chữ hoa chữ thường (.lower())
        data.sort(key=lambda t: t[0].lower(), reverse=reverse)
        
    # Di chuyển các dòng dữ liệu Treeview về vị trí mới đã được sắp xếp
    for i, (_, k) in enumerate(data):
        tree.move(k, "", i)
        
    # Ràng buộc lại sự kiện click heading lần tiếp theo: bấm lại sẽ đảo ngược sắp xếp (not reverse)
    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))


def switch_page(ui, page_name):
    """
    Cơ chế chuyển đổi qua lại giữa các trang tĩnh trong Content Area chính (Single Page Application - SPA).
    Bằng cách ẩn tất cả các trang đi và chỉ hiển thị đúng trang được yêu cầu.
    
    Tham số:
      - ui (dict): Bộ từ điển chứa các Widget chính của phần mềm.
      - page_name (str): Tên của trang cần hiển thị ("trang_chu", "thong_ke", "about").
    """
    # 1. Ẩn toàn bộ 3 trang giao diện chính khỏi khung hình (Sử dụng pack_forget)
    ui["page_trang_chu"].pack_forget()
    ui["page_thong_ke"].pack_forget()
    ui["page_gioi_thieu"].pack_forget()

    # 2. Reset thiết kế màu sắc 3 nút Menu Sidebar bên trái về mặc định (Chữ xám nhạt, nền trắng)
    for btn in [ui["btn_trangchu"], ui["btn_thongke"], ui["btn_about"]]:
        btn.config(bg=COLOR_SURFACE, fg=COLOR_MUTED)

    # 3. Hiển thị trang được chọn lên màn hình đồng thời làm nổi bật nút menu tương ứng
    if page_name == "trang_chu":
        ui["page_trang_chu"].pack(fill=tk.BOTH, expand=True) # Điền đầy toàn bộ khung hình
        ui["btn_trangchu"].config(bg=COLOR_ACCENT_BG, fg=COLOR_ACCENT) # Nổi bật nút "Trang chủ"
    elif page_name == "thong_ke":
        ui["page_thong_ke"].pack(fill=tk.BOTH, expand=True)
        ui["btn_thongke"].config(bg=COLOR_ACCENT_BG, fg=COLOR_ACCENT)
    elif page_name == "about":
        ui["page_gioi_thieu"].pack(fill=tk.BOTH, expand=True)
        ui["btn_about"].config(bg=COLOR_ACCENT_BG, fg=COLOR_ACCENT)


def tao_giao_dien_chinh(root):
    """
    Vẽ toàn bộ khung thiết kế giao diện chính của ứng dụng Dashboard:
    - Cửa sổ chính Tkinter.
    - Sidebar điều hướng bên trái chứa logo và các menu tab.
    - Content Area chứa 3 tab màn hình tĩnh bên phải.
    
    Tham số:
      - root (Tk): Cửa sổ Tkinter chính được truyền sang từ Controller.
      
    Trả về:
      - dict: ui - chứa tất cả các đối tượng widget chính để Controller dễ gán sự kiện.
    """
    root.title("🍳 Quản lý Công thức Nấu ăn - Dashboard")
    root.geometry("1280x760")            # Thiết lập kích thước cửa sổ rộng x cao mặc định
    root.minsize(1020, 660)             # Thiết lập kích thước giới hạn nhỏ nhất để tránh vỡ giao diện
    root.configure(bg=COLOR_BG)         # Gán màu nền chính

    # THIẾT LẬP LOGO ICON (.ico) CHO CỬA SỔ CHƯƠNG TRÌNH:
    try:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ico = os.path.join(base, "assets", "app_icon.ico")
        if os.path.exists(ico):
            root.iconbitmap(default=ico)  # Đặt icon cho thanh Taskbar
    except Exception:
        pass # Bỏ qua nếu môi trường không hỗ trợ hoặc thiếu file ảnh icon

    # CẤU HÌNH PHONG CÁCH WIDGET NÂNG CAO (TTK STYLE):
    style = ttk.Style()
    style.theme_use("clam")               # Sử dụng theme gốc 'clam' để dễ ghi đè màu sắc phẳng hiện đại
    _btn_style(style)                     # Định nghĩa style cho các nút bấm
    
    # Thiết lập phong cách bảng biểu Treeview
    style.configure("Treeview",
        font=("Segoe UI", 10),
        background=COLOR_SURFACE,
        fieldbackground=COLOR_SURFACE,
        foreground=COLOR_TEXT,
        rowheight=32,                     # Khoảng cách giữa các dòng cao ráo dễ đọc (32 pixels)
        borderwidth=0)
    
    # Cấu hình tiêu đề bảng Treeview
    style.configure("Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        background=COLOR_PANEL,
        foreground=COLOR_TEXT,
        relief="flat", padding=8)
    
    # Bản đồ màu sắc (map) cho bảng Treeview khi click chuột chọn dòng
    style.map("Treeview",
        background=[
            ("selected", COLOR_SEL),      # Màu nền khi dòng được click chọn
            ("active",   COLOR_BG),       # Màu nền khi di chuột qua dòng
        ],
        foreground=[
            ("selected", COLOR_ACCENT),   # Màu chữ khi dòng được click chọn
            ("active",   COLOR_TEXT),
        ])
        
    style.map("Treeview.Heading",
        background=[("active", COLOR_BORDER)],
        foreground=[("active", COLOR_TEXT)])

    # Khởi tạo từ điển lưu trữ các widget
    ui = {}

    # ═══════════════════════════════════════════════════
    # ─── 1. THANH MENU SIDEBAR BÊN TRÁI (SIDEBAR) ──────
    # ═══════════════════════════════════════════════════
    sidebar = tk.Frame(root, bg=COLOR_SURFACE, width=230, highlightbackground=COLOR_BORDER, highlightthickness=1)
    sidebar.pack(side=tk.LEFT, fill=tk.Y)  # Điền đầy hết chiều dọc màn hình
    sidebar.pack_propagate(False)          # Giữ cố định chiều rộng 230px, không bị co bóp theo phần tử con bên trong

    # Thương hiệu logo ứng dụng (Brand Logo) ở đỉnh Sidebar
    brand_f = tk.Frame(sidebar, bg=COLOR_SURFACE, pady=24)
    brand_f.pack(fill=tk.X)
    tk.Label(brand_f, text="🍳  SmartRecipe", font=("Segoe UI", 16, "bold"), bg=COLOR_SURFACE, fg=COLOR_ACCENT).pack()
    tk.Label(brand_f, text="Quản lý Công thức Nấu ăn", font=("Segoe UI", 8, "bold"), bg=COLOR_SURFACE, fg=COLOR_MUTED).pack(pady=(2, 0))

    # Vạch chia nhẹ thẩm mỹ ngăn cách Logo với Menu
    tk.Frame(sidebar, bg=COLOR_BORDER, height=1).pack(fill=tk.X, padx=16, pady=(0, 16))

    # Hàm tạo nhanh các nút điều hướng Menu Sidebar có cấu trúc giống nhau
    def make_sidebar_btn(text, icon):
        btn = tk.Button(sidebar, text=f"  {icon}   {text}", font=("Segoe UI", 10, "bold"),
                        bg=COLOR_SURFACE, fg=COLOR_MUTED, anchor="w", padx=20, pady=12,
                        borderwidth=0, relief="flat", activebackground=COLOR_ACCENT_BG, activeforeground=COLOR_ACCENT,
                        cursor="hand2")  # Con trỏ chuột chuyển thành bàn tay khi rà qua
        btn.pack(fill=tk.X, padx=12, pady=4)
        return btn

    # Đăng ký 3 nút chuyển trang Menu
    ui["btn_trangchu"] = make_sidebar_btn("Trang chủ", "🏠")
    ui["btn_thongke"] = make_sidebar_btn("Thống kê", "📊")
    ui["btn_about"] = make_sidebar_btn("Giới thiệu", "ℹ️")

    # Bản quyền phần mềm nhỏ dưới chân Sidebar
    footer_f = tk.Frame(sidebar, bg=COLOR_SURFACE, pady=16)
    footer_f.pack(side=tk.BOTTOM, fill=tk.X)
    tk.Label(footer_f, text="© 2026 Nhóm 3 - LTPT BTL", font=("Segoe UI", 8), bg=COLOR_SURFACE, fg=COLOR_MUTED).pack()

    # ═══════════════════════════════════════════════════
    # ─── 2. VÙNG HIỂN THỊ NỘI DUNG CHÍNH (CONTENT) ─────
    # ═══════════════════════════════════════════════════
    content_area = tk.Frame(root, bg=COLOR_BG)
    content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) # Điền đầy toàn bộ phần trống bên phải còn lại

    # ───────────────────────────────────────────────────
    # 🏠 TRANG CHỦ (Danh sách công thức - Treeview)
    # ───────────────────────────────────────────────────
    page_trang_chu = tk.Frame(content_area, bg=COLOR_BG)
    ui["page_trang_chu"] = page_trang_chu

    # Header của Trang chủ (Chứa tiêu đề và thanh tìm kiếm/lọc)
    header_trang_chu = tk.Frame(page_trang_chu, bg=COLOR_SURFACE, height=60, highlightbackground=COLOR_BORDER, highlightthickness=1)
    header_trang_chu.pack(fill=tk.X)
    header_trang_chu.pack_propagate(False)

    tk.Label(header_trang_chu, text="Danh Sách Công Thức Nấu Ăn", font=("Segoe UI", 12, "bold"), bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(side=tk.LEFT, padx=18)

    # Khung chứa các công cụ Lọc và Tìm kiếm dạt bên phải
    f_filter_search = tk.Frame(header_trang_chu, bg=COLOR_SURFACE)
    f_filter_search.pack(side=tk.RIGHT, padx=18)

    # Hộp chọn Combobox Loại món ăn
    tk.Label(f_filter_search, text="Lọc loại:", bg=COLOR_SURFACE, fg=COLOR_MUTED, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
    ui["cbo_filter"] = ttk.Combobox(f_filter_search, values=["Tất cả"] + LOAI_MON_LIST, state="readonly", width=12, font=("Segoe UI", 9))
    ui["cbo_filter"].set("Tất cả")
    ui["cbo_filter"].pack(side=tk.LEFT, padx=4)

    # Vạch đứng nhỏ chia tách Combobox với Ô Tìm kiếm
    tk.Frame(f_filter_search, bg=COLOR_BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=4)

    # Ô nhập từ khóa tìm kiếm (Entry)
    ui["ent_search"] = ttk.Entry(f_filter_search, width=20, font=("Segoe UI", 9))
    ui["ent_search"].pack(side=tk.LEFT, padx=4)

    # Nút tìm kiếm (Kính lúp/Tìm)
    ui["btn_search"] = ttk.Button(f_filter_search, text="Tìm", style="Search.TButton")
    ui["btn_search"].pack(side=tk.LEFT, padx=2)

    # Nút xóa bộ lọc tìm kiếm (Chữ X đỏ)
    ui["btn_clear"] = ttk.Button(f_filter_search, text="✖", style="Neutral.TButton", width=3)
    ui["btn_clear"].pack(side=tk.LEFT, padx=2)

    # Thân chính của Trang chủ (Chứa các nút chức năng và Bảng Treeview)
    body_trang_chu = tk.Frame(page_trang_chu, bg=COLOR_BG, padx=20, pady=16)
    body_trang_chu.pack(fill=tk.BOTH, expand=True)

    # Thanh công cụ con (Nút Thêm, Sửa, Xóa)
    toolbar_sub = tk.Frame(body_trang_chu, bg=COLOR_BG)
    toolbar_sub.pack(fill=tk.X, pady=(0, 10))

    ui["btn_them"] = ttk.Button(toolbar_sub, text="＋ Thêm công thức", style="Action.TButton")
    ui["btn_them"].pack(side=tk.LEFT, padx=(0, 6))

    ui["btn_sua"] = ttk.Button(toolbar_sub, text="✏ Sửa công thức", style="Neutral.TButton")
    ui["btn_sua"].pack(side=tk.LEFT, padx=6)

    ui["btn_xoa"] = ttk.Button(toolbar_sub, text="🗑 Xóa", style="Danger.TButton")
    ui["btn_xoa"].pack(side=tk.LEFT, padx=6)

    # Khung bo góc chứa bảng danh sách công thức (Thẻ Card)
    table_card = tk.Frame(body_trang_chu, bg=COLOR_SURFACE, highlightbackground=COLOR_BORDER, highlightthickness=1)
    table_card.pack(fill=tk.BOTH, expand=True)

    cols = ["Chọn", "STT", "Tên món", "Loại món", "TG (phút)"]
    ui["cols"] = cols

    # Khởi tạo đối tượng bảng danh sách Treeview chính
    tree = ttk.Treeview(table_card, columns=cols, show="headings")
    ui["tree"] = tree

    # Cấu hình chiều rộng (widths) và căn lề chữ (anchors) cho từng cột dữ liệu
    col_widths = {"Chọn": 55, "STT": 60, "Tên món": 450, "Loại món": 180, "TG (phút)": 130}
    col_anchor = {"Chọn": tk.CENTER, "STT": tk.CENTER, "Tên món": tk.W, "Loại món": tk.CENTER, "TG (phút)": tk.CENTER}
    
    for col in cols:
        if col == "Chọn":
            tree.heading(col, text="☐")  # Cột checkbox đầu bảng hiển thị ô vuông trống
        else:
            # Click vào tiêu đề cột sẽ kích hoạt hàm sắp xếp sort_treeview
            tree.heading(col, text=col, command=lambda _c=col: sort_treeview(tree, _c, False))
        tree.column(col, width=col_widths.get(col, 120), anchor=col_anchor.get(col, tk.W), minwidth=40)

    # Tô màu xen kẽ cho các dòng lẻ/chẵn của bảng để tăng độ chuyên nghiệp và dễ đọc
    tree.tag_configure("odd",  background=COLOR_ROW_ODD,  foreground=COLOR_TEXT)
    tree.tag_configure("even", background=COLOR_ROW_EVEN, foreground=COLOR_TEXT)

    # Thanh cuộn đứng (Scrollbar) của bảng
    scrollbar_y = ttk.Scrollbar(table_card, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Thanh trạng thái (Status Bar) dưới đáy trang danh sách công thức
    frame_status = tk.Frame(page_trang_chu, bg=COLOR_SURFACE, pady=10, padx=20, highlightbackground=COLOR_BORDER, highlightthickness=1)
    frame_status.pack(fill=tk.X)

    ui["lbl_tong"] = tk.Label(frame_status, text="Tổng: 0 công thức", font=("Segoe UI", 10, "bold"), bg=COLOR_SURFACE, fg=COLOR_TEXT)
    ui["lbl_tong"].pack(side=tk.LEFT, padx=12)

    ui["lbl_tg_tb"] = tk.Label(frame_status, text="TG chuẩn bị TB: — phút", font=("Segoe UI", 10), bg=COLOR_SURFACE, fg=COLOR_MUTED)
    ui["lbl_tg_tb"].pack(side=tk.LEFT, padx=12)

    # Mẹo nhỏ hướng dẫn người dùng
    tk.Label(frame_status, text="💡 Click đúp vào dòng để xem chi tiết hướng dẫn nấu", font=("Segoe UI", 9, "italic"), bg=COLOR_SURFACE, fg=COLOR_MUTED).pack(side=tk.RIGHT, padx=12)

    # ───────────────────────────────────────────────────
    # 📊 TRANG THỐNG KÊ (Báo cáo biểu đồ Matplotlib)
    # ───────────────────────────────────────────────────
    page_thong_ke = tk.Frame(content_area, bg=COLOR_BG)
    ui["page_thong_ke"] = page_thong_ke

    # Header của trang thống kê
    header_thong_ke = tk.Frame(page_thong_ke, bg=COLOR_SURFACE, height=60, highlightbackground=COLOR_BORDER, highlightthickness=1)
    header_thong_ke.pack(fill=tk.X)
    header_thong_ke.pack_propagate(False)
    tk.Label(header_thong_ke, text="📊  Báo Cáo & Phân Tích Thống Kê", font=("Segoe UI", 12, "bold"), bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(side=tk.LEFT, padx=18)

    body_thong_ke = tk.Frame(page_thong_ke, bg=COLOR_BG, padx=20, pady=16)
    body_thong_ke.pack(fill=tk.BOTH, expand=True)

    # Hộp chứa 4 Thẻ Card hiển thị các con số tổng quan (Thống kê nhanh)
    frame_cards = tk.Frame(body_thong_ke, bg=COLOR_BG)
    frame_cards.pack(fill=tk.X, pady=(0, 16))

    # Hàm tạo nhanh các thẻ Card Thống kê số lượng lớn nổi bật
    def create_stat_card(parent_frame, title, color_accent, row, col):
        card = tk.Frame(parent_frame, bg=COLOR_SURFACE, highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.grid(row=row, column=col, sticky="ew", padx=6, pady=4)
        
        # Vạch trang trí dọc bên trái thẻ Card giúp nhận diện tông màu
        indicator = tk.Frame(card, bg=color_accent, width=4)
        indicator.pack(side=tk.LEFT, fill=tk.Y)
        
        info_f = tk.Frame(card, bg=COLOR_SURFACE, padx=12, pady=10)
        info_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(info_f, text=title, font=("Segoe UI", 9, "bold"), bg=COLOR_SURFACE, fg=COLOR_MUTED).pack(anchor="w")
        lbl_val = tk.Label(info_f, text="—", font=("Segoe UI", 16, "bold"), bg=COLOR_SURFACE, fg=COLOR_TEXT)
        lbl_val.pack(anchor="w", pady=(4, 0))
        return lbl_val

    # Thiết lập giãn đều chiều rộng 4 cột grid
    frame_cards.columnconfigure(0, weight=1)
    frame_cards.columnconfigure(1, weight=1)
    frame_cards.columnconfigure(2, weight=1)
    frame_cards.columnconfigure(3, weight=1)

    ui["lbl_stats_tong"] = create_stat_card(frame_cards, "Tổng số công thức:", COLOR_ACCENT, 0, 0)
    ui["lbl_stats_tb"]   = create_stat_card(frame_cards, "Thời gian chuẩn bị TB:", COLOR_ACCENT2, 0, 1)
    ui["lbl_stats_min"]  = create_stat_card(frame_cards, "Chuẩn bị nhanh nhất:", COLOR_WARN, 0, 2)
    ui["lbl_stats_max"]  = create_stat_card(frame_cards, "Chuẩn bị lâu nhất:", COLOR_DANGER, 0, 3)

    # Thẻ Card khổng lồ chứa 2 Biểu đồ vẽ bằng Matplotlib
    chart_card = tk.Frame(body_thong_ke, bg=COLOR_SURFACE, highlightbackground=COLOR_BORDER, highlightthickness=1)
    chart_card.pack(fill=tk.BOTH, expand=True)
    ui["stats_container"] = chart_card

    # ───────────────────────────────────────────────────
    # ℹ️ TRANG GIỚI THIỆU (About Page)
    # ───────────────────────────────────────────────────
    page_gioi_thieu = tk.Frame(content_area, bg=COLOR_BG)
    ui["page_gioi_thieu"] = page_gioi_thieu

    header_gioi_thieu = tk.Frame(page_gioi_thieu, bg=COLOR_SURFACE, height=60, highlightbackground=COLOR_BORDER, highlightthickness=1)
    header_gioi_thieu.pack(fill=tk.X)
    header_gioi_thieu.pack_propagate(False)
    tk.Label(header_gioi_thieu, text="ℹ️  Giới Thiệu Ứng Dụng", font=("Segoe UI", 12, "bold"), bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(side=tk.LEFT, padx=18)

    body_about = tk.Frame(page_gioi_thieu, bg=COLOR_BG, padx=20, pady=24)
    body_about.pack(fill=tk.BOTH, expand=True)

    # Khung Card giới thiệu thông tin chính
    about_card = tk.Frame(body_about, bg=COLOR_SURFACE, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=40, pady=40)
    about_card.pack(fill=tk.BOTH, expand=True)

    tk.Label(about_card, text="🍳  PHẦN MỀM QUẢN LÝ CÔNG THỨC NẤU ĂN", font=("Segoe UI", 18, "bold"), bg=COLOR_SURFACE, fg=COLOR_ACCENT).pack(pady=(0, 16))
    
    sep_f = tk.Frame(about_card, bg=COLOR_BORDER, height=1)
    sep_f.pack(fill=tk.X, pady=(0, 24))

    # Hàm tạo nhanh các hàng thông tin có nhãn rõ ràng
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

    desc_txt = (
        "Ứng dụng hỗ trợ ghi nhớ, lưu trữ thông tin, tìm kiếm thông minh đa từ khóa không dấu "
        "và phân tích thống kê chi tiết các công thức nấu ăn. Giao diện được tối ưu hóa cho trải nghiệm "
        "người dùng mượt mà, trực quan và hiện đại."
    )
    # wraplength=680 sẽ tự động ngắt dòng đoạn văn khi nó vượt quá chiều ngang 680 pixels
    tk.Label(about_card, text=desc_txt, font=("Segoe UI", 10, "italic"), bg=COLOR_SURFACE, fg=COLOR_MUTED, wraplength=680, justify="center").pack(pady=10)

    # Thiết lập trang mở ra mặc định ban đầu là Trang chủ
    switch_page(ui, "trang_chu")

    return ui


# ─── HIỂN THỊ DỮ LIỆU LÊN BẢNG TREEVIEW ───────────────────────────────────────────

def hien_thi_bang(ui, df):
    """
    Xóa sạch dữ liệu cũ và nạp lại toàn bộ dữ liệu từ DataFrame vào bảng Treeview giao diện.
    
    Tham số:
      - ui (dict): Từ điển lưu trữ các widget.
      - df (DataFrame): DataFrame chứa dữ liệu công thức nấu ăn mới nhất.
    """
    tree = ui["tree"]
    tree.heading("Chọn", text="☐")  # Reset biểu tượng checkbox ở tiêu đề về ô rỗng
    
    # Xóa sạch tất cả các dòng cũ trên Treeview
    for row in tree.get_children():
        tree.delete(row)

    # Nếu DataFrame rỗng (không có kết quả hoặc tìm không thấy), kết thúc sớm
    if df is None or df.empty:
        return

    # Duyệt qua từng dòng của DataFrame bắt đầu đếm số thứ tự từ 1 (start=1)
    for idx, (_, row) in enumerate(df.iterrows(), start=1):
        tg = row.get("thoi_gian", 0)
        # Sắp xếp các cột dữ liệu theo đúng thứ tự khai báo Treeview
        values = [
            "☐",                    # Cột 1: Ký tự ô trống đại diện checkbox
            str(idx),               # Cột 2: Số thứ tự (STT) tăng dần
            row.get("ten_mon", ""),  # Cột 3: Tên món ăn
            row.get("loai_mon", ""), # Cột 4: Loại món ăn
            str(tg),                # Cột 5: Thời gian chuẩn bị
        ]
        
        # Tag xen kẽ dòng "odd" (lẻ) và "even" (chẵn) để tô màu sắc khác nhau
        tag = "odd" if idx % 2 else "even"
        tree.insert("", tk.END, values=values, tags=(tag,))


def cap_nhat_status(ui, stats):
    """Cập nhật các nhãn số liệu hiển thị ở thanh trạng thái (Status Bar) dưới bảng Trang chủ."""
    tong = stats.get("tong_ct", 0)
    tg_tb = stats.get("tg_trung_binh", 0)
    ui["lbl_tong"].config(text=f"Tổng: {tong} công thức")
    ui["lbl_tg_tb"].config(
        text=f"TG chuẩn bị TB: {tg_tb:.1f} phút" if tong else "TG chuẩn bị TB: — phút")


def cap_nhat_trang_thong_ke(ui, stats):
    """
    Vẽ lại 2 biểu đồ phân tích thống kê Matplotlib cực đẹp trên trang Dashboard.
    Hàm này tự động giải phóng bộ nhớ (memory leak check) khi biểu đồ cũ bị thay thế.
    """
    # 1. Cập nhật các con số khổng lồ trên 4 thẻ Card Thống kê
    ui["lbl_stats_tong"].config(text=str(stats.get("tong_ct", 0)))
    ui["lbl_stats_tb"].config(text=f"{stats.get('tg_trung_binh', 0):.1f} phút" if stats.get("tong_ct", 0) else "—")
    ui["lbl_stats_min"].config(text=f"{stats.get('tg_min', 0)} phút" if stats.get("tong_ct", 0) else "—")
    ui["lbl_stats_max"].config(text=f"{stats.get('tg_max', 0)} phút" if stats.get("tong_ct", 0) else "—")
    
    # 2. Xóa sạch các widget biểu đồ cũ trong khung chứa (stats_container) trước khi vẽ biểu đồ mới
    for widget in ui["stats_container"].winfo_children():
        widget.destroy()
        
    # Trường hợp cơ sở dữ liệu trống trơn
    if not stats or stats.get("tong_ct", 0) == 0:
        tk.Label(ui["stats_container"], text="Chưa có dữ liệu để lập biểu đồ phân tích thống kê.",
                 font=("Segoe UI", 11, "italic"), bg=COLOR_SURFACE, fg=COLOR_MUTED).pack(pady=60)
        return
        
    # 3. VẼ BIỂU ĐỒ BẰNG MATPLOTLIB:
    plt.style.use("default") # Reset phong cách mặc định
    
    # Tạo đối tượng Figure chứa 2 biểu đồ con (ax1, ax2) xếp cạnh nhau ngang
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), facecolor=COLOR_SURFACE)
    # Cấu hình khoảng cách căn lề cho biểu đồ
    fig.subplots_adjust(bottom=0.25, wspace=0.35)
    
    # ─── BIỂU ĐỒ CỘT 1 (Thời gian chuẩn bị trung bình theo từng loại món ăn) ───
    tg_loai = stats.get("tg_theo_loai", {})
    if tg_loai:
        labels1 = list(tg_loai.keys())
        values1 = list(tg_loai.values())
        
        # Vẽ các thanh cột đứng (bar) có tông màu tím violet chủ đạo
        bars = ax1.bar(labels1, values1, color=COLOR_ACCENT, width=0.55)
        ax1.set_title("TG Chuẩn bị TB theo Loại (phút)", color=COLOR_TEXT, pad=12, fontname="Segoe UI", fontsize=10, fontweight="bold")
        
        # Xoay chữ nhãn cột nghiêng 30 độ để tránh đè chữ
        ax1.tick_params(axis='x', rotation=30, colors=COLOR_MUTED, labelsize=8)
        ax1.tick_params(axis='y', colors=COLOR_MUTED, labelsize=8)
        ax1.set_facecolor("#FCFAFF")  # Tô màu nền nhẹ bên trong khu vực vẽ cột
        ax1.grid(axis='y', linestyle='--', alpha=0.3) # Vẽ đường lưới ngang đứt nét
        
        # Ẩn 2 đường viền trên và viền phải của biểu đồ để tăng cảm giác phẳng, hiện đại
        for spine in ["top", "right"]:
            ax1.spines[spine].set_visible(False)
        ax1.spines["left"].set_color(COLOR_BORDER)
        ax1.spines["bottom"].set_color(COLOR_BORDER)
        
        # Tự động ghi nhãn số thực tế trên đỉnh của từng cột (annotate)
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), # Khoảng dịch chữ lên trên 3 pixels
                        textcoords="offset points",
                        ha='center', va='bottom', color=COLOR_TEXT, fontsize=8)
    else:
        ax1.text(0.5, 0.5, "Không có dữ liệu", ha='center', va='center')
        ax1.set_title("TG Chuẩn bị TB theo Loại")

    # ─── BIỂU ĐỒ QUẠT 2 (Tỷ lệ 7 nguyên liệu phổ biến nhất) ───
    top_nl = stats.get("top_nguyen_lieu", {})
    if top_nl:
        labels2 = list(top_nl.keys())[:7]  # Giới hạn lấy top 7 nguyên liệu đứng đầu
        values2 = list(top_nl.values())[:7]
        
        # Vẽ biểu đồ quạt tròn (pie chart) phân bố màu sắc theo quang phổ plasma nổi bật
        wedges, texts, autotexts = ax2.pie(values2, labels=labels2, autopct='%1.1f%%',
                                           startangle=90, textprops=dict(color=COLOR_TEXT, fontsize=8),
                                           colors=plt.cm.plasma(np.linspace(0.2, 0.8, len(labels2))))
        ax2.set_title("Top 7 Nguyên liệu phổ biến", color=COLOR_TEXT, pad=12, fontname="Segoe UI", fontsize=10, fontweight="bold")
    else:
        ax2.text(0.5, 0.5, "Không có dữ liệu", ha='center', va='center')
        ax2.set_title("Top Nguyên liệu phổ biến")

    # 4. TÍCH HỢP BIỂU ĐỒ VÀO WIDGET TKINTER:
    canvas = FigureCanvasTkAgg(fig, master=ui["stats_container"])
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    # GIẢI PHÓNG BỘ NHỚ MATPLOTLIB KHI WIDGET BỊ HỦY:
    # Biểu đồ Matplotlib vẽ ra chiếm rất nhiều RAM. Nếu tắt cửa sổ mà không đóng đối tượng Figure (plt.close(fig)), 
    # tài nguyên RAM sẽ bị rò rỉ (memory leak). Ta bind sự kiện <Destroy> để tự động giải phóng Figure.
    def _on_destroy_canvas(event):
        plt.close(fig)
    canvas_widget.bind("<Destroy>", _on_destroy_canvas)


# ─── HÀM THIẾT KẾ CÁC TRƯỜNG NHẬP LIỆU (FORM BUILDERS) ─────────────────────────────

def _make_field_label(parent, text):
    """Tạo nhãn Label chuẩn hóa cho các trường nhập liệu form."""
    tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"),
             bg=COLOR_SURFACE, fg=COLOR_MUTED, anchor="w").pack(anchor="w", pady=(10, 3))


def _make_entry(parent, width=None):
    """
    Tạo ô nhập liệu Entry đẹp mắt có hiệu ứng viền phát sáng (Focus Highlight Effect).
    Khi người dùng nhấp chuột vào ô nhập (FocusIn), viền đổi màu tím thẫm. 
    Khi bấm ra ngoài (FocusOut), viền trả lại màu xám mặc định.
    """
    # Khung bao bọc bên ngoài đóng vai trò làm đường viền bo pixels
    frm = tk.Frame(parent, bg=COLOR_BORDER, padx=1, pady=1)
    frm.pack(fill=tk.X)
    
    # Ô nhập liệu thực tế đặt phẳng (relief="flat") bên trong khung viền
    e = tk.Entry(frm, font=("Segoe UI", 10), relief="flat",
                 bg=COLOR_SURFACE, fg=COLOR_TEXT, insertbackground=COLOR_ACCENT)
    e.pack(fill=tk.X, padx=8, pady=6)
    
    # Cấu hình đổi màu khung viền
    def _focus_in(ev): frm.config(bg=COLOR_ACCENT)
    def _focus_out(ev): frm.config(bg=COLOR_BORDER)
    e.bind("<FocusIn>", _focus_in)
    e.bind("<FocusOut>", _focus_out)
    return e


def _make_text(parent, height=4):
    """Tạo ô nhập văn bản dài (Text Area) có viền highlight phát sáng đổi màu khi focus."""
    frm = tk.Frame(parent, bg=COLOR_BORDER, padx=1, pady=1)
    frm.pack(fill=tk.X)
    
    t = tk.Text(frm, font=("Segoe UI", 10), height=height, relief="flat",
                bg=COLOR_SURFACE, fg=COLOR_TEXT, insertbackground=COLOR_ACCENT,
                wrap="word")  # wrap="word" đảm bảo ngắt dòng trọn vẹn từ ngữ, không bị bẻ đôi ký tự
    t.pack(fill=tk.X, padx=8, pady=6)
    
    def _focus_in(ev): frm.config(bg=COLOR_ACCENT)
    def _focus_out(ev): frm.config(bg=COLOR_BORDER)
    t.bind("<FocusIn>", _focus_in)
    t.bind("<FocusOut>", _focus_out)
    return t


def _make_section(parent, title, icon=""):
    """Tạo một thẻ Section bo khung đẹp mắt để nhóm các trường nhập liệu liên quan lại với nhau."""
    card = tk.Frame(parent, bg=COLOR_SURFACE,
                    highlightbackground=COLOR_BORDER, highlightthickness=1)
    card.pack(fill=tk.X, pady=(0, 12))
    
    # Phần đỉnh tiêu đề Section (Header)
    hdr = tk.Frame(card, bg=COLOR_PANEL, padx=14, pady=8)
    hdr.pack(fill=tk.X)
    tk.Label(hdr, text=f"{icon}  {title}" if icon else title,
             font=("Segoe UI", 10, "bold"), bg=COLOR_PANEL, fg=COLOR_TEXT).pack(anchor="w")
             
    # Phần thân chứa các ô nhập (Body)
    body = tk.Frame(card, bg=COLOR_SURFACE, padx=14, pady=4)
    body.pack(fill=tk.X)
    return body


# ─── CỬA SỔ POPUP NHẬP LIỆU THÊM / SỬA CÔNG THỨC ──────────────────────────────

def hien_thi_form(parent, is_edit=False, current_data=None):
    """
    Hiển thị hộp thoại (Dialog Window) Popup để nhập dữ liệu Thêm hoặc Sửa công thức.
    Thiết kế bố cục dạng lưới 2 cột cực đẹp, hỗ trợ thanh cuộn dọc (Canvas Scrollbar) 
    và bắt lỗi dữ liệu đầu vào chặt chẽ.
    
    Tham số:
      - parent: Đối tượng cửa sổ cha (để căn giữa vị trí cửa sổ con).
      - is_edit (bool): True nếu là chế độ Sửa (sẽ điền sẵn dữ liệu cũ), False là Thêm mới.
      - current_data (dict): Dữ liệu cũ cần điền vào các ô nhập nếu sửa.
      
    Trả về:
      - dict: Thông tin công thức người dùng vừa nhập nếu bấm Lưu, hoặc None nếu bấm Hủy.
    """
    top = tk.Toplevel(parent)  # Tạo cửa sổ cấp cao nhất (Popup Window)
    top.title("Sửa Công thức" if is_edit else "Thêm Công thức mới")
    top.configure(bg=COLOR_BG)
    top.resizable(True, True)  # Cho phép co giãn cửa sổ
    top.grab_set()             # Đóng băng tương tác cửa sổ chính phía sau, buộc người dùng xử lý xong form mới quay lại được

    # Biến trung gian lưu kết quả trả về
    result = []

    # ── KHUNG THIẾT KẾ CUỘN CANVAS (SCROLLABLE CANVAS WORKFLOW) ──
    # Form có rất nhiều trường nhập liệu. Nếu màn hình độ phân giải thấp sẽ bị tràn và mất các nút ở đáy.
    # Giải pháp: Dùng bộ Canvas để cuộn được toàn bộ các thẻ nhập liệu bằng con trỏ hoặc chuột giữa!
    wrap = tk.Frame(top, bg=COLOR_BG)
    wrap.pack(fill=tk.BOTH, expand=True)

    cv = tk.Canvas(wrap, bg=COLOR_BG, highlightthickness=0)
    sb = ttk.Scrollbar(wrap, orient="vertical", command=cv.yview)
    cv.configure(yscrollcommand=sb.set)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Thân chứa các thẻ nhập liệu nằm trên Canvas
    body = tk.Frame(cv, bg=COLOR_BG, padx=20, pady=16)
    body_win = cv.create_window((0, 0), window=body, anchor="nw")

    # Tự động tính toán lại vùng cuộn dọc (scrollregion) khi các thẻ con bên trong co giãn kích thước
    def _on_body_resize(e): cv.configure(scrollregion=cv.bbox("all"))
    # Ép chiều rộng khung body luôn giãn khít theo chiều rộng cửa sổ Canvas
    def _on_cv_resize(e):   cv.itemconfig(body_win, width=e.width)
    # Lắng nghe sự kiện lăn nút cuộn chuột giữa
    def _on_wheel(e):       cv.yview_scroll(int(-1*(e.delta/120)), "units")
    
    body.bind("<Configure>", _on_body_resize)
    cv.bind("<Configure>", _on_cv_resize)
    cv.bind_all("<MouseWheel>", _on_wheel)

    # ── CẤU TRÚC LAYOUT 2 CỘT CHÍNH (2-COLUMN GRID) ──
    body.columnconfigure(0, weight=1)
    body.columnconfigure(1, weight=1)

    col_left  = tk.Frame(body, bg=COLOR_BG)
    col_right = tk.Frame(body, bg=COLOR_BG)
    col_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    col_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

    # =========================================================================
    # ─── CỘT TRÁI: THÔNG TIN CƠ BẢN VÀ NGUYÊN LIỆU ───
    # =========================================================================
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

    # Nút bấm mở hộp thoại chọn file ảnh minh họa (.png, .jpg...) từ máy tính
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

    # Nút folder icon để bấm duyệt thư mục chọn file ảnh
    tk.Button(frm_img_inner, text="📂", font=("Segoe UI", 10),
              bg=COLOR_PANEL, fg=COLOR_TEXT, relief="flat",
              cursor="hand2", command=on_choose_img,
              padx=8, pady=4).pack(side=tk.RIGHT, padx=4, pady=4)

    # Section Nguyên liệu & Định lượng (Cột trái, Dưới)
    sec_nl = _make_section(col_left, "Nguyên Liệu & Định Lượng", "🥬")

    _make_field_label(sec_nl, "Nguyên liệu  (ngăn cách bằng  |  )")
    txt_nl = _make_text(sec_nl, height=3)

    _make_field_label(sec_nl, "Định lượng    (ngăn cách bằng  |  )")
    txt_dl = _make_text(sec_nl, height=3)

    # =========================================================================
    # ─── CỘT PHẢI: HƯỚNG DẪN CÁCH NẤU VÀ LƯU Ý ───
    # =========================================================================
    sec_cl = _make_section(col_right, "Hướng Dẫn Thực Hiện", "🍳")
    _make_field_label(sec_cl, "Cách làm  (mỗi bước viết trên 1 dòng)")
    txt_cl = _make_text(sec_cl, height=10)

    sec_ly = _make_section(col_right, "Lưu Ý Khi Nấu", "💡")
    _make_field_label(sec_ly, "Lưu ý  (mỗi ý viết trên 1 dòng)")
    txt_ly = _make_text(sec_ly, height=6)

    # =========================================================================
    # ─── PHẦN CHÂN ĐẾ (FOOTER): NÚT BẤM VÀ THÔNG BÁO LỖI ───
    # =========================================================================
    footer = tk.Frame(top, bg=COLOR_SURFACE,
                      highlightbackground=COLOR_BORDER, highlightthickness=1)
    footer.pack(fill=tk.X, side=tk.BOTTOM)

    # Nhãn hiển thị thông báo lỗi bằng chữ đỏ rực cảnh báo khi validate đầu vào thất bại
    lbl_err = tk.Label(footer, text="", font=("Segoe UI", 9, "bold"),
                       bg=COLOR_SURFACE, fg=COLOR_DANGER)
    lbl_err.pack(side=tk.LEFT, padx=20, pady=14)

    f_btns = tk.Frame(footer, bg=COLOR_SURFACE)
    f_btns.pack(side=tk.RIGHT, padx=16, pady=10)

    # ── ĐIỀN SẴN DỮ LIỆU CŨ (Chỉ chạy ở chế độ Sửa món ăn) ──
    if is_edit and current_data:
        ent_ten.insert(0, current_data.get("ten_mon", ""))
        cbo_loai.set(current_data.get("loai_mon", LOAI_MON_LIST[0]))
        txt_nl.insert("1.0", current_data.get("nguyen_lieu", ""))
        txt_dl.insert("1.0", current_data.get("dinh_luong", ""))
        ent_tg.insert(0, str(current_data.get("thoi_gian", 0)))
        txt_cl.insert("1.0", str(current_data.get("cach_lam", "")))
        txt_ly.insert("1.0", str(current_data.get("luu_y", "")))
        ent_img.insert(0, str(current_data.get("hinh_anh", "")))

    # ── BẮT LỖI VÀ VALIDATE TRƯỚC KHI GỬI DỮ LIỆU LÊN CONTROLLER ──
    def on_luu():
        ten    = ent_ten.get().strip()
        loai   = cbo_loai.get()
        nl     = txt_nl.get("1.0", tk.END).strip()
        dl     = txt_dl.get("1.0", tk.END).strip()
        tg_str = ent_tg.get().strip()
        cl     = txt_cl.get("1.0", tk.END).strip()
        ly     = txt_ly.get("1.0", tk.END).strip()
        img    = ent_img.get().strip()

        # Cấu trúc kiểm tra nhanh các trường bắt buộc phải có (*)
        checks = [
            (not ten,       "⚠  Tên món ăn không được để trống!",              ent_ten),
            (len(ten) > 100, "⚠  Tên món ăn không được quá 100 ký tự!",         ent_ten),
            (not loai,      "⚠  Vui lòng chọn Loại món ăn!",                   None),
            (not tg_str,    "⚠  Vui lòng nhập Thời gian chuẩn bị!",            ent_tg),
        ]
        
        for cond, msg, widget in checks:
            if cond:
                lbl_err.config(text=msg)
                if widget: widget.focus_set()
                return
                
        # Validate kiểu dữ liệu thời gian chuẩn bị
        try:
            tg = int(tg_str)
            if tg < 0: raise ValueError
        except ValueError:
            lbl_err.config(text="⚠  Thời gian chuẩn bị phải là số nguyên >= 0!")
            ent_tg.focus_set()
            return

        # TC-07: Kiểm tra số lượng nguyên liệu và định lượng phải khớp nhau
        if nl or dl:
            nl_items = [x.strip() for x in nl.split("|") if x.strip()]
            dl_items = [x.strip() for x in dl.split("|") if x.strip()]
            if len(nl_items) != len(dl_items):
                lbl_err.config(text="⚠  Số lượng định lượng không khớp với nguyên liệu!")
                return

        # Nạp dữ liệu hợp lệ vào từ điển kết quả
        result.append({"ten_mon": ten, "loai_mon": loai,
                        "nguyen_lieu": nl, "dinh_luong": dl,
                        "thoi_gian": tg, "cach_lam": cl,
                        "luu_y": ly, "hinh_anh": img})
        top.destroy() # Đóng popup form lại sau khi lưu thành công

    # NÚT HỦY BỎ
    tk.Button(f_btns, text="Hủy bỏ", font=("Segoe UI", 10, "bold"),
              bg=COLOR_PANEL, fg=COLOR_TEXT, relief="flat",
              activebackground=COLOR_BORDER, cursor="hand2",
              padx=18, pady=8, command=top.destroy).pack(side=tk.LEFT, padx=(0, 10))
              
    # NÚT LƯU LẠI
    tk.Button(f_btns, text="💾  Lưu lại", font=("Segoe UI", 10, "bold"),
              bg=COLOR_ACCENT, fg="#FFFFFF", relief="flat",
              activebackground="#6D28D9", cursor="hand2",
              padx=18, pady=8, command=on_luu).pack(side=tk.LEFT)

    # ── CĂN GIỮA VỊ TRÍ CỬA SỔ POPUP ──
    # Tính toán tọa độ x, y để khi cửa sổ Popup hiện lên nó sẽ nằm chính giữa cửa sổ cha, 
    # tạo sự cân đối và trải nghiệm UX mượt mà.
    W, H = 980, 660
    sx = parent.winfo_x() + (parent.winfo_width()  - W) // 2
    sy = parent.winfo_y() + (parent.winfo_height() - H) // 2
    top.geometry(f"{W}x{H}+{sx}+{sy}")

    # Đảm bảo giải phóng ràng buộc cuộn chuột của Canvas khi đóng cửa sổ phụ
    def _on_destroy(event):
        if event.widget == top:
            cv.unbind_all("<MouseWheel>")
    top.bind("<Destroy>", _on_destroy)

    top.wait_window()  # Tạm dừng luồng code cho đến khi cửa sổ Popup này bị đóng
    return result[0] if result else None


# ─── CỬA SỔ PHỤ XEM CHI TIẾT MÓN ĂN DẠNG CARD CHUYÊN NGHIỆP ─────────────────────

def hien_thi_chi_tiet(parent, data):
    """
    Hiển thị cửa sổ popup dạng Card cuộn được chứa đầy đủ chi tiết công thức món ăn:
    - Tiêu đề món siêu to nổi bật.
    - Huy hiệu (Badges) loại món và thời gian chuẩn bị.
    - Bảng danh sách nguyên liệu và định lượng tương ứng.
    - Ảnh minh họa sắc nét đính kèm (nếu có).
    - Hướng dẫn các bước nấu ăn được bóc tách và tự động đánh số thứ tự trong các thẻ riêng biệt.
    - Các lưu ý quan trọng nổi bật tông màu vàng cam ấm.
    """
    top = tk.Toplevel(parent)
    top.title(f"📖 Công thức: {data.get('ten_mon', '')}")
    top.configure(bg=COLOR_BG)
    top.geometry("840x700")
    top.minsize(660, 500)
    top.grab_set()

    # Sử dụng Canvas cuộn để tránh mất thông tin khi trang quá dài
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

    # ── TÊN MÓN ĂN CỰC TO NỔI BẬT ──
    tk.Label(main, text=data.get("ten_mon", ""), font=("Segoe UI", 22, "bold"),
             bg=COLOR_BG, fg=COLOR_ACCENT, wraplength=760, justify="left").pack(anchor="w", padx=24, pady=(24, 4))

    # Đường chỉ kẻ trang trí nhẹ dưới tên món
    sep_line = tk.Frame(main, bg=COLOR_ACCENT, height=2)
    sep_line.pack(fill=tk.X, padx=24, pady=(0, 12))

    # KHUNG CHỨA CÁC HUY HIỆU HUY CHƯƠNG (BADGES):
    f_badge = tk.Frame(main, bg=COLOR_BG)
    f_badge.pack(anchor="w", padx=24, pady=(0, 12))
    
    def make_badge(parent, text, bg_col, text_col):
        tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"),
                 bg=bg_col, fg=text_col, padx=12, pady=5).pack(side=tk.LEFT, padx=(0, 10))

    # Vẽ huy hiệu Loại món ăn
    make_badge(f_badge, f"📂  {data.get('loai_mon', 'Khác')}", COLOR_ACCENT_BG, COLOR_ACCENT)
    
    # Định dạng chuỗi hiển thị thời gian thông minh (Ví dụ: 90 phút -> 1 giờ 30 phút)
    def format_time(minutes):
        try:
            mins = int(minutes)
        except (ValueError, TypeError):
            return "Không rõ"
        if mins <= 0:
            return "Không rõ"
        if mins < 60:
            return f"{mins} phút"
        hours, rem = divmod(mins, 60) # Chia lấy thương số và số dư
        if rem == 0:
            return f"{hours} giờ"
        return f"{hours} giờ {rem} phút"

    # Vẽ huy hiệu Thời gian nấu
    make_badge(f_badge, f"⏱  {format_time(data.get('thoi_gian', 0))}", COLOR_ACCENT2_BG, COLOR_ACCENT2)

    # ── BẢNG NGUYÊN LIỆU & ĐỊNH LƯỢNG ──
    tk.Label(main, text="🥬  Nguyên liệu & Định lượng", font=("Segoe UI", 14, "bold"),
             bg=COLOR_BG, fg=COLOR_TEXT).pack(anchor="w", padx=24, pady=(18, 6))

    # Bóc tách nguyên liệu và định lượng được phân cách nhau bởi dấu "|"
    nl_raw = str(data.get("nguyen_lieu", "")).strip()
    dl_raw = str(data.get("dinh_luong", "")).strip()
    nl_items = [s.strip() for s in nl_raw.split("|") if s.strip()] if nl_raw else []
    dl_items = [s.strip() for s in dl_raw.split("|") if s.strip()] if dl_raw else []

    if nl_items:
        # Hộp chứa dạng bảng
        ing_container = tk.Frame(main, bg=COLOR_SURFACE, highlightbackground=COLOR_BORDER, highlightthickness=1)
        ing_container.pack(fill=tk.X, padx=24, pady=(0, 4))

        # Tiêu đề cột của bảng nguyên liệu
        header_f = tk.Frame(ing_container, bg=COLOR_PANEL)
        header_f.pack(fill=tk.X)
        tk.Label(header_f, text=" STT", font=("Segoe UI", 9, "bold"), bg=COLOR_PANEL, fg=COLOR_MUTED, width=6, anchor="center").pack(side=tk.LEFT, padx=(4, 0))
        tk.Label(header_f, text="Nguyên liệu cần có", font=("Segoe UI", 9, "bold"), bg=COLOR_PANEL, fg=COLOR_MUTED, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12, pady=6)
        tk.Label(header_f, text="Định lượng chính xác", font=("Segoe UI", 9, "bold"), bg=COLOR_PANEL, fg=COLOR_MUTED, width=20, anchor="center").pack(side=tk.RIGHT, padx=12)

        # Duyệt nạp từng dòng nguyên liệu vào bảng
        for i, nl in enumerate(nl_items):
            dl = dl_items[i] if i < len(dl_items) else "—" # Trả về "—" nếu thiếu định lượng tương ứng
            row_bg = COLOR_ROW_ODD if i % 2 == 0 else COLOR_ROW_EVEN
            row_f = tk.Frame(ing_container, bg=row_bg)
            row_f.pack(fill=tk.X)
            
            tk.Label(row_f, text=str(i + 1), font=("Segoe UI", 9), bg=row_bg, fg=COLOR_MUTED, width=6, anchor="center").pack(side=tk.LEFT, padx=(4, 0))
            tk.Label(row_f, text=nl, font=("Segoe UI", 9), bg=row_bg, fg=COLOR_TEXT, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12, pady=5)
            tk.Label(row_f, text=dl, font=("Segoe UI", 9, "bold"), bg=row_bg, fg=COLOR_ACCENT2, width=20, anchor="center").pack(side=tk.RIGHT, padx=12, pady=5)
    else:
        tk.Label(main, text="Chưa có thông tin nguyên liệu chi tiết.", font=("Segoe UI", 10, "italic"), bg=COLOR_BG, fg=COLOR_MUTED).pack(anchor="w", padx=34, pady=4)

    # ── ẢNH MINH HỌA MÓN ĂN (NẾU CÓ) ──
    img_path = str(data.get("hinh_anh", "")).strip()
    if img_path and os.path.exists(img_path):
        try:
            # Mở và điều chỉnh kích thước ảnh tỷ lệ thumbnail (rộng tối đa 480px, cao tối đa 280px)
            img = Image.open(img_path)
            img.thumbnail((480, 280))
            photo = ImageTk.PhotoImage(img)
            
            lbl_img = tk.Label(main, image=photo, bg=COLOR_BG)
            lbl_img.image = photo  # Đăng ký tham chiếu ảnh để tránh rò rỉ rác bộ nhớ làm mất ảnh
            lbl_img.pack(anchor="w", padx=24, pady=12)
        except Exception:
            pass # Bỏ qua nếu định dạng ảnh hỏng

    # ── HƯỚNG DẪN CÁC BƯỚC NẤU ĂN (TÁCH THÀNH CÁC THẺ CARD ĐẸP MẮT) ──
    tk.Label(main, text="🍳  Hướng dẫn từng bước thực hiện", font=("Segoe UI", 14, "bold"),
             bg=COLOR_BG, fg=COLOR_TEXT).pack(anchor="w", padx=24, pady=(18, 6))

    cach_lam_raw = str(data.get("cach_lam", "")).strip()
    # Tách văn bản cách nấu thành các dòng độc lập, bỏ các dòng rỗng
    step_lines = [s.strip() for s in cach_lam_raw.splitlines() if s.strip()]

    if not step_lines and not cach_lam_raw:
        tk.Label(main, text="Chưa có hướng dẫn các bước nấu cụ thể.", font=("Segoe UI", 10, "italic"), bg=COLOR_BG, fg=COLOR_MUTED).pack(anchor="w", padx=34, pady=4)
    else:
        lines_to_show = step_lines if step_lines else [cach_lam_raw]
        step_num = 0
        
        for line in lines_to_show:
            import re
            # LOẠI BỎ TIỀN TỐ ĐÁNH SỐ TỰ ĐỘNG CỦA NGƯỜI DÙNG:
            # Nếu người dùng tự gõ dạng: "Bước 1: Sơ chế..." hoặc "1. Sơ chế...", biểu thức chính quy (Regex) dưới đây
            # sẽ lọc bỏ chuỗi "Bước 1:" hay "1." đi, chỉ giữ lại chữ "Sơ chế...". 
            # Sau đó hệ thống sẽ tự đánh số lại tròn trịa cực kỳ đồng bộ!
            clean = re.sub(r'^(bước\s*\d+[:\.]?|\d+[:\.])\s*', '', line, flags=re.IGNORECASE).strip()
            if not clean:
                continue
            step_num += 1

            # Khung Card bo viền chứa thông tin của mỗi bước làm món
            card = tk.Frame(main, bg=COLOR_SURFACE, highlightbackground=COLOR_BORDER, highlightthickness=1)
            card.pack(fill=tk.X, padx=24, pady=5)

            # Biểu tượng Số thứ tự bước hình tròn màu tím đẹp mắt bên trái Card
            badge_frame = tk.Frame(card, bg=COLOR_ACCENT, width=32, height=32)
            badge_frame.pack(side=tk.LEFT, padx=(12, 0), pady=10)
            badge_frame.pack_propagate(False) # Cố định kích thước hình tròn 32x32px
            
            tk.Label(badge_frame, text=str(step_num), font=("Segoe UI", 10, "bold"), bg=COLOR_ACCENT, fg="#FFFFFF").place(relx=0.5, rely=0.5, anchor="center")

            # Văn bản mô tả bước nấu ăn bên phải Card
            tk.Label(card, text=clean, font=("Segoe UI", 10), bg=COLOR_SURFACE, fg=COLOR_TEXT,
                     justify="left", wraplength=700, anchor="w").pack(side=tk.LEFT, padx=14, pady=10, fill=tk.X, expand=True)

    # ── BẢNG GHI CHÚ / LƯU Ý KHI THỰC HIỆN ──
    tk.Label(main, text="💡  Lưu ý quan trọng khi nấu", font=("Segoe UI", 14, "bold"),
             bg=COLOR_BG, fg=COLOR_WARN).pack(anchor="w", padx=24, pady=(20, 6))

    # Khung lưu ý có nền màu vàng ấm
    note_panel = tk.Frame(main, bg=COLOR_WARN_BG, highlightbackground=COLOR_WARN, highlightthickness=1)
    note_panel.pack(fill=tk.X, padx=24, pady=(0, 24))

    luu_y_raw = str(data.get("luu_y", "")).strip()
    luu_y_lines = [s.strip() for s in luu_y_raw.splitlines() if s.strip()]

    if luu_y_lines:
        # Nạp ghi chú người dùng tự nhập
        for note in luu_y_lines:
            tk.Label(note_panel, text=f"⚠   {note}", font=("Segoe UI", 10),
                     bg=COLOR_WARN_BG, fg=COLOR_WARN, justify="left", wraplength=730, anchor="w").pack(anchor="w", padx=16, pady=5)
    else:
        # Nếu món ăn chưa có ghi chú, hiển thị 3 gợi ý nấu ăn cơ bản mặc định
        default_notes = [
            "Đảm bảo chuẩn bị đủ dụng cụ và sơ chế nguyên liệu sạch sẽ trước khi thực hiện.",
            "Nêm nếm và điều chỉnh lượng gia vị (ớt, muối, đường) phù hợp với khẩu vị gia đình.",
            "Luôn theo dõi sát nhiệt độ bếp và thời gian đun nấu để món ăn chín hoàn hảo.",
        ]
        for note in default_notes:
            tk.Label(note_panel, text=f"▸   {note}", font=("Segoe UI", 9),
                     bg=COLOR_WARN_BG, fg=COLOR_WARN, justify="left", wraplength=730, anchor="w").pack(anchor="w", padx=16, pady=4.5)

    # Khoảng trống nhỏ dưới đáy trang chi tiết cho thoáng mắt
    tk.Label(main, text="", bg=COLOR_BG).pack(pady=6)

    # Hủy bind lăn chuột cuộn canvas khi tắt cửa sổ
    def _on_destroy(event):
        if event.widget == top:
            canvas.unbind_all("<MouseWheel>")
    top.bind("<Destroy>", _on_destroy)

    return top
