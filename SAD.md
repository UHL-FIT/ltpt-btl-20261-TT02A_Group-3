# Software Architecture Document (SAD)
# Quản Lý Công Thức Nấu Ăn – Nhóm 3

> **Môn học**: Lập trình Python – BTL 2026-1  
> **Nhóm**: Nhóm 3 · **Trường**: Đại học Hạ Long (UHL)  
> **Phiên bản**: 2.0.0 · **Ngày**: 17/05/2026

---

## 1. Giới thiệu

Tài liệu này mô tả kiến trúc tổng thể của ứng dụng **Quản lý Công thức Nấu ăn** – bao gồm các quyết định thiết kế, cấu trúc source code, luồng dữ liệu và công nghệ sử dụng. Mục tiêu là cung cấp cái nhìn rõ ràng cho bất kỳ developer nào muốn hiểu hoặc mở rộng hệ thống.

---

## 2. Kiến trúc Tổng thể (Architectural Pattern)

Ứng dụng được xây dựng theo kiến trúc **MVC (Model – View – Controller)** kết hợp mô hình phân lớp đơn giản dành cho Desktop, triển khai ở cấp độ **module (không dùng class)** để phù hợp với trình độ Python cơ bản.

```
┌──────────────────────────────────────────────────────────┐
│                        USER                              │
│          (click chuột / nhập bàn phím)                   │
└────────────────────────┬─────────────────────────────────┘
                         │ sự kiện
                         ▼
┌──────────────────────────────────────────────────────────┐
│              VIEW  (gui_view_congthuc.py)                 │
│  Tkinter widgets: Treeview, Button, Entry, Combobox...   │
│  • Hiển thị dữ liệu                                      │
│  • Không chứa business logic                             │
└────────────────────────┬─────────────────────────────────┘
                         │ gọi handler
                         ▼
┌──────────────────────────────────────────────────────────┐
│         CONTROLLER  (gui_controller_congthuc.py)         │
│  • Validate input (kiểm tra trống, kiểu dữ liệu...)      │
│  • Điều phối luồng: View → Model → View                  │
│  • Hiển thị messagebox cảnh báo / xác nhận               │
└──────────┬─────────────────────────────┬─────────────────┘
           │ gọi hàm                     │ trả về (df, ok, msg)
           ▼                             │
┌──────────────────────┐                 │
│  MODEL (congthuc.py) │─────────────────┘
│  • CRUD SQLite DB    │
│  • Trả về DataFrame  │
│  • Thống kê numpy    │
│  • Không biết về UI  │
└──────────┬───────────┘
           │ đọc / ghi
           ▼
┌──────────────────────┐
│   DATA SOURCE        │
│   data/congthuc.db   │
│   (SQLite3)          │
└──────────────────────┘
```

### Vai trò từng tầng

| Tầng | File | Nhiệm vụ |
|------|------|----------|
| **Model** | `models/congthuc.py` | CRUD dữ liệu SQLite3; trả về DataFrame; tính toán thống kê bằng `pandas` và `numpy` |
| **View** | `views/gui_view_congthuc.py` | Xây dựng và hiển thị toàn bộ widget Tkinter; không chứa logic nghiệp vụ |
| **Controller** | `controllers/gui_controller_congthuc.py` | Bắt sự kiện từ View, validate, gọi Model, cập nhật lại View |
| **Utility** | `utils/logger.py` | Ghi log DEBUG/INFO/ERROR ra file `data/app.log` |
| **Entry Point** | `main.py` | Khởi động ứng dụng GUI |

---

## 3. Cấu trúc Source Code

```
ltpt-btl-20261-nhom-3/
├── data/
│   ├── congthuc.db                 # SQLite Database chính (tự tạo khi chạy lần đầu)
│   └── app.log                     # File log tự động
│
├── models/
│   └── congthuc.py                 # Model: CRUD công thức (SQLite3) + thống kê numpy/pandas
│
├── views/
│   └── gui_view_congthuc.py        # View: Dark UI – Main window + form popup + thống kê
│
├── controllers/
│   └── gui_controller_congthuc.py  # Controller: kết nối View ↔ Model công thức
│
├── utils/
│   └── logger.py                   # Logging toàn ứng dụng
│
├── assets/                         # Icon .ico
├── tests/                          # Unit Test
├── main.py                         # Entry Point (GUI)
└── main_cli.py                     # Entry Point (CLI)
```

---

## 4. Thiết kế Chi tiết Các Module

### 4.1 Model – `models/congthuc.py`

**Hằng số & Cấu hình**

| Hằng | Giá trị | Mục đích |
|------|---------|----------|
| `FILE_DB` | `data/congthuc.db` | Đường dẫn file SQLite Database |
| `LOAI_MON_LIST` | `["Khai vị", "Món chính", ...]` | Danh mục loại món |
| `COLS_DB` | `["ten_mon", "loai_mon", ..., "luu_y"]` | Thứ tự cột trả về |

