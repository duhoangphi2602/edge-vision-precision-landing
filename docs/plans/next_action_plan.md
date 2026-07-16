# Next Action Plan: Day 06

*Dựa trên ROADMAP v1.0 (Production-Oriented, Mission-Driven)*

## Phase 1: Production Alignment & Cross-Process IPC (Day 06)
**Trọng tâm:** Biến code R&D thành code Production. Tách Perception và Control thành 2 quá trình chạy song song giao tiếp qua UDP.
- **ALIGN_001:** Setup YAML config chuẩn cho Mission P1-A, P1-B.
- **ALIGN_002:** Viết hợp đồng giao tiếp `MISSION_CONTRACTS.md` và schema JSON UDP.
- **ALIGN_003-005:** Đóng gói evidence hiện tại, thiết lập template Experiment Registry.
- **IPC Setup:** Viết code Python bắn/nhận UDP (`udp_sender.py`, `udp_receiver.py`). Chạy test failsafe timeout 200ms.

## Phase 2: SITL Integration (P1-A Precision Landing) (Day 07 - Day 10)
**Trọng tâm:** Nối C++ PID/Control vào PX4 SITL. 
- MAVLink bridge (MAVSDK hoặc ROS2 tùy thuộc vào quyết định kiến trúc).
- Landing State Machine (INIT -> SEARCH -> ACQUIRE -> ALIGN -> DESCEND -> LAND).

## Phase 3: Vehicle Tracking (P1-B) & ML Iterations (Day 11 - Day 15)
**Trọng tâm:** Phát hiện và Tracking xe (ByteTrack/BoTSORT).
- Cập nhật YOLO từ Tier 1 (VisDrone) lên Tier 2 (Custom).
- Tích hợp Target Selector policy (nearest_to_frame_center).

## Phase 4: Edge Deployment & Benchmarking (Day 16 - Day 20)
**Trọng tâm:** Đẩy mô hình xuống giới hạn Edge (Laptop CPU).
- Export ONNX, đo P50, P95 latency (mục tiêu <= 150ms).

## Phase 5: Video Stabilization & Tracking Analyzer (P2-A) (Day 21 - Day 26)
**Trọng tâm:** Project 2 độc lập. 
- Chống rung video và đánh giá ảnh hưởng lên Tracking.

## Phase 6: Final Polish & Portfolio Release (Day 27 - Day 30)
**Trọng tâm:** Đảm bảo 100% tái tạo được mã nguồn (Reproducibility).
- Docker hóa hệ thống. Thực hiện Clean Clone test. CLI One-command.
