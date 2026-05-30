"""
controllers/gui_controller_congthuc.py
=======================================
Controller kết nối Model (congthuc.py) và View (gui_view_congthuc.py).
Đóng vai trò là "Bộ não" quản lý luồng điều hướng của hệ thống Dashboard và xử lý các sự kiện GUI.

Ghi chú cho người mới học:
- Controller lắng nghe hành động của người dùng trên giao diện (ví dụ: bấm nút Thêm, Xóa, Tìm kiếm).
- Nó sẽ gọi Model để lấy hoặc cập nhật dữ liệu dưới Database.
- Sau đó, nó sẽ ra lệnh cho View cập nhật giao diện hiển thị cho phù hợp.
- Đây là nơi chứa toàn bộ "Logic điều khiển" (Business Logic) của phần mềm.
"""

import tkinter as tk             # Thư viện giao diện đồ họa chuẩn của Python
from tkinter import messagebox  # Thư viện hiển thị hộp thoại thông báo (cảnh báo, thông tin, xác nhận)
import pandas as pd             # Thư viện xử lý bảng dữ liệu
from models import congthuc as model  # Nhập tầng Model quản lý dữ liệu
import views.gui_view_congthuc as view  # Nhập tầng View quản lý giao diện
from utils.logger import setup_logger   # Nhập cấu hình ghi nhật ký

# Khởi tạo logger riêng cho tầng Controller
logger = setup_logger("ctrl_congthuc")

# ─── TRẠNG THÁI TOÀN CỤC CỦA ỨNG DỤNG (APPLICATION STATE) ──────────────────────
# Trong các ứng dụng lớn, ta thường đóng gói các biến này vào một Class. Tuy nhiên,
# để giữ cấu trúc đơn giản và logic nguyên bản, dự án dùng các biến ở cấp độ Module:
app_df   = pd.DataFrame()  # Bảng dữ liệu công thức nấu ăn hiện hành đang lưu trong bộ nhớ RAM
app_ui   = {}              # Bộ từ điển chứa tất cả các widget giao diện (nút bấm, ô nhập, bảng...) để dễ quản lý
app_root = None            # Đối tượng cửa sổ chính của ứng dụng Tkinter (Main Window)
active_detail_windows = {}  # Quản lý các cửa sổ xem chi tiết món ăn đang mở trên màn hình: {ten_mon: window_object}
                            # Giúp đồng bộ hóa: khi sửa/xóa món ăn, ta biết cửa sổ nào đang mở để đóng hoặc vẽ lại!


# ─── HÀM TRỢ GIÚP NỘI BỘ (INTERNAL HELPERS) ───────────────────────────

def _tai_du_lieu():
    """
    Tải dữ liệu mới nhất từ model, áp dụng bộ lọc hiển thị bảng chính
    và đồng bộ hóa toàn bộ các số liệu thống kê trên giao diện.
    """
    global app_df  # Khai báo sử dụng biến toàn cục app_df để cập nhật dữ liệu mới nhất
    
    # 1. Gọi Model đọc cơ sở dữ liệu SQLite
    app_df, ok = model.lay_danh_sach()
    if not ok:
        messagebox.showerror("Lỗi", "Không thể tải dữ liệu công thức từ cơ sở dữ liệu.")
        return

    # 2. Áp dụng bộ lọc tìm kiếm hiện hành trên giao diện và cập nhật bảng chính ở Trang chủ
    # app_df.copy() nhân bản DataFrame để tránh làm mất dữ liệu gốc khi thực hiện lọc
    display_df = _apply_filter(app_df.copy())
    view.hien_thi_bang(app_ui, display_df)  # Gọi View nạp dữ liệu đã lọc vào bảng Treeview

    # 3. Cập nhật thanh trạng thái (Status Bar) dưới đáy bảng Trang chủ
    stats = model.thong_ke(display_df)
    view.cap_nhat_status(app_ui, stats)

    # 4. Đồng bộ tính toán thống kê toàn bộ và cập nhật trang Dashboard biểu đồ tĩnh
    stats_all = model.thong_ke(app_df)
    view.cap_nhat_trang_thong_ke(app_ui, stats_all)


