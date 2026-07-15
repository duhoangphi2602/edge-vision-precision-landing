# Nguồn Dữ Liệu (Dataset Sources)

Tài liệu này lưu trữ thông tin về các nguồn dữ liệu được sử dụng trong dự án Edge Vision Precision Landing.

## 1. VisDrone2019 (UAV Domain Baseline)
- **Tên:** VisDrone2019-DET
- **Nguồn:** [VisDrone Dataset](http://aiskyeye.com/) (thường được tải thông qua Ultralytics `VisDrone.yaml`).
- **License:** Dành cho mục đích nghiên cứu (Non-commercial, Academic use).
- **Mission Target:** Cung cấp dữ liệu nhận diện vật thể từ góc nhìn từ trên không (Aerial/UAV perspective), giúp mô hình làm quen với các đặc trưng của vật thể nhìn từ drone (nhỏ, bị che khuất, mật độ cao).
- **Classes (10 classes):** `pedestrian`, `people`, `bicycle`, `car`, `van`, `truck`, `tricycle`, `awning-tricycle`, `bus`, `motor`.
- **Lưu ý trong dự án này:** Với mục tiêu Precision Landing / Target Tracking, chúng ta chủ yếu quan tâm đến các class phương tiện di chuyển trên mặt đất (như `car`, `truck`, `van`, `bus`). Các class khác (như `pedestrian`) có thể được dùng làm nhiễu hoặc bỏ qua trong quá trình tính toán loss tùy vào chiến lược fine-tuning sau này.
