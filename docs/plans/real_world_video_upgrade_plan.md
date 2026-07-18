# Real-world Video Upgrade Plan (Revised)

## 1. Architectural Strategy
- Giữ nguyên các video `synthetic_car_tracking.mp4` và `aruco_id0_landing_v1.mp4`. Cập nhật Manifest đổi role thành `deterministic_regression_fixture`.
- Tách dataset thành cấu trúc 4 layer chuẩn: `raw`, `interim`, `processed`, `manifests` bên trong `edge-ai-training/datasets`.
- Tập trung vào **Smoke Subset** (1 sequence) của VisDrone-MOT cho bài toán Tracking (P1-B/P2-A) để đảm bảo toàn bộ đường ống chạy ổn định trước khi scale up.
- Phân biệt rõ Media-level Faults (làm nhiễu video) và Stream/Runtime Faults (delay/drop gói tin lúc replay).

## 2. Dataset Pipeline (P1-B)
1. **Download:** Tải 1 sequence ngắn từ VisDrone-MOT validation set (gồm video và file `txt` nhãn) vào `datasets/raw/visdrone/`.
2. **Parser:** Viết `visdrone_mot_parser.py` chuyển file nhãn sang định dạng CSV nội bộ, giữ lại `target_id`, `class_id`, `occlusion`, `truncation`.
3. **Target Selection:** Viết `select_tracking_target.py` để dựa vào policy (ví dụ: class = car, gần tâm nhất ở frame đầu) để chọn đúng target và bám theo `target_id` đó trong suốt bài test.

## 3. Lỗi và đánh giá
- Bơm **Media Faults** (Gaussian Blur, Noise, Tối) vào video thật này.
- Tạo **Runtime Faults** (Drop frame, IPC delay) lúc play lại bằng Python adapter.
- So sánh hiệu suất Tracking (Precision, Recall, Lock Rate, Switch Count) giữa Clean và Corrupted.

## 4. Báo cáo
Tổng hợp kết quả vào `docs/reviews/real_world_dataset_upgrade_validation.md`.
