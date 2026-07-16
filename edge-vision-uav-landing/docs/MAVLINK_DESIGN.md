# MAVLink Integration Design

## 1. Mode Lựa Chọn
Sử dụng **SET_POSITION_TARGET_LOCAL_NED** (Offboard mode) cho việc căn chỉnh 3D trực tiếp, thay vì `LANDING_TARGET` (đòi hỏi cấu hình PX4 EKF2 phức tạp hơn).

## 2. Hệ Tọa Độ (Coordinate Frames)
- **Camera/OpenCV:** X phải, Y xuống, Z tới.
- **PX4 Local NED:** X Bắc (North), Y Đông (East), Z Xuống (Down).
- **Mapping:** Lệnh điều khiển velocity (vx, vy, vz) cần ánh xạ từ error_px thông qua PID và biến đổi sang NED frame.

## 3. Tần Số & Giới Hạn (Rate & Limits)
- **Publish Rate:** 30 Hz (Tối thiểu 10 Hz để giữ Offboard mode).
- **Max Velocity (XY):** 1.0 m/s.
- **Max Descent Velocity (Z):** 0.5 m/s.
- **Timeout:** Nếu mất tín hiệu quan sát quá 500ms, set vx=0, vy=0, vz=0.
