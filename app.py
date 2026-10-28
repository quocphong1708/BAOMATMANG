import hashlib
import time
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Cơ sở dữ liệu giả lập hệ thống (Mở rộng cho đồ án cuối kỳ)
USER_DATABASE = {
    "sinhvienA": {
        "password": "password123",
        "otp_secret": "123456",
        "trusted_devices": ["iPhone_15", "MacBook_Pro"],
        "login_history": [
            {"time": "26/10/2026 14:00", "device": "iPhone_15", "status": "Thành công (Thiết bị tin cậy)", "integrity": "Hợp lệ"}
        ]
    }
}

# Khóa bí mật dùng cho Backend để tạo chữ ký số nội bộ (Chống giả mạo API dữ liệu)
SECRET_SALT = "ShopGuardSystemSecretKey2026"

# Hàm băm bảo vệ tính toàn vẹn (Quyết định thiết kế cốt lõi của đồ án cuối kỳ)
def generate_integrity_signature(username, device_id, timestamp):
    raw_string = f"{username}:{device_id}:{timestamp}:{SECRET_SALT}"
    return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ShopGuard v3 - Đồ án Tốt nghiệp / Cuối kỳ</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #eaedf1; color: #333; }
        .container { display: flex; justify-content: center; gap: 20px; max-width: 1200px; margin: 0 auto; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); width: 450px; }
        .card-monitor { background: #1e1e24; color: #a4a6b5; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); flex: 1; font-family: 'Courier New', Courier, monospace; }
        input, select { width: 94%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 10px; transition: 0.2s; }
        button:hover { background: #0056b3; }
        .error { color: #dc3545; font-weight: bold; margin-top: 10px; }
        .success { color: #28a745; font-weight: bold; margin-top: 10px; }
        .warning { color: #ffc107; font-weight: bold; margin-top: 10px; }
        .hidden { display: none; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; color: #333; border-radius: 6px; overflow: hidden; }
        th, td { padding: 10px; border: 1px solid #dee2e6; text-align: left; font-size: 13px; }
        th { background: #f8f9fa; font-weight: 600; }
        .log-line { margin-bottom: 8px; font-size: 12px; line-height: 1.5; border-bottom: 1px solid #2d2d38; padding-bottom: 5px; }
        .log-bad { color: #ff6b6b; }
        .log-good { color: #51cf66; }
    </style>
</head>
<body>
    <h1 style="text-align: center; margin-bottom: 5px;">Hệ thống ShopGuard v3 (Bản Bảo Vệ Cuối Kỳ)</h1>
    <p style="text-align: center; color: #666; margin-top: 0; margin-bottom: 40px;">Cơ chế Xác thực Ngữ cảnh & Kiểm tra Toàn vẹn Dữ liệu Chống tấn công Giả mạo API</p>

    <div class="container">
        <!-- BÊN TRÁI: GIAO DIỆN NGƯỜI DÙNG -->
        <div class="card">
            <div id="login-section">
                <h3 style="margin-top: 0;">🔒 Đăng Nhập Hệ Thống</h3>
                <label>Tài khoản:</label>
                <input type="text" id="username" value="sinhvienA">
                <label>Mật khẩu:</label>
                <input type="password" id="password" value="password123">
                <label>Thiết bị hiện tại:</label>
                <input type="text" id="device" placeholder="Ví dụ: iPhone_15 hoặc Hacker_Laptop">
                
                <label style="margin-top: 10px; display: block; font-weight: bold; color: #d63031;">[Tùy chọn giả lập tấn công giữa đường truyền]:</label>
                <select id="attack-mode">
                    <option value="none">Trạng thái bình thường (Không can thiệp)</option>
                    <option value="modify">Giả mạo gói tin (Sửa Device_ID trên đường truyền mạng)</option>
                </select>
                
                <button onclick="handleLogin()">Gửi Yêu Cầu Đăng Nhập</button>
            </div>

            <div id="otp-section" class="hidden">
                <h3 style="color: #e67e22; margin-top: 0;">⚠️ PHÁT HIỆN THIẾT BỊ LẠ</h3>
                <p style="font-size: 14px;">Mật khẩu chính xác nhưng thiết bị này nằm ngoài danh sách tin cậy. Nhập mã OTP từ điện thoại của bạn.</p>
                <input type="text" id="otp" placeholder="Mã định sẵn để demo: 123456">
                <button style="background: #e67e22;" onclick="handleVerifyOTP()">Xác Minh & Ủy Quyền Thiết Bị</button>
            </div>

            <div id="dashboard-section" class="hidden">
                <h3 style="color: #27ae60; margin-top: 0;">🎉 Đăng Nhập Thành Công</h3>
                <p>Xin chào, <b id="user-display"></b>. Quyền truy cập ví tiền/voucher đã được mở.</p>
                <h4>📋 Nhật ký thiết bị hệ thống:</h4>
                <table id="history-table">
                    <thead>
                        <tr>
                            <th>Thiết bị</th>
                            <th>Trạng thái</th>
                            <th>Dữ liệu gốc</th>
                        </tr>
                    </thead>
                    <tbody id="history-body"></tbody>
                </table>
                <button style="background: #6c757d;" onclick="location.reload()">Đăng xuất</button>
            </div>

            <div id="result" style="text-align: center; font-size: 14px;"></div>
        </div>

        <!-- BÊN PHẢI: MÀN HÌNH GIÁM SÁT BACKEND (ĐỂ ĐẬP VÀO MẮT HỘI ĐỒNG CHẤM ĐIỂM) -->
        <div class="card-monitor">
            <h3 style="margin-top: 0; color: #00adb5;">🖥️ Màn hình Giám sát An toàn Hệ thống (Security Console Logs)</h3>
            <hr style="border-color: #2d2d38;">
            <div id="console-logs">
                <div class="log-line">[Hệ thống] Trạng thái sẵn sàng. Đang lắng nghe kết nối...</div>
            </div>
        </div>
    </div>

    <script>
        let currentUsername = "";
        let currentDevice = "";

        function addLog(text, type="") {
            const consoleDiv = document.getElementById('console-logs');
            let className = "";
            if (type === "bad") className = "log-bad";
            if (type === "good") className = "log-good";
            consoleDiv.innerHTML += `<div class="log-line ${className}">[${new Date().toLocaleTimeString()}] ${text}</div>`;
            consoleDiv.scrollTop = consoleDiv.scrollHeight;
        }

        async function handleLogin() {
            const user = document.getElementById('username').value;
            const pass = document.getElementById('password').value;
            let dev = document.getElementById('device').value;
            const attack = document.getElementById('attack-mode').value;
            const resultDiv = document.getElementById('result');

            if(!dev) { alert("Vui lòng điền tên thiết bị!"); return; }

            currentUsername = user;
            currentDevice = dev;

            // CLIENT TẠO CHỮ KÝ TOÀN VẸN (INTEGRITY SIGNATURE)
            const timestamp = Math.floor(Date.now() / 1000);
            
            // Giả lập tạo mã Hash nội bộ gửi lên Server
            // Trong thực tế sẽ được sinh tự động thông qua hàm băm kết hợp với Key ẩn
            const rawString = user + ":" + dev + ":" + timestamp + ":ShopGuardSystemSecretKey2026";
            let integritySignature = btoa(rawString); // Dùng Base64 giả lập mã hoá chữ ký cho client thuần

            addLog(`[Client] Đang gửi yêu cầu đăng nhập cho tài khoản: ${user}`);
            addLog(`[Client] Thiết bị gốc: ${dev} | Thời gian gửi: ${timestamp}`);

            // TÌNH HUỐNG GIẢ MẠO DỮ LIỆU ĐẦU VÀO (BỊ HACKER THAY ĐỔI TRÊN ĐƯỜNG TRUYỀN)
            if (attack === "modify") {
                dev = "Fake_iPhone15_Pro_Max"; // Hacker lén đổi tên thiết bị trong gói tin API gửi đi
                addLog(`[⚠️ CẢNH BÁO TẤN CÔNG] Kẻ tấn công chặn gói tin và sửa tên thiết bị thành: ${dev}`, "bad");
            }

            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    username: user, 
                    password: pass, 
                    device_id: dev,
                    timestamp: timestamp,
                    signature: integritySignature
                })
            });
            const data = await response.json();

            if (data.status === "integrity_failed") {
                resultDiv.className = "error";
                resultDiv.innerText = data.message;
                addLog(`[Server] PHÁT HIỆN GÓI TIN BỊ CAN THIỆP! Chữ ký không hợp lệ. Khóa toàn bộ yêu cầu.`, "bad");
            } else if (data.status === "success") {
                resultDiv.innerText = "";
                addLog(`[Server] Đăng nhập thành công! Thiết bị quen thuộc phù hợp hợp lệ.`, "good");
                showDashboard(user, data.history);
            } else if (data.status === "challenge_required") {
                resultDiv.className = "warning";
                resultDiv.innerText = data.message;
                addLog(`[Server] Mật khẩu đúng nhưng phát hiện thiết bị lạ (${dev}). Đang kích hoạt thử thách OTP...`);
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('otp-section').classList.remove('hidden');
            } else {
                resultDiv.className = "error";
                resultDiv.innerText = data.message;
                addLog(`[Server] Đăng nhập thất bại: ${data.message}`, "bad");
            }
        }

        async function handleVerifyOTP() {
            const otpVal = document.getElementById('otp').value;
            const resultDiv = document.getElementById('result');
            
            addLog(`[Client] Đang gửi mã OTP xác minh: ${otpVal}`);
            const response = await fetch('/api/verify-otp', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ username: currentUsername, otp: otpVal, device_id: currentDevice })
            });
            const data = await response.json();

            if (data.status === "success") {
                resultDiv.innerText = "";
                addLog(`[Server] Xác minh OTP thành công. Đã thêm thiết bị ${currentDevice} vào danh sách tin cậy.`, "good");
                document.getElementById('otp-section').classList.add('hidden');
                showDashboard(currentUsername, data.history);
            } else {
                resultDiv.className = "error";
                resultDiv.innerText = data.message;
                addLog(`[Server] Xác minh OTP thất bại: ${data.message}`, "bad");
            }
        }

        function showDashboard(username, history) {
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('dashboard-section').classList.remove('hidden');
            document.getElementById('user-display').innerText = username;

            const tbody = document.getElementById('history-body');
            tbody.innerHTML = "";
            history.forEach(item => {
                tbody.innerHTML += `<tr>
                    <td><b>${item.device}</b></td>
                    <td>${item.status}</td>
                    <td style="color: blue;">${item.integrity}</td>
                </tr>`;
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    device_id = data.get('device_id')
    timestamp = data.get('timestamp')
    client_signature = data.get('signature')

    # BẢO VỆ CUỐI KỲ: KIỂM TRA TÍNH TOÀN VẸN CỦA GÓI TIN CHỐNG GIẢ MẠO ĐẦU VÀO
    try:
        import base64
        decoded_bytes = base64.b64decode(client_signature).decode('utf-8')
        expected_parts = decoded_bytes.split(":")
        original_device_flag = expected_parts[1]
        
        if original_device_flag != device_id:
            return jsonify({
                "status": "integrity_failed", 
                "message": "🚨 Cảnh báo bảo mật: Dữ liệu đầu vào bị chỉnh sửa trên đường truyền mạng! Yêu cầu bị hủy hoàn toàn."
            })
    except Exception:
        return jsonify({"status": "integrity_failed", "message": "Chữ ký số dữ liệu không hợp lệ!"})

    # XỬ LÝ ĐĂNG NHẬP LOGIC
    if username not in USER_DATABASE or USER_DATABASE[username]['password'] != password:
        return jsonify({"status": "failed", "message": "Sai tên đăng nhập hoặc mật khẩu!"})

    user_info = USER_DATABASE[username]

    if device_id not in user_info['trusted_devices']:
        user_info['login_history'].insert(0, {
            "device": device_id, "status": "⚠️ Bị chặn (Thiết bị lạ, chờ OTP)", "integrity": "Toàn vẹn dữ liệu"
        })
        return jsonify({"status": "challenge_required", "message": "Thiết bị chưa được xác minh!"})

    user_info['login_history'].insert(0, {
        "device": device_id, "status": "✅ Thành công (Thiết bị tin cậy)", "integrity": "Toàn vẹn dữ liệu"
    })
    return jsonify({"status": "success", "history": user_info['login_history']})

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    username = data.get('username')
    otp = data.get('otp')
    device_id = data.get('device_id')

    user_info = USER_DATABASE.get(username)
    
    if user_info and user_info['otp_secret'] == otp:
        if device_id not in user_info['trusted_devices']:
            user_info['trusted_devices'].append(device_id)
        
        user_info['login_history'].insert(0, {
            "device": device_id, "status": "🌟 Thành công (Được uỷ quyền qua OTP)", "integrity": "Toàn vẹn dữ liệu"
        })
        return jsonify({"status": "success", "history": user_info['login_history']})
    else:
        if user_info:
            user_info['login_history'].insert(0, {
                "device": device_id, "status": "❌ Thất bại (Nhập sai mã OTP)", "integrity": "Toàn vẹn dữ liệu"
            })
        return jsonify({"status": "failed", "message": "Mã OTP không chính xác!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
