[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/-QmD8cHQ)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23820488&assignment_repo_type=AssignmentRepo)

# 🍳 Quản Lý Công Thức Nấu Ăn – Nhóm 3

Ứng dụng Python Desktop giúp lưu trữ, tìm kiếm và phân tích các công thức nấu ăn một cách trực quan và hiệu quả. Dữ liệu được lưu dưới dạng file CSV, xử lý bằng `pandas` và `numpy`.

> **Môn học**: Lập trình Python – BTL 2026-1 · **Nhóm**: Nhóm 3 · **Trường**: Đại học Hạ Long (UHL)

---

## ✨ Tính năng nổi bật

| # | Tính năng | Mô tả |
|---|-----------|-------|
| 1 | **Quản lý Công thức** | Thêm, Sửa, Xoá công thức với đầy đủ thông tin: Tên, Loại món, Nguyên liệu, Định lượng, Thời gian chuẩn bị |
| 2 | **Tìm kiếm & Lọc** | Tìm kiếm toàn văn kết hợp lọc nhanh theo Loại món ăn |
| 3 | **Sắp xếp** | Click tiêu đề cột để sắp xếp tăng/giảm |
| 4 | **Import / Export CSV** | Nhập/xuất dữ liệu hàng loạt qua file `.csv` |
| 5 | **Thống kê (numpy)** | Thời gian chuẩn bị trung bình theo từng loại món; top nguyên liệu dùng nhiều nhất |
| 6 | **Validation** | Kiểm tra đầy đủ các trường bắt buộc, kiểu dữ liệu; hiển thị thông báo rõ ràng |
| 7 | **Dark UI** | Giao diện tối hiện đại, auto resize, hài hoà trên mọi kích thước cửa sổ |

---

## 📁 Cấu trúc Dự án

```
ltpt-btl-20261-nhom-3/
├── assets/                         # Icon và tài nguyên ảnh
├── controllers/
│   ├── gui_controller_congthuc.py  # Controller GUI – Công thức Nấu ăn (MÔN HỌC)
│   ├── gui_controller.py           # Controller GUI – SmartAttend (gốc)
│   └── cli_controller.py           # Controller CLI
├── data/
│   ├── congthuc.csv                # Dữ liệu công thức nấu ăn
│   └── diemdanh.csv                # Dữ liệu điểm danh (gốc)
├── models/
│   ├── congthuc.py                 # Model – Công thức Nấu ăn (pandas + numpy)
│   └── diemdanh.py                 # Model – Điểm danh (gốc)
├── views/
│   ├── gui_view_congthuc.py        # View – Giao diện Công thức Nấu ăn
│   ├── gui_view.py                 # View – Giao diện SmartAttend (gốc)
│   └── cli_view.py                 # View – Dòng lệnh
├── utils/
│   └── logger.py                   # Tiện ích ghi log
├── main.py                         # Entry Point (mặc định: Công thức Nấu ăn)
├── requirements.txt                # Thư viện phụ thuộc
├── README.md                       # Tài liệu hướng dẫn tổng quan
├── SRS.md                          # Đặc tả Yêu cầu Hệ thống
├── SAD.md                          # Thiết kế Kiến trúc Phần mềm
├── CONVENTIONS.md                  # Quy chuẩn viết code & commit
├── setup_env.bat                   # Tạo môi trường ảo & cài thư viện
├── build.bat                       # Đóng gói thành file .exe
├── clean.bat                       # Dọn dẹp file rác sau build
└── run_tests.bat                   # Chạy toàn bộ Unit Test
```

---

## 🚀 Hướng dẫn cài đặt & chạy

### Bước 1 – Khởi tạo môi trường

Nhấp đúp vào `setup_env.bat` (Windows) để tự động:
- Tạo môi trường ảo `.venv`
- Cài đặt toàn bộ thư viện từ `requirements.txt` (`pandas`, `numpy`, v.v.)

Hoặc thực hiện thủ công:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Bước 2 – Chạy ứng dụng

**Quản lý Công thức Nấu ăn (GUI – Mặc định)**
```bash
.venv\Scripts\activate
python main.py
```

**SmartAttend – Điểm danh (GUI gốc)**
```bash
python main.py --diemdanh
```

**Giao diện Dòng lệnh (CLI)**
```bash
python main.py --cli
```

### Bước 3 – Đóng gói file `.exe` (tuỳ chọn)

```bash
build.bat
```
Xuất ra `dist/` hoặc `Setup_CongThuc.exe` nếu dùng Inno Setup.

### Bước 4 – Dọn dẹp (tuỳ chọn)

```bash
clean.bat
```

---

## 📋 Định dạng file CSV import

File CSV phải có các cột sau (encoding UTF-8):

| Cột | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| `ten_mon` | text | ✅ | Tên món ăn (phải duy nhất) |
| `loai_mon` | text | ✅ | Khai vị / Món chính / Tráng miệng / Đồ uống / Khác |
| `nguyen_lieu` | text | | Các nguyên liệu, ngăn cách bằng dấu `\|` |
| `dinh_luong` | text | | Định lượng tương ứng, ngăn cách bằng dấu `\|` |
| `thoi_gian` | số nguyên | ✅ | Thời gian chuẩn bị (phút) |

---

## 👥 Tác giả / Contributors

| Tên | Vai trò |
|-----|---------|
| **Nhóm 3** | Sinh viên thực hiện BTL môn Lập trình Python |
| **ThS. Vũ Duy Sơn** | Giảng viên hướng dẫn · vuduyson@daihochalong.edu.vn |

---

*Phiên bản: 1.0.0 · Phát hành: 10/05/2026*
