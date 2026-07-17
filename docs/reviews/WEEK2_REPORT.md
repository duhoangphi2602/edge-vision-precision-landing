# Week 2 Report: Integration, Tracking & ML Candidate

## 1. System Status
- **Mission Contracts:** P1-A (Precision Landing) & P1-B (Vehicle Tracking) đang hoạt động với Python prototype.
- **CLI Plans:** Các tham số cho `p1_a_landing_v1.yaml` và `p1_b_tracking_v1.yaml` đã được thiết lập.
- **Deployment Matrix:** Sử dụng ONNX Runtime (CPU) cho Phase 1, sẵn sàng chuyển sang TensorRT/C++ cho Phase 2 (Gate 3).

## 2. Core Components Verified
- **State Machine:** Đã có logic SEARCH, LOCKED, LOST, LANDING, và EMERGENCY.
- **Robustness v0.1:** Đã xử lý target-loss timeout (1000ms), stale-data (qua latency tracking).
- **IPC Prototype:** UDP client/server hoạt động với độ trễ thấp (< 5ms).
- **Vehicle Tracking:** Nearest-to-center policy hoạt động ổn định.

## 3. Known Limitations (Record missing evidence)
- **Domain Gap:** Dataset training chưa sát hoàn toàn với góc nhìn UAV thực tế (hiện tượng bbox lớn).
- **Hybrid SITL:** Chưa có liên kết trực tiếp MAVSDK với PX4 SITL (sẽ làm ở Phase C++).