**Các hàm công khai**

| Hàm | Tham số | Trả về | Mô tả |
|-----|---------|--------|-------|
| `khoi_tao_db()` | — | — | Tạo DB + bảng nếu chưa có; auto-migrate CSV cũ |
| `lay_danh_sach()` | — | `(DataFrame, bool)` | Đọc từ SQLite, trả về df |
| `them_cong_thuc(df, data)` | df, dict | `(df, bool, str)` | INSERT vào DB |
| `sua_cong_thuc(df, old_ten, data)` | df, str, dict | `(df, bool, str)` | UPDATE trong DB |
| `xoa_cong_thuc(df, ten_list)` | df, list | `(df, bool, str)` | DELETE nhiều hàng khỏi DB |
| `thong_ke(df)` | df | `dict` | Thống kê tổng quan + numpy |

**Quy ước trả về của CRUD:**  
Mọi hàm CRUD đều trả về tuple `(DataFrame_mới, bool_thành_công, str_thông_báo)` để Controller xử lý nhất quán.

**Kỹ thuật numpy sử dụng:**
```python
# Thời gian trung bình toàn bộ
tg_tb = float(np.mean(thoi_gian_arr))

# Thời gian TB theo nhóm loại món
for loai in df["loai_mon"].unique():
    arr = pd.to_numeric(df.loc[df["loai_mon"]==loai, "thoi_gian"], errors="coerce").values
    tg_theo_loai[loai] = float(np.mean(arr))

# Top nguyên liệu phổ biến (pandas)
nl_series = pd.Series(all_nls)
top_nl = nl_series.value_counts().head(10)
```

---

### 4.2 View – `views/gui_view_congthuc.py`

**Bố cục Main Window** (từ trên xuống dưới):

```
┌─────────────────────────────────────────────────────────┐
│  HEADER BAR  (tím – bg=COLOR_ACCENT)                    │
│  🍳 Quản Lý Công Thức Nấu Ăn                            │
├─────────────────────────────────────────────────────────┤
│  TOOLBAR  (bg=COLOR_SURFACE)                            │
│  [＋Thêm] [✏Sửa] [🗑Xóa] | [📂Import] [💾Export]       │
│                    | [📊Thống kê] [ℹ️About]  🔍[___][Tìm]│
├─────────────────────────────────────────────────────────┤
│                                                         │
│  TREEVIEW (fill=BOTH, expand=True)                      │
│  ☐ | STT | Tên món | Loại | Nguyên liệu | Định lượng | TG│
│  ─────────────────────────────────────────── ↕ scroll   │
│                                          ── ↔ scroll    │
├─────────────────────────────────────────────────────────┤
│  STATUS BAR  (bg=COLOR_SURFACE)                         │
│  Tổng: N công thức   TG TB: X.X phút    💡 hint         │
└─────────────────────────────────────────────────────────┘
```

**Palette màu Dark Theme:**

| Biến | Hex | Dùng cho |
|------|-----|----------|
| `COLOR_BG` | `#1E1E2E` | Nền cửa sổ chính |
| `COLOR_SURFACE` | `#2A2A3E` | Header bar, status bar |
| `COLOR_PANEL` | `#313145` | Panel phụ |
| `COLOR_ACCENT` | `#7C3AED` | Header, nút Thêm |
| `COLOR_ACCENT2` | `#10B981` | Nút Tìm |
| `COLOR_DANGER` | `#EF4444` | Nút Xóa |
| `COLOR_TEXT` | `#E2E8F0` | Văn bản chính |
| `COLOR_MUTED` | `#94A3B8` | Nhãn phụ, hint |

**Auto-resize:** Sử dụng `pack(fill=tk.BOTH, expand=True)` cho `frame_mid` chứa Treeview → tự giãn khi kéo cửa sổ.

**Các hàm View công khai:**

| Hàm | Mô tả |
|-----|-------|
| `tao_giao_dien_chinh(root)` | Khởi tạo toàn bộ layout, trả về dict `ui` |
| `hien_thi_bang(ui, df)` | Xóa và render lại Treeview từ DataFrame |
| `cap_nhat_status(ui, stats)` | Cập nhật thanh trạng thái phía dưới |
| `hien_thi_form(parent, is_edit, current_data)` | Popup Thêm/Sửa (gồm cả ô Lưu ý), trả về dict hoặc None |
| `hien_thi_chi_tiet(parent, data)` | Popup chi tiết từng bước + lưu ý riêng theo món |
| `hien_thi_thong_ke(parent, stats)` | Popup thống kê chi tiết (biểu đồ matplotlib) |

---

### 4.3 Controller – `controllers/gui_controller_congthuc.py`

