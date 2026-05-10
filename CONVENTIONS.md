# Mã nguồn chuẩn (Coding Conventions)
# Quản Lý Công Thức Nấu Ăn – Nhóm 3

Dự án `Quản lý Công thức Nấu ăn` hướng đến độ ổn định, khả năng bảo trì và có thể bàn giao (client-ready). Mọi đoạn code được viết ra phải tuân thủ nghiêm ngặt các tiêu chuẩn sau:

---

## 1. Naming Conventions (Quy chuẩn Đặt tên)

Áp dụng tiêu chuẩn **PEP 8**:

- **Biến và Hàm**: Sử dụng `snake_case`.  
  Ví dụ: `lay_danh_sach()`, `them_cong_thuc()`, `tong_ct`
- **Hằng số**: Sử dụng `UPPER_SNAKE_CASE`.  
  Ví dụ: `FILE_CONGTHUC`, `LOAI_MON_LIST`, `COLS_CSV`
- **Lớp (nếu có)**: Sử dụng `PascalCase`.  
  Ví dụ: `RecipeManager`
- **Tên file module**: `snake_case`, mô tả chức năng rõ ràng.  
  Ví dụ: `gui_view_congthuc.py`, `gui_controller_congthuc.py`

---

## 2. Quản lý Phiên bản (Versioning)

Sử dụng **Semantic Versioning (SemVer)** `v[MAJOR].[MINOR].[PATCH]`:

| Loại | Khi nào dùng | Ví dụ |
|------|-------------|-------|
| `MAJOR` | Thay đổi cấu trúc dữ liệu CSV hoặc kiến trúc lớn | `v1.x` → `v2.0.0` |
| `MINOR` | Thêm tính năng mới (cột mới, filter mới, thống kê mới) | `v1.0` → `v1.1.0` |
| `PATCH` | Vá lỗi, chỉnh sửa UI nhỏ | `v1.0.0` → `v1.0.1` |

Phiên bản hiện tại được khai báo tại `main.py`:
```python
__version__ = "1.0.0"
```

---

## 3. Khối Chú thích (Docstrings)

Mọi hàm và module **bắt buộc** có Docstring theo chuẩn **Google Python Style Guide**:

```python
def them_cong_thuc(df, data):
    """
    Thêm một công thức nấu ăn mới vào DataFrame.

    Args:
        df (pandas.DataFrame): Bảng dữ liệu công thức hiện tại.
        data (dict): Thông tin công thức mới gồm các key:
            ten_mon (str), loai_mon (str), nguyen_lieu (str),
            dinh_luong (str), thoi_gian (int).

    Returns:
        tuple: (DataFrame mới, bool True nếu thành công, str thông báo)
    """
```

**Quy tắc bổ sung:**
- Mọi hàm Model trả về tuple `(df, bool, str)` để Controller xử lý nhất quán.
- File module phải có docstring mô tả mục đích và layer (Model/View/Controller).

---

## 4. Hệ thống Vết (Logging)

Thay vì dùng `print()`, toàn bộ hành vi quan trọng phải dùng `utils/logger.py`.  
Log tự động ghi ra `data/app.log`.

| Mức | Khi nào dùng |
|-----|-------------|
| `logger.debug()` | Chi tiết xử lý nội bộ, vòng lặp (dev đọc) |
| `logger.info()` | Ghi vết thao tác user: Thêm / Sửa / Xóa / Tìm kiếm |
| `logger.warning()` | Lỗi logic nhỏ, thiếu dữ liệu tùy chọn |
| `logger.error()` | Bắt buộc trong mọi `try...except`, kèm chi tiết lỗi |

---

## 5. Input Validation

Controller chịu trách nhiệm validate trước khi gọi Model:

- **Trường bắt buộc trống** → Hiển thị label đỏ ngay trong form: `"⚠ Mời bạn nhập Tên món ăn!"`
- **Sai kiểu dữ liệu** (thời gian không phải số) → `"⚠ Thời gian phải là số nguyên >= 0!"`
- **Trùng dữ liệu** → `messagebox.showerror` với thông báo rõ ràng
- **Chọn nhiều dòng khi Sửa** → `"Chỉ được chọn 1 công thức để sửa!"`
- **Không chọn dòng khi Xóa** → `"Vui lòng tick (☑) ít nhất 1 công thức để xóa!"`

---

## 6. Cấu trúc Commit Message

Định dạng: `[type]: [nội dung ngắn gọn bằng tiếng Việt`

| Type | Ý nghĩa |
|------|---------|
| `feat` | Thêm tính năng mới |
| `fix` | Vá lỗi |
| `refactor` | Tái cấu trúc code, không đổi logic |
| `docs` | Cập nhật tài liệu (README, SRS, SAD) |
| `style` | Thay đổi UI/UX, màu sắc, layout |
| `test` | Thêm hoặc sửa unit test |
| `chore` | Cấu hình build, script .bat |

**Ví dụ:**
```
feat: thêm chức năng thống kê nguyên liệu phổ biến
fix: sửa lỗi sort cột khi giá trị rỗng
docs: cập nhật SAD.md theo kiến trúc MVC mới
```
