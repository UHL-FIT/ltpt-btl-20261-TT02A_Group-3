"""
controllers/api_controller.py
=============================
Controller cho Web API (sử dụng Flask).
Đóng vai trò là cổng giao tiếp (API Gateway/Controller) giúp các ứng dụng khác 
(web, mobile, hoặc script Python khác) có thể giao tiếp với dữ liệu (Model) của chúng ta.

Trong mô hình MVC:
- Web API đóng vai trò như một Controller đặc biệt. Thay vì trả về giao diện đồ họa (View bằng Tkinter),
  nó nhận yêu cầu (HTTP Request) dưới dạng dữ liệu (JSON/Query String), gọi Model để xử lý, 
  và trả kết quả về dưới dạng JSON (JavaScript Object Notation) - định dạng dữ liệu chuẩn quốc tế.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from models import congthuc as model
import pandas as pd
from utils.logger import setup_logger

# Khởi tạo logger cho API
logger = setup_logger("api_controller")

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
# Cho phép CORS (Cross-Origin Resource Sharing) để các trang web chạy ở cổng khác
# vẫn có thể gọi API này bình thường mà không bị trình duyệt chặn.
CORS(app)

# Đảm bảo cơ sở dữ liệu đã được khởi tạo trước khi API hoạt động
model.khoi_tao_db()

@app.route("/", methods=["GET"])
def index():
    """
    Trang chủ giới thiệu tài liệu API (API Documentation).
    Trả về một trang HTML nhỏ giới thiệu cách dùng các endpoint của API này.
    """
    return """
    <html>
        <head>
            <title>Recipe Management Web API</title>
            <meta charset="utf-8">
            <style>
                body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; margin: 40px; background-color: #1e1e2e; color: #e2e8f0; }
                h1 { color: #a580ff; border-bottom: 2px solid #313145; padding-bottom: 10px; }
                h2 { color: #10b981; margin-top: 30px; }
                code { background-color: #2a2a3e; padding: 3px 6px; border-radius: 4px; color: #f43f5e; font-family: 'Consolas', monospace; }
                pre { background-color: #2a2a3e; padding: 15px; border-radius: 6px; overflow-x: auto; border: 1px solid #313145; }
                table { width: 100%; border-collapse: collapse; margin-top: 15px; }
                th, td { padding: 12px; border: 1px solid #313145; text-align: left; }
                th { background-color: #313145; color: #a580ff; }
                tr:nth-child(even) { background-color: #222235; }
                .badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; text-transform: uppercase; }
                .get { background-color: #0d9488; color: white; }
                .post { background-color: #ea580c; color: white; }
                .put { background-color: #2563eb; color: white; }
                .delete { background-color: #dc2626; color: white; }
            </style>
        </head>
        <body>
            <h1>🍳 Hệ Thống Web API Quản Lý Công Thức Nấu Ăn (MVC)</h1>
            <p>Chào mừng bạn! Đây là cổng Web API được tích hợp vào ứng dụng của chúng ta. Bạn có thể sử dụng các đường dẫn (endpoints) dưới đây để tương tác với cơ sở dữ liệu:</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Phương thức</th>
                        <th>Đường dẫn (Endpoint)</th>
                        <th>Chức năng</th>
                        <th>Dữ liệu truyền vào (JSON Body / Param)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><span class="badge get">GET</span></td>
                        <td><code>/api/congthuc</code></td>
                        <td>Lấy danh sách tất cả các công thức món ăn</td>
                        <td>Không có</td>
                    </tr>
                    <tr>
                        <td><span class="badge get">GET</span></td>
                        <td><code>/api/congthuc/detail/&lt;ten_mon&gt;</code></td>
                        <td>Xem chi tiết 1 món ăn cụ thể theo tên</td>
                        <td>Tên món ăn truyền trên URL</td>
                    </tr>
                    <tr>
                        <td><span class="badge get">GET</span></td>
                        <td><code>/api/thongke</code></td>
                        <td>Lấy các số liệu thống kê (phép toán numpy/pandas)</td>
                        <td>Không có</td>
                    </tr>
                    <tr>
                        <td><span class="badge post">POST</span></td>
                        <td><code>/api/congthuc</code></td>
                        <td>Thêm một món ăn mới</td>
                        <td>JSON Body chứa thông tin món ăn</td>
                    </tr>
                    <tr>
                        <td><span class="badge put">PUT</span></td>
                        <td><code>/api/congthuc/&lt;ten_mon&gt;</code></td>
                        <td>Cập nhật/Sửa thông tin món ăn</td>
                        <td>JSON Body chứa thông tin mới</td>
                    </tr>
                    <tr>
                        <td><span class="badge delete">DELETE</span></td>
                        <td><code>/api/congthuc/&lt;ten_mon&gt;</code></td>
                        <td>Xóa món ăn theo tên</td>
                        <td>Không có</td>
                    </tr>
                </tbody>
            </table>

            <h2>Ví dụ cấu trúc JSON cho Món ăn (POST / PUT):</h2>
            <pre>{
    "ten_mon": "Phở Bò Hà Nội",
    "loai_mon": "Món chính",
    "nguyen_lieu": "Bánh phở | Thịt bò | Xương ống | Hành tây | Thảo quả | Quế | Hồi",
    "dinh_luong": "500g | 300g | 1kg | 1 củ | 2 quả | 1 thanh | 3 bông",
    "thoi_gian": 180,
    "cach_lam": "1. Ninh xương ống cùng thảo quả, quế, hồi và hành tây nướng trong 3 tiếng.\\n2. Chần bánh phở, xếp thịt bò thái mỏng lên.\\n3. Chan nước dùng nóng hổi và rắc hành lá.",
    "hinh_anh": "assets/pho_bo.jpg",
    "luu_y": "Nên hớt bọt thường xuyên khi ninh xương để nước dùng được trong."
}</pre>
        </body>
    </html>
    """

# =========================================================================
# API 1: LẤY DANH SÁCH TẤT CẢ CÔNG THỨC (GET /api/congthuc)
# =========================================================================
@app.route("/api/congthuc", methods=["GET"])
def api_lay_danh_sach():
    logger.info("Yêu cầu API: Lấy danh sách công thức.")
    # Gọi Model lấy danh sách từ SQLite dưới dạng DataFrame
    df, ok = model.lay_danh_sach()
    if not ok:
        return jsonify({"error": "Không thể truy vấn cơ sở dữ liệu"}), 500
    
    # Chuyển đổi DataFrame thành cấu trúc danh sách từ điển (List of Dicts)
    # orient="records" giúp tạo ra mảng JSON: [{"cột1": "giá trị 1", "cột2": "giá trị 2"}, ...]
    recipes = df.to_dict(orient="records")
    return jsonify(recipes), 200


# =========================================================================
# API 2: XEM CHI TIẾT MỘT MÓN ĂN THEO TÊN (GET /api/congthuc/detail/<ten_mon>)
# =========================================================================
@app.route("/api/congthuc/detail/<ten_mon>", methods=["GET"])
def api_lay_chi_tiet(ten_mon):
    logger.info(f"Yêu cầu API: Xem chi tiết món '{ten_mon}'.")
    # Gọi Model truy vấn chi tiết món ăn
    detail, ok = model.lay_chi_tiet(ten_mon)
    if not ok or detail is None:
        return jsonify({"error": f"Không tìm thấy món ăn có tên '{ten_mon}'"}), 404
    
    return jsonify(detail), 200


# =========================================================================
# API 3: LẤY THÔNG TIN THỐNG KÊ (GET /api/thongke)
# =========================================================================
@app.route("/api/thongke", methods=["GET"])
def api_thongke():
    logger.info("Yêu cầu API: Tính toán thống kê dữ liệu.")
    df, ok = model.lay_danh_sach()
    if not ok:
        return jsonify({"error": "Không thể tải dữ liệu để thống kê"}), 500
    
    # Gọi Model thực hiện tính toán thống kê bằng NumPy và Pandas
    stats = model.thong_ke(df)
    
    # Khắc phục lỗi: NumPy/Pandas trả về kiểu dữ liệu numpy.int64 hoặc numpy.float64
    # vốn không thể trực tiếp chuyển đổi sang định dạng JSON bởi thư viện Flask jsonify.
    # Ta cần chuyển các phần tử trong thống kê sang kiểu int/float chuẩn của Python:
    if "top_nguyen_lieu" in stats:
        stats["top_nguyen_lieu"] = {k: int(v) for k, v in stats["top_nguyen_lieu"].items()}
    if "tg_theo_loai" in stats:
        stats["tg_theo_loai"] = {k: float(v) for k, v in stats["tg_theo_loai"].items()}
        
    return jsonify(stats), 200



# =========================================================================
# API 4: THÊM MÓN ĂN MỚI (POST /api/congthuc)
# =========================================================================
@app.route("/api/congthuc", methods=["POST"])
def api_them_cong_thuc():
    logger.info("Yêu cầu API: Thêm công thức mới.")
    # Lấy dữ liệu JSON gửi kèm trong thân request (Request Body)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dữ liệu JSON đầu vào không hợp lệ hoặc bị trống!"}), 400
    
    # Bước 1: Gọi Model lấy danh sách hiện tại
    df, ok = model.lay_danh_sach()
    if not ok:
        return jsonify({"error": "Lỗi kết nối cơ sở dữ liệu!"}), 500

    # Bước 2: Gọi Model thêm công thức mới vào SQLite
    new_df, is_added, msg = model.them_cong_thuc(df, data)
    
    if is_added:
        return jsonify({"message": msg}), 201  # 201 Created
    else:
        return jsonify({"error": msg}), 400    # 400 Bad Request


# =========================================================================
# API 5: SỬA MÓN ĂN (PUT /api/congthuc/<ten_mon>)
# =========================================================================
@app.route("/api/congthuc/<ten_mon>", methods=["PUT"])
def api_sua_cong_thuc(ten_mon):
    logger.info(f"Yêu cầu API: Sửa công thức '{ten_mon}'.")
    # Lấy dữ liệu JSON cập nhật mới từ client
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dữ liệu JSON đầu vào không hợp lệ!"}), 400

    df, ok = model.lay_danh_sach()
    if not ok:
        return jsonify({"error": "Lỗi kết nối cơ sở dữ liệu!"}), 500

    # Gọi Model cập nhật công thức trong DB SQLite
    new_df, is_updated, msg = model.sua_cong_thuc(df, ten_mon, data)
    
    if is_updated:
        return jsonify({"message": msg}), 200  # 200 OK
    else:
        return jsonify({"error": msg}), 400


# =========================================================================
# API 6: XÓA MỘT MÓN ĂN (DELETE /api/congthuc/<ten_mon>)
# =========================================================================
@app.route("/api/congthuc/<ten_mon>", methods=["DELETE"])
def api_xoa_cong_thuc(ten_mon):
    logger.info(f"Yêu cầu API: Xóa công thức '{ten_mon}'.")
    df, ok = model.lay_danh_sach()
    if not ok:
        return jsonify({"error": "Lỗi kết nối cơ sở dữ liệu!"}), 500

    # Gọi Model thực thi xóa phần tử (xoa_cong_thuc yêu cầu tham số thứ hai dạng danh sách list)
    new_df, is_deleted, msg = model.xoa_cong_thuc(df, [ten_mon])
    
    if is_deleted:
        return jsonify({"message": msg}), 200
    else:
        return jsonify({"error": msg}), 400


def chay_api(host="127.0.0.1", port=5000, debug=True):
    """Hàm khởi chạy máy chủ API Flask."""
    logger.info(f"Khởi chạy Flask Web API tại http://{host}:{port}/")
    # debug=True giúp Flask tự động tải lại code khi bạn thay đổi nội dung file
    app.run(host=host, port=port, debug=debug)