def _apply_filter(df):
    """
    Lọc dữ liệu DataFrame theo loại món ăn và từ khóa tìm kiếm tiếng Việt thông minh.
    
    Tham số:
      - df (DataFrame): Bản sao dữ liệu công thức nấu ăn cần lọc.
      
    Trả về:
      - DataFrame: Dữ liệu đã được lọc sạch.
    """
    import unicodedata  # Thư viện xử lý chuẩn hóa chuỗi ký tự Unicode chuẩn
    
    # Nếu bảng rỗng thì trả về luôn, không cần lọc
    if df is None or df.empty:
        return df

    # LỌC THEO LOẠI MÓN ĂN:
    loai = app_ui["cbo_filter"].get()  # Lấy giá trị đang chọn trong hộp Combobox loại món
    if loai and loai != "Tất cả":
        # Giữ lại các hàng có cột "loai_mon" bằng đúng loại món đang chọn
        df = df[df["loai_mon"] == loai]

    # LỌC THEO TỪ KHÓA TÌM KIẾM THÔNG MINH (TÌM KIẾM KHÔNG DẤU):
    keyword = app_ui["ent_search"].get().strip().lower()  # Lấy từ khóa trong ô nhập, xóa khoảng trắng và đưa về chữ thường
    if keyword:
        
        # Hàm nội bộ hỗ trợ xóa bỏ toàn bộ dấu tiếng Việt và chuyển chữ 'đ', 'Đ' thành 'd', 'D'
        # Giải thích thuật toán cho người mới:
        # - unicodedata.normalize('NFKD', input_str) sẽ phân tách các ký tự tiếng Việt có dấu
        #   thành dạng: chữ cái gốc + dấu kết hợp (ví dụ: chữ 'á' tách thành 'a' và dấu ' sắc').
        # - unicodedata.combining(c) kiểm tra xem ký tự c có phải là dấu kết hợp hay không.
        # - Ta dùng vòng lặp loại bỏ toàn bộ dấu này đi, chỉ giữ lại chữ cái gốc.
        # - Cuối cùng, dùng replace() để chuyển đổi chữ 'đ'/'Đ' thành 'd'/'D' thủ công vì normalize không tự xử lý chữ đ.
        def remove_accents(input_str):
            if not isinstance(input_str, str):
                input_str = str(input_str)
            s = unicodedata.normalize('NFKD', input_str)
            s = "".join([c for c in s if not unicodedata.combining(c)])
            return s.replace('đ', 'd').replace('Đ', 'D')
        
        # Tách từ khóa tìm kiếm thành danh sách các từ riêng biệt để thực hiện tìm kiếm AND logic
        # Ví dụ: từ khóa "cá thu" sẽ tách thành ["ca", "thu"]
        kw_parts = [remove_accents(k) for k in keyword.split()]
        
        # Hàm nội bộ kiểm tra xem một dòng dữ liệu (row) có thỏa mãn từ khóa hay không
        def check_row(row):
            # Ghép tất cả các cột dữ liệu của dòng đó (tên món, loại món, nguyên liệu, cách nấu...)
            # thành một chuỗi văn bản dài duy nhất, xóa dấu tiếng Việt và đưa về chữ thường.
            # Điều này cực kỳ mạnh mẽ vì cho phép người dùng tìm kiếm chéo cột!
            row_str = remove_accents(" ".join(row.astype(str)).lower())
            
            # Kiểm tra xem TẤT CẢ các từ trong danh sách từ khóa tìm kiếm (kw_parts) có nằm trong chuỗi dài này hay không
            # Ví dụ: Món ăn phải chứa cả từ "ca" và từ "thu" thì mới thỏa mãn (AND logic)
            return all(k in row_str for k in kw_parts)
            
        # Áp dụng hàm check_row lên từng dòng của DataFrame (axis=1 nghĩa là duyệt theo chiều ngang dòng)
        # mask sẽ là một mảng chứa các giá trị True/False
        mask = df.apply(check_row, axis=1)
        df = df[mask]  # Chỉ giữ lại các dòng có giá trị True (thỏa mãn tìm kiếm)

    return df


# ─── BỘ PHẬN XỬ LÝ SỰ KIỆN GIAO DIỆN (EVENT HANDLERS) ───────────────────────────

