# Current Project Progress Snapshot (Tổng quan tiến độ dự án)

**Version:** Production-Oriented, Mission-Driven v1.0
**Date:** 2026-07-16
**Current Day:** Day 05 (In Progress)
*Căn cứ xác định:* Dựa theo ROADMAP.md mới nhất, Day 05 đang trong trạng thái "In Progress". Các task của Machine A (Laptop) ở Day 5 (Replay, Fault Injection) đã hoàn tất và có evidence. Các task Machine B (PC GPU) đang chờ. Các task ALIGN (Day 5/6) đang chuẩn bị được thực thi.

## 1. Tóm tắt tiến độ theo Mission (Mission Progress)

### P1-A: Fixed ArUco Precision Landing
- **Trạng thái:** Đang phát triển (Development mode).
- **Đã hoàn thành:**
  - Nhận diện ArUco (ID 0) và Pose Estimation.
  - PID Controller (Anti-windup, first-sample handling).
  - Module giả lập (Replay) và bơm lỗi (Fault Injection).
- **Evidence đã lưu:** 
  - `reports/pid_simulation_summary.csv` (Đạt metrics settling time, overshoot).
  - `logs/fault_injection_log.csv` (Đã test robustness với noise, drop frame).
- **Blockers / Gaps:** Chưa có config YAML chính thức, chưa có MAVLink/SITL bridge, chưa giao tiếp IPC giữa Perception và Control.

### P1-B: Single Ground-Vehicle Tracking
- **Trạng thái:** Sơ khởi (Baseline testing).
- **Đã hoàn thành:** 
  - Train baseline YOLOv11n trên dataset VisDrone (Day 3/4).
- **Evidence đã lưu:** Weights YOLO, logs training.
- **Blockers / Gaps:** Chưa code logic Tracking (ByteTrack/BoTSORT), chưa có Target Selector, chưa có Error Analysis.

### P2-A: Video Stabilization & Tracking Analysis
- **Trạng thái:** Chưa bắt đầu.
- **Lý do:** Tuân thủ ROADMAP, Project 2 chỉ bắt đầu khi Project 1 đạt gate.

### ML Lifecycle (edge-ai-training)
- **Trạng thái:** Baseline completed. Đang ở giai đoạn Error Analysis.
- **Đã hoàn thành:** Setup dataset, baseline training (Tier 0/1).
- **Blockers / Gaps:** Chưa tiến hành Dataset Audit, thiếu file `EXPERIMENT_REGISTRY.csv` chuẩn. (Thuộc nhiệm vụ chưa chạy của Day 05 Machine B).

### Infrastructure
- **Trạng thái:** Đang thiết lập.
- **Đã hoàn thành:** Cấu trúc thư mục, daily logs.
- **Blockers / Gaps:** 
  - **Thiếu toàn bộ ALIGN tasks** (Từ 001 đến 005 theo Roadmap mới): Mission config, Interface Contracts, v.v.

---

## 2. Gaps & Blockers Quan Trọng (Cần giải quyết trước khi sang code logic mới)
1. **Mission Contracts & Interface:** Code Python hiện tại (vd: PID) đang test nội bộ (offline simulation), chưa tách thành 2 process rõ ràng (Perception Process -> UDP -> Control Process) theo chuẩn `target_observation_schema`.
2. **Config YAML:** `run_perception.py` hoặc các script cũ đang hardcode tham số. Cần chuyển sang đọc từ `configs/missions/`.
3. **ML Pipeline Evidence:** Machine B cần hoàn thiện báo cáo phân tích lỗi `yolo_v0_1_report.md` thực tế để quyết định chiến lược data cho Day 06+.

---

## 3. Lộ trình ưu tiên (Từ Hiện tại tới Day 30)

- **Day 06:** Production Alignment (ALIGN_001 -> 005) & IPC Setup. (Thiết lập quy chuẩn, giao tiếp UDP).
- **Day 07 - Day 10:** Hoàn thiện P1-A (Fixed Landing) với Gazebo SITL / MAVLink. Lấy evidence SITL. (Gate C).
- **Day 11 - Day 15:** Triển khai P1-B (Vehicle Tracking) & ML iteration (YOLO update + Tracking algorithm). Lấy evidence Tracking metrics.
- **Day 16 - Day 20:** Edge Deployment Benchmark & Tối ưu hóa (ONNX, Latency P95, FPS). Pass ML Gate D.
- **Day 21 - Day 26:** Triển khai P2-A (Gimbal Video Stabilization Analyzer).
- **Day 27 - Day 30:** Clean Clone, Documentation (README, MODEL_CARD), Docker, One-command demo. Pass Portfolio Gate E.

---

## 4. Quyết định Hành Động (Action Decision)
- **Tiếp tục với Day 06:** Tập trung giải quyết các task ALIGN trên Machine A. Mọi artifact đã tạo ở Day 1-5 được **GIỮ NGUYÊN**, chỉ bổ sung các file hợp đồng (Contracts) và refactor code đọc config. Machine B có thể chạy error analysis song song hoặc làm sau.
