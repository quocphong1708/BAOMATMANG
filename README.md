# 🔒 Hệ Thống ShopGuard v3 - Bảo Vệ Tài Khoản TMĐT Toàn Diện
> **Đồ án cuối kỳ môn Thương mại điện tử (TMĐT)**
> **Đề tài:** Thiết kế hệ thống an toàn dựa trên Xác thực ngữ cảnh & Kiểm tra tính toàn vẹn dữ liệu.

---

## 💡 Ý TƯỞNG BÀI TOÁN & TÀI SẢN BẢO VỆ (Dành cho Slide 1 & 2)

*   **Bối cảnh:** Hiện nay, người dùng có thói quen đặt mật khẩu giống nhau cho nhiều website. Khi một trang web nhỏ bị hack, hacker sẽ lấy danh sách tài khoản/mật khẩu đó để dò quét tự động (tấn công *Credential Stuffing*) vào các trang TMĐT lớn nhằm chiếm đoạt tài sản.
*   **Tuyên bố cốt lõi (Tư duy Zero Trust):** Hệ thống **không mặc định tin tưởng** thông tin gửi lên chỉ vì nó có mật khẩu đúng 100%. 
*   **Tài sản cần bảo vệ:** Ví tiền điện tử của khách hàng, liên kết thẻ ngân hàng, điểm thưởng tích lũy và voucher giảm giá giá trị cao.

---

## 🛠️ 3 QUYẾT ĐỊNH THIẾT KẾ CỐT LÕI (Trọng tâm ghi điểm của Slide)

### 1. Xác thực dựa trên ngữ cảnh thiết bị (Device Context Authentication)
*   **Giải pháp:** Hệ thống bắt buộc trích xuất mã định danh thiết bị (`device_id`) kèm theo gói tin đăng nhập từ Client.
*   **Logic xử lý:** Đối chiếu `device_id` với mảng thiết bị tin cậy (`trusted_devices`) của tài khoản trong CSDL. Nếu khớp, cho phép vào thẳng. Nếu là thiết bị lạ, lập tức kích hoạt trạng thái **"Thử thách" (Challenge Required)** và chặn truy cập tạm thời để bắt xác minh mã OTP gửi qua kênh độc lập (SMS/Email chính chủ).

### 2. Bảo vệ toàn vẹn dữ liệu đầu vào chống giả mạo API (Integrity Check)
*   **Giải pháp:** Sử dụng cơ chế Chữ ký số nội bộ (Signature Verification) bằng thuật toán mã hóa băm chuỗi.
*   **Logic phản ứng:** Khi hacker dùng các công cụ can thiệp mạng (như Burp Suite) để lén sửa đổi thông tin thiết bị ở giữa đường truyền mạng nhằm đánh lừa hệ thống, Backend sẽ đối chiếu Signature của Client và chuỗi nhận được. Nếu phát hiện sai lệch dù chỉ 1 ký tự, hệ thống lập tức **hủy toàn bộ yêu cầu** và phát cảnh báo đỏ, không cho phép đi tiếp vào bước nhập OTP.

### 3. Nhật ký minh bạch & Giám sát thời gian thực (Real-time Audit Logs)
*   **Giải pháp:** Xây dựng màn hình giám sát độc lập (Security Console Logs) phía Backend chạy song song với giao diện người dùng.
*   **Vai trò:** Ghi vết vĩnh viễn tất cả hành vi đăng nhập kèm trạng thái chi tiết (*Thành công / Bị chặn do thiết bị lạ / Bị hủy do gói tin bị can thiệp*). Giúp quản trị viên hệ thống phát hiện sớm các cuộc tấn công dò quét trên diện rộng.

---

## 📊 KỊCH BẢN DEMO GIỮA/CUỐI KỲ (Dành cho Slide Demo)

Hệ thống đã được lập trình sẵn dữ liệu thử nghiệm (Tài khoản: `sinhvienA` / Mật khẩu: `password123`). Thực hiện Demo theo 3 kịch bản:

1.  **Luồng bình thường:** Nhập thiết bị `iPhone_15` + Trạng thái bình thường → Đăng nhập thành công ngay lập tức.
2.  **Luồng rủi ro (Thiết bị lạ):** Nhập thiết bị `Hacker_Laptop` + Trạng thái bình thường → Hệ thống chặn lại, đòi mã OTP. Nhập mã OTP demo `123456` → Đăng nhập thành công và cập nhật thiết bị này vào danh sách an toàn.
3.  **Luồng tấn công (Giả mạo dữ liệu):** Nhập thiết bị `iPhone_15` + Chọn tùy chọn **"Giả mạo gói tin..."** → Hệ thống phát hiện chữ ký sai lệch, từ chối xử lý và hiển thị log cảnh báo mã độc tấn công ở màn hình đen bên phải.

---

## 🚀 HƯỚNG DẪN CHẠY CODE TRÊN MÁY (Dành cho thành viên trong nhóm)

### Bước 1: Cài đặt môi trường
Mở Terminal máy tính của bạn lên (Command Prompt hoặc PowerShell) và chạy lệnh cài đặt thư viện cần thiết:
```bash
pip install Flask
```

### Bước 2: Khởi động Server
Tìm đến thư mục chứa file `app.py` của bạn, mở Terminal tại thư mục đó và gõ lệnh:
```bash
python app.py
```
*(Nếu máy báo lỗi lệnh python, hãy thử thay bằng: `python3 app.py` hoặc `py app.py`)*

### Bước 3: Xem kết quả trên giao diện Web
Sau khi chạy lệnh ở Bước 2 thành công, mở trình duyệt Web (Chrome, Edge) và truy cập địa chỉ sau để bắt đầu Demo:
```text
http://127.0.0
```

---
## ⚖️ PHÂN TÍCH ĐÁNH ĐỔI THIẾT KẾ (Trade-off)
*   **An toàn vs Tiện lợi:** Người dùng thật sẽ mất thêm một bước nhập OTP ở lần đầu tiên khi họ nâng cấp hoặc đổi sang điện thoại mới. 
*   **Giá trị lâu dài:** Chấp nhận một chút bất tiện nhỏ này giúp bảo vệ tuyệt đối số dư tài chính của khách hàng, nâng cao uy tín bảo mật cho nền tảng TMĐT và giảm thiểu 99% các vụ khiếu nại mất tiền do lộ thông tin tài khoản.