def on_trangchu():
    """Chuyển đổi giao diện sang màn hình Trang chủ (danh sách công thức nấu ăn)."""
    logger.info("Chuyển sang Trang chủ.")
    view.switch_page(app_ui, "trang_chu")  # Gọi View hiển thị trang chủ và ẩn các trang khác


def on_thongke():
    """Tính toán lại toàn bộ dữ liệu thống kê và chuyển đổi sang màn hình báo cáo Dashboard."""
    logger.info("Chuyển sang màn hình Thống kê.")
    stats = model.thong_ke(app_df)  # Tính toán thống kê trên toàn bộ cơ sở dữ liệu
    view.cap_nhat_trang_thong_ke(app_ui, stats)  # Ra lệnh cho View vẽ lại các biểu đồ Matplotlib
    view.switch_page(app_ui, "thong_ke")         # Chuyển tab sang trang thống kê


def on_about():
    """Chuyển đổi giao diện sang màn hình giới thiệu thông tin nhóm thực hiện và phiên bản phần mềm."""
    logger.info("Chuyển sang màn hình Giới thiệu.")
    view.switch_page(app_ui, "about")


def on_search(*_):
    """
    Thực hiện bộ lọc tìm kiếm khi người dùng bấm nút 'Tìm' hoặc nhấn phím 'Enter'.
    Sau đó vẽ lại bảng Treeview chính và cập nhật số liệu thanh trạng thái dưới đáy.
    """
    logger.info("Thực hiện tìm kiếm.")
    display_df = _apply_filter(app_df.copy())
    view.hien_thi_bang(app_ui, display_df)
    stats = model.thong_ke(display_df)
    view.cap_nhat_status(app_ui, stats)


def on_clear_search():
    """Xóa sạch từ khóa trong ô tìm kiếm, đưa bộ lọc loại món về mặc định và tải lại toàn bộ dữ liệu."""
    logger.info("Xóa bộ lọc tìm kiếm.")
    app_ui["ent_search"].delete(0, tk.END)  # Xóa sạch chữ trong ô Entry tìm kiếm
    app_ui["cbo_filter"].set("Tất cả")       # Chọn lại loại món là "Tất cả" trong Combobox
    _tai_du_lieu()                          # Nạp lại dữ liệu ban đầu


def on_them():
    """Mở cửa sổ Form Popup nhập liệu để người dùng thêm công thức món ăn mới."""
    global app_df
    logger.info("Mở Form thêm công thức.")
    # Gọi View hiển thị Form Popup (is_edit=False nghĩa là form thêm mới trống)
    data = view.hien_thi_form(app_root, is_edit=False)
    if data:
        # Nếu người dùng nhập liệu hợp lệ và bấm "Lưu lại", data sẽ chứa dữ liệu món ăn dạng dict
        app_df, ok, msg = model.them_cong_thuc(app_df, data)  # Gọi Model lưu vào cơ sở dữ liệu SQLite
        if ok:
            _tai_du_lieu()  # Tải lại bảng chính và Dashboard thống kê để hiển thị món ăn mới ngay lập tức!
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Lỗi", msg)


