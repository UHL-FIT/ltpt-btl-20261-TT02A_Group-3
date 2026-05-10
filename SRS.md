# Software Requirements Specification (SRS)
# Quản Lý Công Thức Nấu Ăn – Nhóm 3

> **Môn học**: Lập trình Python – BTL 2026-1  
> **Nhóm**: Nhóm 3 · **Trường**: Đại học Hạ Long (UHL)  
> **Phiên bản**: 1.0.0 · **Ngày**: 10/05/2026

---

## 1. Giới thiệu

### 1.1 Mục đích
Tài liệu này đặc tả các yêu cầu chức năng và phi chức năng cho hệ thống **Quản lý Công thức Nấu ăn** – ứng dụng Desktop Python giúp người dùng lưu trữ, tìm kiếm, sắp xếp và phân tích các công thức nấu ăn một cách khoa học và trực quan.

### 1.2 Phạm vi hệ thống
Hệ thống cho phép người dùng:
- Lưu trữ công thức nấu ăn (tên món, loại, nguyên liệu, định lượng, thời gian chuẩn bị) vào file CSV.
- Tra cứu nhanh theo từ khóa và lọc theo loại món ăn.
- Xem thống kê thời gian chuẩn bị trung bình theo từng loại món và nguyên liệu phổ biến nhất.

### 1.3 Định nghĩa & Thuật ngữ

| Thuật ngữ | Ý nghĩa |
|-----------|---------|
| Công thức | Một bản ghi gồm: Tên món, Loại món, Nguyên liệu, Định lượng, Thời gian chuẩn bị |
| Nguyên liệu | Danh sách các thành phần ngăn cách bằng ký tự `\|` |
| Định lượng | Danh sách khối lượng/thể tích tương ứng với nguyên liệu, ngăn cách bằng `\|` |
| TG chuẩn bị | Thời gian chuẩn bị món ăn tính bằng phút (số nguyên >= 0) |

---

## 2. Mô tả Tổng quan

### 2.1 Đặc điểm Người dùng (Actor)
- **Người dùng cuối**: Người trực tiếp sử dụng phần mềm để quản lý công thức nấu ăn cá nhân hoặc tập thể. Có toàn quyền Thêm, Sửa, Xoá, Tìm kiếm, Import/Export.

### 2.2 Môi trường Hoạt động
- Chạy trên hệ điều hành **Windows 10/11** (có cung cấp file `.exe`).
- Không yêu cầu kết nối Internet (ứng dụng Desktop chạy hoàn toàn Offline).
- Dữ liệu được lưu cục bộ tại `data/congthuc.csv`.

---

## 3. Yêu cầu Chức năng (Functional Requirements)

### FR1: Giao diện Chính (Main Window)

**FR1.1 Bố cục giao diện (ít nhất 3 Windows)**
- **01 Main window**: Hiển thị bảng dữ liệu công thức, thanh công cụ (Thêm, Sửa, Xoá, Import CSV, Export CSV, Thống kê, About), ô tìm kiếm toàn văn, bộ lọc Loại món, thanh trạng thái (tổng số công thức, thời gian TB).
- **02 Sub windows**: 01 popup **Thêm công thức** mới và 01 popup **Sửa công thức** (dùng chung form, phân biệt qua tham số `is_edit`).
- **01 Sub window Thống kê**: Popup hiển thị bảng thống kê chi tiết.

**FR1.2 Bảng dữ liệu**
- Hiển thị các cột: Chọn (☐/☑), STT, Tên món, Loại món, Nguyên liệu, Định lượng, TG (phút).
- Hỗ trợ **sắp xếp** tăng/giảm khi click tiêu đề cột.
- Có thanh cuộn ngang và dọc khi dữ liệu nhiều.
- Hai màu xen kẽ (striped rows) để dễ đọc.

**FR1.3 Checkbox & Chọn nhiều dòng**
- Cột "Chọn" dùng ký tự ☐/☑ để đánh dấu dòng.
- Click vào header "Chọn" để chọn/bỏ chọn tất cả.
- Xoá hàng loạt dựa trên các dòng được tích ☑.

---

### FR2: Quản lý Công thức (CRUD)

**FR2.1 Thêm công thức**
- Người dùng nhập: Tên món (*), Loại món (*), Nguyên liệu, Định lượng, Thời gian chuẩn bị (*).
- Tên món phải là duy nhất (không phân biệt hoa/thường).
- Sau khi lưu: cập nhật ngay bảng chính và file CSV.

**FR2.2 Sửa công thức**
- Chọn đúng 1 dòng (☑ hoặc click) rồi bấm Sửa, hoặc Double-click vào dòng.
- Form điền sẵn dữ liệu cũ, người dùng chỉnh sửa rồi lưu.
- Nếu chọn nhiều hơn 1 dòng → thông báo "Chỉ được chọn 1 công thức để sửa!".

