# Interface & Mission Contracts (v1.1)

## 1. Perception Observation Schema (UDP)
**Protocol:** UDP
**Format:** JSON (string payload UTF-8)
**Frequency:** Phụ thuộc vào FPS của camera (thường là 30Hz).

Ví dụ một gói payload chuẩn được gửi từ Perception (Python) sang Control (C++):
```json
{
  "schema_version": "1.1",
  "mission_id": "P1_A_FIXED_ARUCO_LANDING",
  "timestamp_capture_ns": 1690000000000,
  "timestamp_publish_ns": 1690000005000,
  "sequence_id": 100,
  "frame_id": 100,
  "source_type": "gazebo",
  "target_found": true,
  "marker_dictionary": "DICT_4X4_50",
  "marker_id": 0,
  "center_px": {"x": 320.0, "y": 240.0},
  "error_px": {"x": 10.5, "y": -5.0},
  "normalized_error": {"x": 0.03, "y": -0.02},
  "pose_valid": true,
  "translation_camera_m": {"x": 0.1, "y": 0.0, "z": 2.5},
  "rotation_rvec": [0.01, 0.02, -0.01],
  "detection_latency_ms": 12.5,
  "tracker_id": 111,
  "bbox": [100, 100, 150, 150]
}
```

## 2. Coordinate Transforms (Hệ trục tọa độ)
Hệ thống kết nối 3 không gian tọa độ khác nhau, yêu cầu chuyển đổi chính xác:
- **Camera Frame (OpenCV):** X hướng sang phải, Y hướng xuống dưới màn hình, Z hướng về phía trước (độ sâu).
- **Drone Body Frame (FRD):** X hướng về trước (Forward), Y hướng sang phải (Right), Z hướng xuống đất (Down).
- **World Frame (NED):** North (Bắc), East (Đông), Down (Xuống).
- **Contract Rule:** Perception node PHẢI gửi dữ liệu `normalized_error` (tọa độ lệch trong khoảng -1.0 đến 1.0) để Control Node tự scale theo trường nhìn (FOV), HOẶC gửi trực tiếp `translation_camera_m`. Control Node chịu trách nhiệm xoay trục từ Camera Frame sang FRD Body Frame trước khi bơm vào bộ điều khiển PID.

## 3. IPC Control Rules & Robustness (Quy tắc chịu lỗi)
Control Node (C++) phải tuân thủ các quy định an toàn sau:
1. **Malformed Packets:** Phải catch exception khi parse JSON. Nếu chuỗi JSON hỏng, drop gói tin và bỏ qua.
2. **Stale Packets (Dữ liệu ôi thiu):** Phải so sánh `timestamp_capture_ns` với thời gian hiện tại của hệ thống. Nếu độ chênh lệch (Delay) > 200ms, lập tức drop gói tin vì dữ liệu này không còn phản ánh đúng vị trí thực tế của drone.
3. **Out-of-order Packets (Đảo thứ tự):** Qua mạng UDP, gói tin số 101 có thể đến trước gói số 100. Control Node phải lưu `last_processed_sequence`. Nếu nhận được gói có `sequence_id` nhỏ hơn `last_processed_sequence`, phải drop ngay lập tức.

## 4. Mission Boundaries (Giới hạn giải pháp)
Để tránh "Over-engineering" (làm phức tạp hóa vấn đề), các dự án bị khóa giới hạn:
- **P1-A (ArUco Landing):** Chỉ cam kết nhận diện và hạ cánh trên 1 marker duy nhất (mặc định ID 0). KHÔNG hỗ trợ hạ cánh bầy đàn hoặc Multi-Marker.
- **P1-B (Vehicle Tracking):** Chỉ cam kết bám theo 1 xe ô tô/tải ở một thời điểm. Tracker sẽ cố gắng bám ID cũ nếu bị che khuất (occlusion) ngắn hạn (dưới 3 giây). Nếu che khuất toàn phần quá 3 giây, cam kết sẽ thả mục tiêu (Abort).
- **P2-A (Video Stabilization):** Hệ thống chỉ chạy off-board (phân tích video sau khi bay) để đánh giá. KHÔNG thiết kế để chạy chống rung real-time nhúng trên bo mạch drone.
