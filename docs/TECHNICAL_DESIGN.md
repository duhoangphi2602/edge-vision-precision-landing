# Technical Design Document (v1.0)

## 1. System Architecture (Kiến trúc hệ thống)
Dự án được thiết kế theo kiến trúc phân tán đa tiến trình (Distributed Process Architecture), chia làm 2 node chính:
- **Perception Node (Python/ONNX):** Chịu trách nhiệm đọc camera/video, chạy YOLO (cho P1-B) hoặc ArUco (cho P1-A), tính toán độ lệch (pixel error) và đóng gói thành JSON.
- **Control Node (C++):** Nhận JSON qua giao thức mạng UDP, giải mã (parse), chạy bộ điều khiển (PID/LQR), và gửi lệnh Setpoint (vận tốc/tọa độ) tới PX4 qua MAVSDK.

**Tại sao lại là UDP?** 
Trong điều khiển bay, độ trễ (latency) quan trọng hơn việc mất 1-2 khung hình. Dùng TCP sẽ gây ra hiện tượng "chờ gửi lại" (retransmit) làm tăng đột biến độ trễ, gây nguy hiểm cho drone. UDP cho phép bỏ qua packet rớt và luôn lấy dữ liệu mới nhất.

## 2. Workspace-Level Portfolio Demo Orchestration
Hệ thống sẽ có một lớp Menu/CLI/WebUI (Orchestrator) để dễ dàng demo. **Tuy nhiên, giới hạn kỹ thuật được thiết lập nghiêm ngặt như sau:**
- Các dự án (P1-A, P1-B, P2-A) phải chạy hoàn toàn độc lập ở mức mã nguồn và runtime. Không chia sẻ state bộ nhớ.
- Direct command (gọi file python/cpp trực tiếp từ terminal) vẫn là "source of truth" duy nhất.
- Orchestrator KHÔNG can thiệp vào flight-control runtime hay logic xử lý ảnh. Nó chỉ có quyền start/stop process con và đọc log/report.

## 3. Evidence & Simulation Modes (Các chế độ mô phỏng)
Hệ thống sử dụng 3 cấp độ bằng chứng để xác thực:
1. **Offline Replay Evidence:** Chạy Perception Node bằng một file video MP4 tĩnh. 
   - *Mục đích:* Đo lường chính xác FPS, End-to-End Latency, và CPU/Memory Usage. Không có feedback loop.
2. **Hybrid SITL Evidence:** Perception phân tích video tĩnh, gửi tọa độ ảo qua UDP. Control Node nhận UDP và xuất lệnh điều khiển ảo ra log (không truyền tới PX4 Gazebo). 
   - *Mục đích:* Test khả năng chống chịu của C++ Node (Stale Rejection, Malformed Packets, Jitter).
3. **Full SITL Evidence:** Chạy môi trường 3D Gazebo, PX4 SITL. Camera Gazebo sinh ảnh theo thời gian thực -> Perception -> UDP -> Control -> MAVLink -> PX4. 
   - *Mục đích:* Đánh giá bán kính hạ cánh (Landing error radius) và động lực học (Dynamics).

## 4. State Machine & Fallback Modes
**Target Selector State Machine (Dành cho P1-B - Tracking):**
- `SEARCHING`: Quét toàn màn hình, chọn bounding box có confidence cao nhất hoặc ở gần trung tâm khung hình nhất.
- `LOCKED`: Đã gán Tracking ID. Tracker liên tục bám theo ID này. Bỏ qua các xe khác.
- `LOST`: Mất dấu ID đang bám (do bị che khuất). Chuyển sang RECOVERY.
- `RECOVERY`: Mở rộng vùng tìm kiếm quanh vị trí cuối cùng trong X giây. Nếu tìm thấy, quay lại LOCKED.
- `ABORT`: Mất dấu quá lâu (vượt quá timeout). Ra lệnh cho drone Hover (Đứng yên) hoặc RTL (Return-to-Launch).

**Control Node Failsafe (Dành cho P1-A - Landing):**
- Nếu UDP packet bị delay hoặc là dữ liệu cũ (Stale) quá 200ms -> Từ chối (Reject), drone tiếp tục giữ lệnh điều khiển trước đó (Hold/Hover).
- Nếu mất kết nối hoàn toàn (Không nhận được UDP trong 2s) -> C++ Node kích hoạt Failsafe, gửi lệnh LAND hoặc RTL qua MAVLink.
