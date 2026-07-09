## 1. Mục đích file

File này mô tả bối cảnh phần cứng, hệ điều hành, môi trường phát triển, giới hạn tài nguyên và cách tổ chức làm việc của người phát triển project.

AI Agent bắt buộc phải đọc file này trước khi đề xuất checklist, viết code, tạo Dockerfile, chọn thư viện hoặc thiết kế pipeline.

Mục tiêu là đảm bảo mọi hướng dẫn phù hợp với điều kiện thực tế:

- Không có drone thật
- Không yêu cầu phần cứng UAV thật
- Có thể chạy trên máy tính cá nhân
- Đang sử dụng Ubuntu 26.04 LTS
- Ưu tiên CPU-first trên laptop
- Ưu tiên GPU-first trên PC GPU
- Có thể làm song song trên 2 máy
- Cần tái lập bằng Docker/scripts
- Cần đo lường được FPS, latency, control error, robustness

---

## 2. Thông tin người phát triển

- Người phát triển chính: 1 người
- Cách làm việc mong muốn: mô phỏng workflow 2 người / 2 máy
- Mục tiêu: tạo portfolio chứng minh năng lực Edge AI / Computer Vision / Robotics / UAV Perception
- Trình độ hiện tại: đang học và triển khai thực tế từng bước
- Yêu cầu hướng dẫn: cần checklist chi tiết, deep dive, giải thích gốc rễ, không bỏ qua bước nhỏ

---

## 3. Mục tiêu kỹ thuật tổng thể

Project cần phát triển một hệ thống điều khiển và thị giác máy tính hoàn chỉnh cho UAV chạy trên máy tính cá nhân.

Không yêu cầu drone thật.

Hệ thống cần chứng minh năng lực qua:

- Computer Vision perception pipeline
- AI target tracking
- Precision landing logic
- PID control bằng C++
- IPC giữa Python và C++
- MAVLink-style command abstraction
- Robustness testing
- Benchmark FPS / latency / error
- Docker reproducibility
- Clean documentation
- Demo video

---

## 4. Nguyên tắc tổ chức project

Repository tổng là một workspace/monorepo.

Tuy nhiên, không được hiểu repository tổng là một project duy nhất.

Nguyên tắc bắt buộc:

- Một folder project chỉ chứa một project chính.
- Không trộn code của Project chính và Project phụ vào cùng một folder.
- Project phụ chỉ được đặt riêng trong folder riêng.
- Thư mục hỗ trợ như `edge-ai-training/`, `docs/`, `scripts/`, `daily_logs/` được phép nằm ở root vì chúng phục vụ toàn bộ workspace.
- AI Agent phải đi theo roadmap: hoàn thành Project chính trước, sau đó mới triển khai Project phụ.
- Trong từng project, có thể chia việc như 2 người / 2 máy làm song song.

Thứ tự ưu tiên triển khai:

1. Project chính: `precision-landing-uav-sitl`
2. Thư mục hỗ trợ training/export: `edge-ai-training`
3. Project phụ: `gimbal-video-stabilization-analyzer`

---

## 5. Cấu trúc repository mong muốn

```txt
edge-vision-precision-landing/
├── precision-landing-uav-sitl/              # Project chính: UAV precision landing + target tracking
├── gimbal-video-stabilization-analyzer/     # Project phụ: video stabilization + tracking quality analysis
├── edge-ai-training/                        # Thư mục hỗ trợ train/export model
├── docs/                                    # Tài liệu chung của workspace
├── scripts/                                 # Script setup/test/benchmark chung
├── daily_logs/                              # Nhật ký triển khai từng ngày
├── ROADMAP.md
├── AGENT_PACK_COMBINED.md
├── ENVIRONMENT_CONTEXT.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md

---

## 6. Chi tiết các dự án theo roadmap

Roadmap gồm 2 dự án portfolio chính và 1 thư mục hỗ trợ:

### Dự án 1 — Dự án chính
- **Tên đầy đủ:** Edge Vision Precision Landing & AI Target Tracking for UAV SITL
- **Thư mục dự án:** `precision-landing-uav-sitl/`
- **Mục tiêu kỹ thuật:**
  - Precision landing bằng AprilTag/ArUco
  - AI target tracking bằng YOLO
  - ONNX/OpenVINO edge inference benchmark
  - Python perception pipeline
  - C++ PID control node
  - C++ failsafe
  - Python → C++ IPC qua UDP/TCP/Unix socket
  - MAVLink-compatible message design (LANDING_TARGET / SET_POSITION_TARGET_LOCAL_NED)
  - Robustness testing dưới các điều kiện lỗi giả lập
  - Tính tái lập (reproducibility) bằng Docker/scripts
  - Báo cáo (reports), chỉ số đo lường (metrics) và video demo

---

### Dự án 2 — Dự án phụ
- **Tên đầy đủ:** Gimbal-Aware Video Stabilization & Tracking Quality Analyzer
- **Thư mục dự án:** `gimbal-video-stabilization-analyzer/`
- **Mục tiêu kỹ thuật:**
  - Ổn định hình ảnh video (Video stabilization)
  - Ước lượng chuyển động camera / dòng quang học (Optical flow / camera motion estimation)
  - Làm mượt quỹ đạo camera (Camera trajectory smoothing)
  - Phân tích chất lượng bám mục tiêu (Tracking quality analysis)
  - Đo lường chỉ số giảm rung lắc (Jitter reduction metric)
  - So sánh tỷ lệ mất dấu (Tracking lost-rate comparison)
  - Xuất báo cáo so sánh trước/sau khi ổn định (Before/after report)

---

### Thư mục hỗ trợ ML/Training
- **Tên thư mục:** `edge-ai-training/`
- **Lưu ý:** Đây không phải project portfolio thứ ba, mà là thư mục hỗ trợ cho Dự án 1.
- **Mục tiêu kỹ thuật:**
  - Huấn luyện mô hình YOLO (YOLO training)
  - Quản lý và chuẩn bị dữ liệu (Dataset management)
  - Xuất mô hình sang định dạng ONNX/OpenVINO
  - Đánh giá hiệu năng (Benchmark) trên GPU/CPU