def on_sua():
    """
    Mở Form Popup sửa đổi thông tin cho công thức món ăn đang được chọn trên bảng.
    Hỗ trợ đồng bộ hóa giao diện cực kỳ chuyên nghiệp (Real-time update).
    """
    global app_df
    logger.info("Mở Form sửa công thức.")
    tree = app_ui["tree"]  # Lấy bảng Treeview từ giao diện

    # Lấy danh sách các dòng được tick checkbox (☑) trong bảng chính
    checked = [iid for iid in tree.get_children()
               if tree.item(iid, "values")[0] == "☑"]
    
    # Nếu không có dòng nào được tick checkbox, kiểm tra xem người dùng có click chuột bôi đen dòng nào không
    if not checked:
        checked = list(tree.selection())
        
    # Cảnh báo nếu người dùng chưa chọn món ăn nào cả
    if not checked:
        messagebox.showwarning("Cảnh báo",
            "Vui lòng tích chọn (☑) hoặc bấm chọn 1 công thức trên bảng để sửa!")
        return
        
    # Cảnh báo nếu chọn cùng lúc nhiều hơn 1 món ăn để sửa
    if len(checked) > 1:
        messagebox.showwarning("Cảnh báo",
            "Chỉ được phép chọn duy nhất 1 công thức để sửa tại một thời điểm!")
        return

    # Lấy dữ liệu của dòng đang chọn
    # vals[0]: dấu check, vals[1]: STT, vals[2]: tên món ăn
    vals = tree.item(checked[0], "values")
    ten_mon = vals[2]
    
    # Truy vấn thông tin dòng đó trong DataFrame hiện tại
    row = app_df[app_df["ten_mon"] == ten_mon]
    if row.empty:
        messagebox.showerror("Lỗi", "Không tìm thấy công thức nấu ăn tương ứng!")
        return

    # Chuyển dòng dữ liệu thành dạng từ điển dict để truyền vào form điền sẵn dữ liệu cũ
    current_data = row.iloc[0].to_dict()
    
    # Hiển thị Form Popup điền sẵn dữ liệu cũ của món ăn (is_edit=True)
    data = view.hien_thi_form(app_root, is_edit=True, current_data=current_data)
    if data:
        # Gọi Model cập nhật dữ liệu mới vào SQLite Database
        app_df, ok, msg = model.sua_cong_thuc(app_df, ten_mon, data)
        if ok:
            _tai_du_lieu()  # Cập nhật bảng biểu ngay lập tức
            
            # =========================================================================
            # ĐỒNG BỘ HÓA CỰC KỲ CHUYÊN NGHIỆP:
            # Nếu món ăn này đang được mở xem ở tab chi tiết phụ, ta phải tự động đóng
            # tab chi tiết cũ đi và mở lại tab chi tiết mới chứa thông tin đã sửa từ DB!
            # =========================================================================
            if ten_mon in active_detail_windows:
                # Tìm cửa sổ cũ đang hiển thị món ăn này
                old_win = active_detail_windows.pop(ten_mon, None)
                if old_win and old_win.winfo_exists():
                    old_win.destroy()  # Đóng cửa sổ cũ
                
                # Mở lại cửa sổ chi tiết mới với dữ liệu cập nhật
                ten_moi = data.get("ten_mon", ten_mon)
                new_data, d_ok = model.lay_chi_tiet(ten_moi)  # Truy vấn DB lấy thông tin mới nhất
                if d_ok:
                    new_win = view.hien_thi_chi_tiet(app_root, new_data)
                    if new_win:
                        active_detail_windows[ten_moi] = new_win
                        # Ràng buộc sự kiện: Khi người dùng tự tay tắt cửa sổ chi tiết mới, 
                        # ta tự động loại bỏ nó ra khỏi danh sách active_detail_windows
                        new_win.bind("<Destroy>", lambda e, name=ten_moi, w=new_win: active_detail_windows.pop(name, None) if (e.widget == w) else None)
            
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Lỗi", msg)


def on_xoa():
    """
    Xóa các công thức nấu ăn đã được tick chọn (☑).
    Đồng thời tự động tắt các cửa sổ xem chi tiết của món ăn đã bị xóa để tránh xung đột.
    """
    global app_df
    logger.info("Xóa các công thức đã chọn.")
    tree = app_ui["tree"]
    
    # Thu thập toàn bộ tên món ăn của các dòng có checkbox là "☑"
    ten_list = [tree.item(iid, "values")[2]
                for iid in tree.get_children()
                if tree.item(iid, "values")[0] == "☑"]
                
    if not ten_list:
        messagebox.showwarning("Cảnh báo",
            "Vui lòng tick chọn (☑) ít nhất 1 công thức trên bảng để xóa!")
        return
        
    # Hiện hộp thoại xác nhận có thực sự muốn xóa hay không (Yes/No)
    if messagebox.askyesno("Xác nhận",
                           f"Bạn có chắc chắn muốn xóa {len(ten_list)} công thức nấu ăn đã chọn?"):
        # Gọi Model xóa các món ăn khỏi cơ sở dữ liệu SQLite
        app_df, ok, msg = model.xoa_cong_thuc(app_df, ten_list)
        if ok:
            # =========================================================================
            # ĐỒNG BỘ HÓA: Tự động đóng các cửa sổ xem chi tiết của các món vừa bị xóa!
            # Đề phòng trường hợp người dùng đang mở xem chi tiết của món ăn đó nhưng món ăn bị xóa mất.
            # =========================================================================
            for ten in ten_list:
                win = active_detail_windows.pop(ten, None)
                if win and win.winfo_exists():
                    win.destroy()  # Đóng cửa sổ xem chi tiết
                    
            _tai_du_lieu()  # Cập nhật lại toàn bộ bảng chính và thống kê
            messagebox.showinfo("Thành công", "Đã xóa công thức nấu ăn thành công!")
        else:
            messagebox.showerror("Lỗi", msg)


