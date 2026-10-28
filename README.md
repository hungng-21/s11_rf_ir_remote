# Tapo Camera Local AI — Ultimate Edition (v2.0.0)

[](https://github.com/hacs/integration)
[GitHub Release](https://www.google.com/search?q=https://github.com/hungng-21/Tapo_camera_local_ai/releases)
[](https://www.home-assistant.io/)
[](https://www.home-assistant.io/)
[License](https://www.google.com/search?q=LICENSE)

[Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://www.google.com/search?q=https://my.home-assistant.io/redirect/hacs_repository/%3Fowner%3Dhungng-21%26repository%3DTapo_camera_local_ai%26category%3Dintegration)

**Tapo Camera Local AI** là giải pháp Custom Component toàn diện và tối ưu nhất để kết nối, điều khiển và khai thác toàn bộ sức mạnh AI của camera **TP-Link Tapo** trên **Home Assistant**. 

Tích hợp hoạt động **100% nội bộ (Local LAN)** không thông qua máy chủ đám mây (Cloud), không tốn phí thuê bao (No Subscription), đảm bảo tốc độ phản hồi tính bằng mili-giây và bảo mật dữ liệu riêng tư tuyệt đối.

---

## 🌟 Điểm nổi bật của phiên bản v2.0.0 (Ultimate Edition)

* **Hợp nhất Nhận diện Khuôn mặt (Face Recognition) & Bảng điều khiển "Tapo Face Manager"**: Tích hợp toàn bộ hệ thống quản lý khuôn mặt thông minh từ dự án `tapo-c260-face` (của `@quangtienhn`), gom vào **duy nhất 1 phiên kết nối Local** giúp loại bỏ 100% lỗi xung đột phiên (Session Fighting / Rate-limit -40404).
* **Tự nhận diện phần cứng thông minh (Hardware Auto-Detection)**:
  * Camera có xoay quét (PTZ) $\rightarrow$ Tự kích hoạt 4 nút điều hướng, hiệu chuẩn, thanh trượt góc xoay, điểm nhớ Preset và chế độ tuần tra. Camera cố định $\rightarrow$ Tự ẩn sạch nút xoay.
  * Camera có Face AI (như **Tapo C260**) $\rightarrow$ Tự kích hoạt cảm biến khuôn mặt, lịch sử xuất hiện và bảng điều khiển Sidebar. Camera thường (C100, C110, C120, C125, C200, C210, C310, C500...) $\rightarrow$ **Tự ẩn toàn bộ entity khuôn mặt thừa** và tự dọn dẹp Entity Registry.
* **Tách biệt chuẩn hóa Độ nhạy AI (AI Sensitivity Separation)**:
  * **4 thanh trượt 10 mức (`number`)**: Dành riêng cho các cảm biến hình ảnh 1–10 trong app Tapo (**Motion**, **Person**, **Pet**, **Vehicle**).
  * **5 hộp chọn 3 mức (`select`)**: Dành riêng cho các cảm biến âm thanh chỉ có 3 mức trong app Tapo (**Baby Cry**, **Dog Bark**, **Cat Meow**, **Glass Break**, **Tamper** với 3 giá trị: `low`, `normal`, `high`).
* **Hỗ trợ đầy đủ còi báo động (`siren`) & điều khiển âm thanh 2 chiều**: Bật/tắt còi kèm độ dài thời gian hú (`duration`) và âm lượng (`volume_level`), thanh trượt âm lượng Loa/Micro (0–100%), công tắc ngắt Micro phần cứng.
* **Chống nghẽn & Độc lập đa luồng**: Luồng RTSP Video (cổng 554) và ONVIF (cổng 2020) chạy độc lập; các truy vấn công tắc và độ nhạy được gộp thành 1 request duy nhất (`multipleRequest`), phản hồi cực nhanh ~50ms.

---

## 📸 Giao diện Bảng điều khiển "Tapo Face Manager" (Sidebar)

Khi hệ thống có camera hỗ trợ nhận diện khuôn mặt (**Tapo C260**), Home Assistant sẽ tự động xuất hiện mục **Tapo Face Manager** trên thanh bên (Sidebar):

* **Tab Người quen (Known)**: Danh sách người nhà đã nhận diện, hỗ trợ đổi tên, cập nhật mã Face ID và tự động chuyển tiếp lịch sử cũ sang ID mới.
* **Tab Người lạ (Unknown)**: Bắt trọn mọi khuôn mặt lạ mà camera phát hiện, hiển thị số lần xuất hiện, lần đầu và lần cuối nhìn thấy. Hỗ trợ bấm **"+ Thêm người"** để đặt tên tức thì chỉ với 1 cú click.
* **Tab Lịch sử ngày (Day History)**: Biểu đồ thời gian thực (24 giờ) trực quan từng phút từng giây ai đã xuất hiện trước camera.
* **Tab Thống kê (Statistics)**: Biểu đồ cột tổng hợp tần suất người quen / người lạ theo 7 ngày, 30 ngày, 90 ngày và phân tích ngày cao điểm.
* **Tab Cài đặt & Thẻ Sức khỏe kết nối (Health Diagnostics)**: Đo thời gian phản hồi (ms), số lỗi liên tiếp và cho phép tinh chỉnh chu kỳ quét, thời gian chống lặp (Dedup cooldown), thời gian tự tắt cảm biến người lạ trực tiếp trên Web.

> [!NOTE]
> Bảng điều khiển Face Manager hỗ trợ song ngữ **Tiếng Việt / Tiếng Anh**, tự động lưu tùy chọn ngôn ngữ và cho phép chuyển đổi tức thì.

---

## 📦 Danh mục thực thể cung cấp (Entities)

Toàn bộ các thực thể được gom chung vào **1 Thiết bị Camera duy nhất** trên Home Assistant:

### 1. Luồng Video Trực tiếp (`camera`)
* `camera.<ten_cam>_hd_stream`: Luồng chính chất lượng cao (HD / 2K / 4K - RTSP `stream1`).
* `camera.<ten_cam>_sd_stream`: Luồng phụ mượt mà, tốn cực ít tài nguyên CPU (SD - RTSP `stream2`).
* Hỗ trợ gọi dịch vụ xoay quét góc tương đối (`tapo_local_ai.ptz_move`) và xoay tới điểm nhớ (`tapo_local_ai.ptz_goto_preset`).

### 2. Cảm biến nhị phân AI & Sự kiện (`binary_sensor`)
* `Phát hiện tiếng khóc trẻ em` (`baby_cry`)
* `Phát hiện chó sủa` (`bark`)
* `Phát hiện mèo kêu` (`meow`)
* `Phát hiện kính vỡ` (`glass_break`)
* `Phát hiện người (AI Person)` (`person`)
* `Phát hiện thú cưng (AI Pet)` (`pet`)
* `Phát hiện phương tiện (AI Vehicle)` (`vehicle`)
* `Phát hiện chuyển động` (`motion`)
* `Vượt hàng rào ảo` (`line_crossing`)
* `Xâm nhập vùng cấm` (`area_intrusion`)
* `Che khuất / Phá hoại camera` (`tamper`)
* `Phát hiện bưu kiện` (`package`)
* `Nhận diện người quen` (`face_recognized` — chỉ hiện trên C260)
* `Phát hiện người lạ` (`stranger_detected` — chỉ hiện trên C260, tự tắt sau 30s)
* `Trạng thái kết nối Camera` (`connection`)

### 3. Cảm biến thông tin & Chẩn đoán (`sensor`)
* **Nhóm Khuôn mặt (C260)**: `Tên khuôn mặt (Face Name)`, `Mã khuôn mặt (Face ID)`, `Lần nhận diện gần nhất (Last Seen)`, `Số người quen (Known Faces)`, `Số người lạ (Unknown Faces)`, `Số người lạ hôm nay (Unknown Today)`, `Lần gặp người lạ gần nhất (Last Unknown Seen)`, `Số lần bỏ qua lặp khuôn mặt (Dedup Skipped)`.
* **Nhóm Chẩn đoán kết nối**: `Lần quét thành công gần nhất (Last Poll)`, `Thời gian phản hồi Camera (Response Time ms)`, `Số lỗi quét liên tiếp (Polling Errors)`, `Chế độ kết nối (Connection Mode)`.

### 4. Thực thể Sự kiện (`event`)
* `event.<ten_cam>_face_event`: Bắn sự kiện với 2 kiểu `face_recognized` và `face_unknown` để viết Automation trực tiếp trong giao diện UI của Home Assistant.
* Bắn đồng thời 2 sự kiện `tapo_local_ai_face_detected` và `tapo_c260_face_detected` lên Home Assistant Event Bus.

### 5. Còi báo động (`siren`) & Nút bấm (`button`)
* `siren.<ten_cam>_siren`: Còi hú tích hợp (hỗ trợ bật/tắt thủ công kèm `duration` tính bằng giây và `volume_level`).
* `button.<ten_cam>_ptz_move_up / down / left / right`: 4 nút xoay PTZ theo góc bước cài đặt.
* `button.<ten_cam>_ptz_calibrate`: Hiệu chuẩn lại motor xoay quét.
* `button.<ten_cam>_manual_alarm_start / stop`: Nút kích hoạt / dừng còi hú khẩn cấp.
* `button.<ten_cam>_reboot`: Khởi động lại camera từ xa qua mạng nội bộ.

### 6. Công tắc AI & Phần cứng (`switch`)
* 10 công tắc bật/tắt từng tính năng AI Detection riêng biệt.
* `Tự động xoay theo chuyển động` (`auto_track_switch` — chỉ có trên camera PTZ).
* `Chế độ riêng tư (Privacy Mode)` (`privacy_mode_switch` — cụp ống kính / tắt hình).
* `Đèn trạng thái LED` (`led_indicator_switch`).
* `Đảo ngược hình ảnh 180°` (`flip`).
* `Khử cong viền góc rộng` (`lens_distortion`).
* `Ghi hình thẻ nhớ microSD` (`record_to_sd`).
* `Tắt Micro phần cứng` (`microphone_mute`).
* `Tự động hú còi khi phát hiện AI` (`auto_alarm_switch`).

### 7. Thanh trượt số (`number`) & Hộp chọn (`select`)
* **Thanh trượt độ nhạy 10 mức (1–10)**: Độ nhạy chuyển động (`motion_sensitivity`), Người (`person_sensitivity`), Thú cưng (`pet_sensitivity`), Xe cộ (`vehicle_sensitivity`).
* **Hộp chọn độ nhạy 3 mức (`low`/`normal`/`high`)**: Tiếng khóc (`baby_cry_sensitivity`), Chó sủa (`bark_sensitivity`), Mèo kêu (`meow_sensitivity`), Kính vỡ (`glass_break_sensitivity`), Che khuất camera (`tamper_sensitivity`).
* **Điều khiển phần cứng**: Âm lượng Loa (0–100%), Âm lượng Micro (0–100%), Thời lượng hú còi (0–300s), Góc xoay mỗi bước (5°–360°), Chế độ nhìn đêm (`Infrared`/`Full-Color`/`Smart`), Tần số chống chớp đèn (`Auto`/`50Hz`/`60Hz`), Kiểu báo động (`sound`/`light`/`both`), Mức âm lượng còi (`low`/`normal`/`high`), Điểm nhớ Preset và Chế độ tuần tra PTZ.

---

## 🚀 Hướng dẫn Cài đặt

### Cách 1: Cài đặt tự động qua HACS (Khuyên dùng)

1. Mở Home Assistant $\rightarrow$ chọn **HACS** ở thanh bên trái.
2. Nhấp vào dấu **3 chấm** ở góc trên bên phải $\rightarrow$ chọn **Custom repositories (Kho lưu trữ tùy chỉnh)**.
3. Dán đường dẫn sau vào ô Repository:
   ```text
   https://github.com/hungng-21/Tapo_camera_local_ai
   ```
4. Chọn danh mục: **Integration** $\rightarrow$ bấm **Add**.
5. Tìm kiếm `Tapo Camera Local AI` $\rightarrow$ bấm **Download** phiên bản mới nhất (`v2.0.0`).
6. Khởi động lại Home Assistant.

### Cách 2: Cài đặt thủ công (Manual)

1. Tải file `tapo_local_ai.zip` từ trang [Releases](https://www.google.com/search?q=https://github.com/hungng-21/Tapo_camera_local_ai/releases).
2. Giải nén file, sao chép toàn bộ thư mục `tapo_local_ai` vào đường dẫn `/config/custom_components/` của Home Assistant (đường dẫn đầy đủ: `/config/custom_components/tapo_local_ai/`).
3. Khởi động lại Home Assistant.

---

## ⚙️ Cấu hình thêm Camera vào Home Assistant

1. Mở ứng dụng **Tapo** trên điện thoại: vào mục cài đặt camera $\rightarrow$ **Cài đặt nâng cao (Advanced Settings)** $\rightarrow$ **Tài khoản Camera (Camera Account)** $\rightarrow$ Tạo tài khoản cục bộ (Username & Password).
2. Trên Home Assistant: Vào **Cài đặt (Settings)** $\rightarrow$ **Thiết bị & Dịch vụ (Devices & Services)** $\rightarrow$ **Thêm tích hợp (Add Integration)** $\rightarrow$ Tìm kiếm **Tapo Camera Local AI**.
3. Điền các thông số:
   * **Host**: Địa chỉ IP nội bộ của camera (ví dụ `192.168.1.100`, nên đặt IP tĩnh trong router).
   * **Username**: Tên tài khoản Camera Account vừa tạo ở Bước 1.
   * **Password**: Mật khẩu Camera Account vừa tạo ở Bước 1.
   * **Cloud Password (Tùy chọn)**: Mật khẩu tài khoản TP-Link Cloud (cần thiết đối với các dòng firmware mới dùng chuẩn bảo mật KLAP/TPAP và dòng **Tapo C260**).
   * Các cổng mặc định: Điều khiển HTTPS (`443`), ONVIF (`2020`), RTSP (`554`).
4. Bấm **Gửi (Submit)**. Camera sẽ được kết nối ngay lập tức!
5. Nhấn **Ctrl + F5** trên trình duyệt máy tính để nạp bảng điều khiển **Tapo Face Manager** ở thanh bên.

---

## 💡 Ví dụ Automation thông minh mẫu

### 1. Chào đón người nhà khi về đến cửa (Nhận diện khuôn mặt)
```yaml
alias: "Camera C260 - Chào người quen"
trigger:
  - platform: event
    event_type: tapo_local_ai_face_detected
    event_data:
      recognized: true
action:
  - service: tts.speak
    target:
      entity_id: media_player.loa_phong_khach
    data:
      media_player_entity_id: media_player.loa_phong_khach
      message: "Chào mừng {{ trigger.event.data.name }} đã về nhà!"
```

### 2. Báo động ngay lập tức khi phát hiện người lạ
```yaml
alias: "Camera C260 - Cảnh báo Người lạ"
trigger:
  - platform: state
    entity_id: binary_sensor.tapo_c260_stranger_detected
    to: "on"
action:
  - service: notify.mobile_app_dien_thoai
    data:
      title: "⚠️ Cảnh báo an ninh!"
      message: "Phát hiện khuôn mặt người lạ tại camera {{ trigger.to_state.name }}!"
      data:
        image: "/api/camera_proxy/camera.tapo_c260_hd_stream"
```

### 3. Tự động bật đèn khi phát hiện tiếng em bé khóc vào ban đêm
```yaml
alias: "Trông trẻ - Bật đèn khi bé khóc"
trigger:
  - platform: state
    entity_id: binary_sensor.tapo_camera_baby_cry
    to: "on"
condition:
  - condition: time
    after: "21:00:00"
    before: "06:00:00"
action:
  - service: light.turn_on
    target:
      entity_id: light.den_ngu
    data:
      brightness_pct: 20
```

---

## ❓ Câu hỏi thường gặp (FAQ)

&lt;details&gt;
&lt;summary&gt;&lt;b&gt;1. Tôi cập nhật từ v1.x lên v2.0.0 thì camera cũ có bị mất cấu hình không?&lt;/b&gt;&lt;/summary&gt;
Hoàn toàn &lt;b&gt;KHÔNG&lt;/b&gt;. Bản v2.0.0 tương thích ngược 100%. Tất cả Entity ID, tên gọi, các thẻ trên Dashboard và Automation bạn đã tạo từ trước đều được giữ nguyên vẹn.
&lt;/details&gt;

&lt;details&gt;
&lt;summary&gt;&lt;b&gt;2. Camera của tôi không có Face AI (như C125, C200, C210...) thì có bị hiện các thực thể thừa không?&lt;/b&gt;&lt;/summary&gt;
&lt;b&gt;KHÔNG&lt;/b&gt;. Hệ thống tự động nhận diện model phần cứng. Nếu camera không có Face AI, toàn bộ các entity khuôn mặt sẽ tự động được ẩn đi và dọn sạch, bảng Face Manager trên thanh bên cũng chỉ xuất hiện khi bạn có ít nhất một camera C260.
&lt;/details&gt;

&lt;details&gt;
&lt;summary&gt;&lt;b&gt;3. Làm thế nào để camera không bị khóa bảo mật (-40404)?&lt;/b&gt;&lt;/summary&gt;
Bản v2.0.0 đã gộp toàn bộ việc lấy dữ liệu AI và Face ID vào &lt;b&gt;chỉ 1 phiên kết nối duy nhất&lt;/b&gt;, loại bỏ hoàn toàn việc tranh chấp cổng 443. Ngoài ra, cơ chế giãn cách tự động 60s sẽ lập tức kích hoạt nếu camera có dấu hiệu từ chối kết nối, đảm bảo không bao giờ bị khóa tạm thời.
&lt;/details&gt;

---

## 🤝 Đóng góp & Bản quyền

Dự án được phát triển và duy trì bởi [@hungng-21](https://www.google.com/search?q=https://github.com/hungng-21) cùng sự đóng góp giải pháp Nhận diện khuôn mặt từ [@quangtienhn](https://www.google.com/search?q=https://github.com/quangtienhn).

Phát hành theo giấy phép mã nguồn mở **MIT License**.