**State module-level:**
```python
app_df   = pd.DataFrame()   # DataFrame hiện tại
app_ui   = {}               # Dict widget từ View
app_root = None             # Cửa sổ gốc Tk
```

**Bảng Event Handler:**

| Handler | Trigger | Hành động |
|---------|---------|-----------|
| `on_them()` | Nút ＋Thêm | Mở form → validate → model.them → reload |
| `on_sua()` | Nút ✏Sửa / Double-click | Kiểm tra chọn 1 dòng → form → model.sua → reload |
| `on_xoa()` | Nút 🗑Xóa | Kiểm tra ☑ → confirm → model.xoa → reload |
| `on_search(*_)` | Nút Tìm / Enter / Combobox | `_apply_filter()` → hien_thi_bang |
| `on_clear_search()` | Nút ✖ | Reset filter → reload |
| `on_import()` | Nút 📂Import | Chọn file → đọc CSV → thêm từng dòng → reload |
| `on_export()` | Nút 💾Export | Chọn nơi lưu → ghi CSV |
| `on_thongke()` | Nút 📊Thống kê | model.thong_ke → view.hien_thi_thong_ke |
| `on_about()` | Nút ℹ️About | messagebox.showinfo |
| `on_single_click(e)` | Click chuột Treeview | Toggle ☐/☑ |
| `on_double_click(e)` | Double-click Treeview | Đánh dấu dòng → gọi on_sua() |

---

## 5. Luồng Dữ liệu (Data Flow)

### 5.1 Ví dụ: Thêm công thức mới

```
[User bấm ＋Thêm]
       │
       ▼
Controller.on_them()
       │  mở popup
       ▼
View.hien_thi_form(is_edit=False)
       │  user nhập liệu, bấm Lưu
       │  validate inline (label đỏ nếu trống)
       ▼
Controller nhận dict data
       │  gọi
       ▼
Model.them_cong_thuc(app_df, data)
       │  kiểm tra trùng tên
       │  SQLite INSERT INTO congthuc
       │  trả về (df_mới, True, "Thêm thành công!")
       ▼
Controller._tai_du_lieu()
       │  apply_filter → hien_thi_bang → cap_nhat_status
       ▼
[Bảng UI cập nhật ngay lập tức]
```

### 5.2 Ví dụ: Xem Thống kê

```
[User bấm 📊Thống kê]
       │
       ▼
Controller.on_thongke()
       │  gọi
       ▼
Model.thong_ke(app_df)
       │  numpy.mean(thoi_gian_arr) → TG TB
       │  numpy.mean theo từng nhóm loại_mon
       │  pd.Series(all_nls).value_counts() → top NL
       │  trả về dict stats
       ▼
View.hien_thi_thong_ke(parent, stats)
       │  render popup với các label
       ▼
[Popup Thống kê hiển thị]
```

---

## 6. Công nghệ Sử dụng

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **Python** | 3.10+ | Ngôn ngữ lập trình chính |
| **sqlite3** | stdlib | Lưu trữ dữ liệu bền vững (thay thế CSV) |
| **pandas** | ≥ 1.3 | Quản lý DataFrame trả về từ SQLite, `value_counts()` |
| **numpy** | ≥ 1.21 | Tính toán thống kê vectorized (`mean`, `max`, `min`) |
| **tkinter** | stdlib | Giao diện đồ hoạ Desktop (Treeview, Toplevel, ttk) |
| **matplotlib** | ≥ 3.5 | Biểu đồ thống kê (Bar chart, Pie chart) |
| **Pillow** | ≥ 9.0 | Hiển thị hình ảnh món ăn trong cửa sổ chi tiết |
| **logging** | stdlib | Ghi log ứng dụng ra `data/app.log` |
| **unittest** | stdlib | Kiểm thử tự động |

---

## 7. Quyết định Kiến trúc Quan trọng

| Quyết định | Lý do |
|-----------|-------|
| **Module-level state** thay vì class | Đơn giản hơn, phù hợp với sinh viên học Python cơ bản, nhất quán với codebase gốc |
| **SQLite3** làm Data Source | Dữ liệu bền vững, hỗ trợ UNIQUE constraint, dễ mở rộng cột mới, tự migrate CSV cũ |
| **pandas + numpy** bắt buộc | Minh họa xử lý dữ liệu dạng bảng và tính toán vectorized theo yêu cầu môn học |
| **Nguyên liệu lưu chuỗi `\|`** | Tránh bảng phụ; đủ đơn giản để parse, split và thống kê |
| **Cột `luu_y` riêng biệt** | Tách biệt lưu ý khỏi cách làm giúp hiển thị và chỉnh sửa độc lập |
| **Validation trong Controller** (không trong View) | Controller là lớp trung gian phù hợp nhất; View chỉ hiển thị |
| **Tuple `(df, bool, msg)`** làm return của Model | Nhất quán, Controller dễ xử lý phân nhánh success/error |