def on_single_click(event):
    """
    Xử lý bật/tắt (toggle) dấu checkbox chọn dòng khi click chuột.
    - Click vào dòng: tick/untick checkbox ☑/☐ của dòng đó.
    - Click vào tiêu đề (Heading) cột 'Chọn': tự động tick/untick TOÀN BỘ các dòng trên bảng!
    """
    tree = app_ui["tree"]
    region = tree.identify_region(event.x, event.y)  # Xác định vùng click chuột (heading, cell, row...)
    col_str = tree.identify_column(event.x)          # Xác định cột bị click chuột (dạng chuỗi "#1", "#2"...)
    if not col_str:
        return
    col_idx = int(col_str.replace("#", "")) - 1      # Chuyển đổi thành chỉ số cột (0-indexed)
    col_name = app_ui["cols"][col_idx]               # Lấy tên cột tương ứng trong danh sách cột

    # TRƯỜNG HỢP 1: Click chuột vào tiêu đề cột "Chọn" (Thanh đầu tiên của bảng) -> Chọn/Bỏ chọn tất cả các dòng
    if region == "heading" and col_name == "Chọn":
        cur = tree.heading("Chọn", "text")           # Đọc tiêu đề hiện tại đang hiển thị
        new_mark = "☑" if "☐" in cur else "☐"        # Đảo trạng thái tiêu đề
        tree.heading("Chọn", text=new_mark)          # Đổi chữ tiêu đề thành ký tự mới
        
        # Duyệt qua toàn bộ tất cả các dòng hiện có trên bảng Treeview
        for iid in tree.get_children():
            vals = list(tree.item(iid, "values"))
            vals[0] = new_mark                       # Gán checkbox của tất cả dòng bằng trạng thái mới
            tree.item(iid, values=vals)              # Cập nhật lại dòng trên bảng giao diện
        return

    # TRƯỜNG HỢP 2: Click chuột trực tiếp vào ô Checkbox (cell Chọn) của một dòng -> Đảo trạng thái dòng đó
    if region == "cell" and col_name == "Chọn":
        iid = tree.identify_row(event.y)             # Xác định dòng cụ thể bị click chuột
        if iid:
            vals = list(tree.item(iid, "values"))
            # Đảo ký hiệu check: ☐ thành ☑ và ngược lại
            vals[0] = "☑" if vals[0] == "☐" else "☐"
            tree.item(iid, values=vals)              # Cập nhật giao diện cell