**FR2.3 Xoá công thức**
- Tick chọn (☑) ít nhất 1 dòng, bấm Xoá → hộp thoại xác nhận → xoá và cập nhật.

---

### FR3: Tìm kiếm & Lọc

**FR3.1 Tìm kiếm toàn văn**
- Nhập từ khóa → tìm trên tất cả các cột (tên món, loại, nguyên liệu, định lượng).
- Hỗ trợ Enter để tìm kiếm nhanh.

**FR3.2 Lọc theo Loại món**
- Combobox "Lọc theo loại" với các giá trị: Tất cả, Khai vị, Món chính, Tráng miệng, Đồ uống, Khác.
- Tự động cập nhật bảng và thống kê khi thay đổi bộ lọc.

**FR3.3 Xoá bộ lọc**
- Nút ✖ đặt lại từ khóa tìm kiếm và loại lọc về "Tất cả".

---

### FR4: Import / Export Dữ liệu

**FR4.1 Import CSV**
- Cho phép chọn file CSV từ máy tính; file phải có cột `ten_mon`, `loai_mon`, `thoi_gian`.
- Tự động bỏ qua các dòng trùng tên món đã tồn tại; thông báo số lượng đã import.

**FR4.2 Export CSV**
- Xuất toàn bộ dữ liệu hiện tại ra file CSV (encoding UTF-8-sig để mở được trên Excel tiếng Việt).

---

### FR5: Thống kê (numpy + pandas)

**FR5.1 Thống kê nhanh (thanh trạng thái)**
- Hiển thị tổng số công thức và thời gian chuẩn bị trung bình (tất cả công thức đang hiển thị).

**FR5.2 Cửa sổ Thống kê chi tiết**
- Tổng số công thức, TG ngắn nhất, TG dài nhất, TG TB toàn bộ.
- **Thời gian chuẩn bị trung bình theo từng Loại món** (tính bằng `numpy.mean` cho từng nhóm).
- **Top 10 nguyên liệu được dùng nhiều nhất** (tách chuỗi `|`, đếm tần suất bằng `pandas.Series.value_counts()`).

---

### FR6: About

- Hiển thị hộp thoại thông tin: Tên phần mềm, Phiên bản, Nhóm thực hiện, Trường, Ngày phát hành.

---

## 4. Yêu cầu Phi chức năng (Non-Functional Requirements)

### NFR1: Kiến trúc & Công nghệ

- Áp dụng kiến trúc **MVC** (module-level, không dùng class):
  - **Model** (`models/congthuc.py`): Lưu trữ CSV; **bắt buộc** dùng `pandas` và `numpy`.
  - **View** (`views/gui_view_congthuc.py`): Tkinter – button, Entry, Text, Combobox, Treeview, Toplevel.
  - **Controller** (`controllers/gui_controller_congthuc.py`): Python cơ bản điều phối View ↔ Model.

### NFR2: Trải nghiệm Người dùng (UI/UX)

- Sắp xếp widget (button, bảng, ô tìm kiếm) hài hoà, hợp lý, tiện sử dụng.
- Toàn bộ layout sử dụng `pack` với `fill` và `expand` để **auto resize/align** khi kéo cửa sổ.
- Giao diện Dark theme: palette màu tối nhất quán, font Segoe UI, padding đồng đều.

### NFR3: Kiểm tra Dữ liệu Đầu vào (Validation)

- **Trường bắt buộc trống**: Hiển thị thông báo ngay trong form (label màu đỏ), không đóng popup.
  - "⚠ Mời bạn nhập Tên món ăn!"
  - "⚠ Mời bạn chọn Loại món ăn!"
  - "⚠ Mời bạn nhập Nguyên liệu!"
  - "⚠ Mời bạn nhập Định lượng!"
  - "⚠ Mời bạn nhập Thời gian chuẩn bị!"
- **Sai kiểu dữ liệu**: "⚠ Thời gian phải là số nguyên >= 0!"
- **Trùng tên món**: Thông báo lỗi qua `messagebox.showerror`.
- **Sửa nhiều dòng**: Thông báo "Chỉ được chọn 1 công thức để sửa!".
- **Xoá không chọn dòng**: Thông báo "Vui lòng tick (☑) ít nhất 1 công thức để xóa!".

### NFR4: Hiệu năng

- Load và hiển thị tối thiểu 1.000 công thức trong vòng < 2 giây.
- Sử dụng vectorization của `numpy` thay cho vòng lặp Python thuần khi tính thống kê.

### NFR5: Lưu trữ Dữ liệu

- File `data/congthuc.csv` được tự động tạo nếu chưa tồn tại khi khởi động.
- Encoding: `utf-8-sig` để tương thích Excel tiếng Việt.
