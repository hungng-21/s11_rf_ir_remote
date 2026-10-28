# 🎛️ S11 RF/IR Remote Manager (v3.0.1)
**Home Assistant Custom Component** quản lý trung tâm điều khiển Tuya Hub (S11, S11+, S06, S09...) qua mạng nội bộ LAN.

![Version](https://img.shields.io/badge/version-3.0.1-blue.svg)
![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)
![Local](https://img.shields.io/badge/execution-Local_LAN-success.svg)

## 🌟 Giới thiệu
Tích hợp này cung cấp một giao diện (UI) trực quan 100% trên Home Assistant để **Học lệnh, Quản lý thư viện, Phát thử và Tích hợp thực thể** cho các Hub hồng ngoại/vô tuyến (IR/RF) của hệ sinh thái Tuya (chạy qua `tuya_local`). 

Giải quyết triệt để các vấn đề nhức nhối của thiết bị Hub Tuya trên Home Assistant, đặc biệt là lỗi "ngủ gật" chip RF và lỗi map ngược dải tần số 433MHz/315MHz của cộng đồng.

## ✨ Tính năng nổi bật
* 🎯 **Giao diện Menu UI Trực quan:** Không cần cấu hình YAML phức tạp. Mọi thao tác Học/Xóa/Phát thử đều nằm gọn trong nút **Configure (Bánh răng ⚙️)**.
* ⚡ **Tự động mồi tần số ngầm (Auto-Wake RF):** Tự động gửi xung `toggle` để đánh thức chip RF của Hub S11+ và ép nhận đúng tần số thật (vượt qua lỗi map ngược Data Point 315/433MHz của `tuya_local`).
* 📚 **Thư Viện Local (Local Library):** Tự động lưu mã đã học vào `/config/.storage/s11_rf_remote_library.json`. Code được bảo toàn an toàn dù cập nhật hay cài lại tích hợp.
* 🤫 **Tối ưu tiếng Bíp (Single-Beep Optimization):** Mặc định truyền `num_repeats: 1` để quạt trần không bị kêu "tít tít" chói tai mỗi lần đổi số.
* 🌀 **Tích hợp sẵn Thực thể Quạt (Fan Entity):** Tự động tạo entity `fan.*` hỗ trợ trượt 6 cấp độ tốc độ mượt mà.

---

## 🛠️ Yêu cầu hệ thống
1. Đã cài đặt **Home Assistant**.
2. Đã thêm Hub Tuya (S11, S11+, S06, S09...) vào HA thông qua custom component **[tuya_local](https://github.com/make-all/tuya-local)** hoặc giao thức local tương tự.
3. Hub được nhận diện dưới dạng một thực thể `remote.*` (ví dụ: `remote.infrared_rf_remote_control`).

---

## 🚀 Hướng dẫn Cài đặt

### Cách 1: Cài đặt qua HACS (Khuyên dùng)
1. Mở HACS -> **Integrations**.
2. Chọn dấu 3 chấm góc phải trên -> **Custom repositories**.
3. Nhập link GitHub của repo này, chọn category là **Integration**.
4. Bấm Download và Khởi động lại Home Assistant.

### Cách 2: Cài đặt Thủ công
1. Tải code của repo này về.
2. Copy thư mục `s11_rf_remote` vào thư mục `/config/custom_components/` trên Home Assistant của bạn.
3. Khởi động lại Home Assistant.

---

## 🎮 Hướng dẫn Sử dụng

1. Vào **Settings (Cài đặt)** -> **Devices & Services (Thiết bị & Dịch vụ)**.
2. Bấm **Add Integration (Thêm Tích Hợp)** -> Tìm kiếm `S11 RF/IR Remote Manager`.
3. Chọn thực thể `remote.*` tương ứng với Hub của bạn và bấm Submit.
4. Sau khi thêm thành công, bấm vào biểu tượng **Bánh răng ⚙️ (Configure)** để mở **Bảng điều khiển**:
   * **[1] Học lệnh mới:** Hỗ trợ mồi sóng RF tự động. Hướng điều khiển vào Hub và bấm 1-1.5s.
   * **[2] Thư viện lệnh:** Xem danh sách, phát thử hoặc xóa mã rác trực quan.
   * **[3] Phát thử nhanh:** Kích hoạt ngay một lệnh bất kỳ không qua thư viện.
   * **[4] Cài đặt Hub:** Đổi sang Hub điều khiển khác nếu nhà có nhiều thiết bị.

---

## 📝 Ví dụ: Tích hợp Quạt ảo qua Automation (Local 100%)
Nếu bạn dùng `input_number` (tốc độ) và `input_boolean` (bật/tắt) để làm quạt ảo trên Dashboard, bạn có thể gọi action phát lệnh cục bộ như sau:

```yaml
action: s11_rf_remote.send_command
data:
  device: quat_tran_phong_khach
  command: speed_1
  repeats: 1
```

## 🐛 Troubleshooting (Gỡ lỗi nhanh)
* **Học RF không nhận:** Đảm bảo để remote cách Hub 30cm - 1m. Tích hợp đã tự động lật dải tần để bắt đúng sóng, nếu vẫn không được, hãy rút nguồn Hub cắm lại để làm sạch RAM.
* **Mất giao diện/Dòng trắng có dấu `>`:** Nhấn `Ctrl + F5` hoặc xóa cache trình duyệt/app, tích hợp tự tạo file ngôn ngữ khi khởi động.
* **Lỗi Add Entry:** Tích hợp đã xử lý tự động ghi đè entry, nếu muốn đổi Hub, hãy dùng menu Bảng điều khiển -> Cài đặt Hub.

---
**Tác giả:** [@nguyen_viet_hung]
**Bản quyền:** MIT License