def on_double_click(event):
    """
    Xử lý khi người dùng double-click (click đúp chuột trái) vào một dòng trên bảng chính.
    Hành động này sẽ mở ra cửa sổ phụ thiết kế đẹp mắt để xem chi tiết hướng dẫn nấu món ăn.
    """
    tree = app_ui["tree"]
    
    # Chỉ mở chi tiết khi click đúp trúng ô dữ liệu (cell) chứ không phải tiêu đề hay vùng trống
    if tree.identify_region(event.x, event.y) != "cell":
        return
    iid = tree.identify_row(event.y)  # Xác định dòng bị click đúp
    if not iid:
        return
    
    vals = list(tree.item(iid, "values"))
    ten_mon = vals[2]  # Lấy tên món ăn ở cột 2
    
    # =========================================================================
    # ĐỒNG BỘ VÀ TỐI ƯU HÓA:
    # Nếu cửa sổ chi tiết của món ăn này đã được mở sẵn và đang nằm ở đâu đó trên màn hình,
    # ta chỉ cần mang nó nổi lên trên cùng (lift) và focus chuột vào nó, tránh mở chồng chất
    # nhiều cửa sổ trùng lặp gây tốn RAM hệ thống!
    # =========================================================================
    if ten_mon in active_detail_windows:
        win = active_detail_windows[ten_mon]
        if win and win.winfo_exists():
            win.lift()       # Mang cửa sổ nổi lên trên cùng
            win.focus_set()  # Đặt tiêu điểm chuột vào cửa sổ
            return
            
    # Gọi Model lấy thông tin đầy đủ và mới nhất trực tiếp từ cơ sở dữ liệu SQLite
    current_data, ok = model.lay_chi_tiet(ten_mon)
    if not ok:
        messagebox.showerror("Lỗi", "Không thể lấy chi tiết công thức từ cơ sở dữ liệu SQLite!")
        return
        
    # Gọi View hiển thị cửa sổ chi tiết dạng Card
    new_win = view.hien_thi_chi_tiet(app_root, current_data)
    if new_win:
        active_detail_windows[ten_mon] = new_win  # Đăng ký cửa sổ vào danh sách đang mở
        
        # Khi cửa sổ này bị tắt đi (sự kiện <Destroy>), ta tự động xóa nó khỏi danh sách active_detail_windows
        new_win.bind("<Destroy>", lambda e, name=ten_mon, w=new_win: active_detail_windows.pop(name, None) if (e.widget == w) else None)


# ─── LIÊN KẾT SỰ KIỆN VỚI WIDGET GIAO DIỆN (BIND EVENTS) ─────────────────────────

def _bind_events():
    """Gán (bind) các hàm xử lý sự kiện trong Controller vào các nút bấm và ô nhập trên giao diện View."""
    # 1. Điều hướng Sidebar trái
    app_ui["btn_trangchu"].config(command=on_trangchu)
    app_ui["btn_thongke"].config(command=on_thongke)
    app_ui["btn_about"].config(command=on_about)
    
    # 2. Thao tác trên trang danh sách công thức (Trang chủ)
    app_ui["btn_them"].config(command=on_them)
    app_ui["btn_sua"].config(command=on_sua)
    app_ui["btn_xoa"].config(command=on_xoa)
    app_ui["btn_search"].config(command=on_search)
    app_ui["btn_clear"].config(command=on_clear_search)
    
    # 3. Phím tắt và sự kiện thay đổi dữ liệu tìm kiếm
    app_ui["ent_search"].bind("<Return>", on_search)  # Gõ Enter trong ô tìm kiếm -> Tìm ngay
    app_ui["cbo_filter"].bind("<<ComboboxSelected>>", on_search)  # Thay đổi bộ lọc loại món -> Tìm ngay

    # 4. Click chuột trên bảng danh sách món ăn
    tree = app_ui["tree"]
    tree.bind("<ButtonRelease-1>", on_single_click)  # Click thả chuột trái -> xử lý checkbox
    tree.bind("<Double-1>", on_double_click)         # Click đúp chuột trái -> mở xem chi tiết hướng dẫn nấu


# ─── ĐIỂM KHỞI CHẠY CHÍNH CỦA ỨNG DỤNG (ENTRY POINT) ──────────────────────────

def chay_ung_dung():
    """Khởi chạy ứng dụng đồ họa Quản lý Công thức Nấu ăn Dashboard."""
    global app_root, app_ui
    logger.info("Khởi động Quản lý Công thức Nấu ăn Dashboard (GUI)")
    
    app_root = tk.Tk()  # Tạo cửa sổ gốc chính Tkinter
    
    # Gọi View khởi tạo, thiết kế toàn bộ giao diện và trả về bộ các Widget quản lý
    app_ui = view.tao_giao_dien_chinh(app_root)
    
    _bind_events()  # Thực hiện gán toàn bộ sự kiện click, gõ phím
    _tai_du_lieu()   # Tải dữ liệu ban đầu từ DB hiển thị lên màn hình
    
    app_root.mainloop()  # Chạy vòng lặp sự kiện chính của giao diện, giúp màn hình hiển thị liên tục và không bị tắt!
    
    logger.info("Thoát ứng dụng Công thức Nấu ăn Dashboard (GUI)")
