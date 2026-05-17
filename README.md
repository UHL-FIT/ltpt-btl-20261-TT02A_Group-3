[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/-QmD8cHQ)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23820488&assignment_repo_type=AssignmentRepo)

# 🍳 Quản Lý Công Thức Nấu Ăn – Nhóm 3

Ứng dụng Python Desktop giúp lưu trữ, tìm kiếm và phân tích các công thức nấu ăn một cách trực quan và hiệu quả. Dữ liệu được lưu trong **SQLite Database**, xử lý bằng `pandas` và `numpy`, giao diện xây dựng bằng `Tkinter`.

> **Môn học**: Lập trình Python – BTL 2026-1 · **Nhóm**: Nhóm 3 · **Trường**: Đại học Hạ Long (UHL)

---

## ✨ Tính năng nổi bật

| # | Tính năng | Mô tả |
|---|-----------|-------|
| 1 | **Quản lý Công thức** | Thêm, Sửa, Xoá công thức với đầy đủ thông tin: Tên, Loại món, Nguyên liệu, Định lượng, Thời gian chuẩn bị, Cách làm, Lưu ý |
| 2 | **Tìm kiếm & Lọc** | Tìm kiếm toàn văn kết hợp lọc nhanh theo Loại món ăn |
| 3 | **Sắp xếp** | Click tiêu đề cột để sắp xếp tăng/giảm |
| 4 | **Chi tiết từng bước** | Cửa sổ chi tiết hiển thị hướng dẫn nấu ăn theo từng bước có đánh số, kèm lưu ý riêng cho từng món |
| 5 | **Thống kê (numpy)** | Thời gian chuẩn bị trung bình theo từng loại món; top nguyên liệu dùng nhiều nhất (biểu đồ matplotlib) |
| 6 | **Validation** | Kiểm tra đầy đủ các trường bắt buộc, kiểu dữ liệu; hiển thị thông báo rõ ràng |
| 7 | **Dark UI** | Giao diện tối hiện đại, auto resize, hài hoà trên mọi kích thước cửa sổ |
| 8 | **SQLite Backend** | Lưu trữ dữ liệu bền vững bằng SQLite3, tự động tạo DB và migrate khi khởi động |

---

## 📁 Cấu trúc Dự án

```
ltpt-btl-20261-nhom-3/
├── assets/                         # Icon và tài nguyên ảnh
├── controllers/
│   └── gui_controller_congthuc.py  # Controller GUI – Công thức Nấu ăn
├── data/
│   ├── congthuc.db                 # SQLite Database (tự động tạo khi chạy lần đầu)
│   └── app.log                     # File log ứng dụng
├── models/
│   └── congthuc.py                 # Model – Công thức Nấu ăn (SQLite3 + pandas + numpy)
├── views/
│   └── gui_view_congthuc.py        # View – Giao diện Công thức Nấu ăn (Tkinter)
├── utils/
│   └── logger.py                   # Tiện ích ghi log
├── tests/
│   └── test_congthuc.py            # Unit Test cho Model
├── main.py                         # Entry Point (mặc định: Công thức Nấu ăn)
├── main_cli.py                     # Entry Point CLI
├── requirements.txt                # Thư viện phụ thuộc
├── README.md                       # Tài liệu hướng dẫn tổng quan
├── SRS.md                          # Đặc tả Yêu cầu Hệ thống
├── SAD.md                          # Thiết kế Kiến trúc Phần mềm
├── CONVENTIONS.md                  # Quy chuẩn viết code & commit
├── setup_env.bat                   # Tạo môi trường ảo & cài thư viện
└── run_tests.bat                   # Chạy toàn bộ Unit Test
```

---

## 🗄️ Cấu trúc Database

Dữ liệu được lưu trong file `data/congthuc.db` (SQLite3) với bảng `congthuc`:

| Cột | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| `id` | INTEGER | ✅ | Khoá chính tự tăng |
| `ten_mon` | TEXT | ✅ | Tên món ăn (phải duy nhất) |
| `loai_mon` | TEXT | ✅ | Khai vị / Món chính / Tráng miệng / Đồ uống / Khác |
| `nguyen_lieu` | TEXT | | Các nguyên liệu, ngăn cách bằng dấu `\|` |
| `dinh_luong` | TEXT | | Định lượng tương ứng, ngăn cách bằng dấu `\|` |
| `thoi_gian` | INTEGER | ✅ | Thời gian chuẩn bị (phút) |
| `cach_lam` | TEXT | | Hướng dẫn nấu ăn, mỗi bước một dòng |
| `hinh_anh` | TEXT | | Đường dẫn tuyệt đối tới file ảnh |
| `luu_y` | TEXT | | Lưu ý khi nấu, đặc thù cho từng món (mỗi ý một dòng) |

> **Lưu ý:** Database được tạo tự động khi chạy lần đầu. Nếu có file `congthuc.csv` cũ trong thư mục `data/`, ứng dụng sẽ tự động migrate dữ liệu sang DB.

---

## 🚀 Hướng dẫn chạy ứng dụng

> Yêu cầu: Python 3.10+ và môi trường ảo đã được kích hoạt.

**Bước 1 – Cài đặt môi trường (chỉ làm 1 lần)**
```bash
setup_env.bat
```

**Bước 2 – Chạy ứng dụng GUI (mặc định)**
```bash
python main.py
```

**Chạy giao diện dòng lệnh (CLI)**
```bash
python main_cli.py
```

**Chạy Unit Test**
```bash
run_tests.bat
# hoặc
python -m pytest tests/ -v
```

---

## 🍽️ Dữ liệu mẫu (10 món)

Ứng dụng đi kèm **10 công thức nấu ăn** đại diện đủ các loại:

| # | Tên món | Loại |
|---|---------|------|
| 1 | Phở bò | Món chính |
| 2 | Cơm chiên dương châu | Món chính |
| 3 | Sinh tố bơ | Đồ uống |
| 4 | Gỏi cuốn tôm thịt | Khai vị |
| 5 | Bún bò Huế | Món chính |
| 6 | Bánh flan | Tráng miệng |
| 7 | Canh chua cá | Món chính |
| 8 | Chả giò rán | Khai vị |
| 9 | Gà nướng mật ong | Món chính |
| 10 | Bánh chuối hấp | Tráng miệng |

Mỗi món đi kèm hướng dẫn nấu chi tiết theo từng bước và **lưu ý nấu ăn riêng** phù hợp với đặc thù của món.

---

## 👥 Tác giả / Contributors

| Tên | Vai trò |
|-----|---------|
| Lê Mạnh Quân | Người viết code |
| Hoàng Văn Thịnh | Người thuyết trình |
| Đào Mạnh Huy | Người làm báo cáo |
| Ngô Hoàng Tuấn Tú | |
| **ThS. Vũ Duy Sơn** | Giảng viên hướng dẫn · vuduyson@daihochalong.edu.vn |

---

*Phiên bản: 2.0.0 · Phát hành: 17/05/2026*
