# Current Project Progress Snapshot (Tổng quan tiến độ dự án)

## 1. Scan Summary (Tóm tắt kết quả quét)
- Thư mục gốc của workspace tồn tại tại `~/Projects/edge-vision-precision-landing`.
- `edge-vision-uav-landing` (Project 1) và `edge-ai-training` (ML Support) đã tồn tại.
- Project 2 chưa tồn tại (đúng như dự kiến).
- Các tài liệu kế hoạch (`day_01_checklist.md`, `day_02_checklist.md`) và nhật ký hàng ngày (`day_01.md`, `day_02.md`) của Day 1 và Day 2 đã tồn tại.
- Các file `ROADMAP.md`, `ENVIRONMENT_CONTEXT.md`, `requirements.txt` và `.gitignore` đã tồn tại và đúng định dạng.

## 2. Existing Important Files (Các file quan trọng hiện có)
- `ROADMAP.md`
- `ENVIRONMENT_CONTEXT.md`
- `AGENT_PACK_COMBINED.md`
- `requirements.txt`
- `.gitignore`
- Các file markdown của Project 1: `README.md`, `TECHNICAL_DESIGN.md`, `PROBLEM.md`, `REQUIREMENTS.md`, `TEST_PLAN.md`, `RESULTS.md`, `LIMITATIONS.md`, `MODEL_CARD.md`, `DATASET_MANIFEST.md`, `CLEAN_CLONE_TEST.md`, `PORTFOLIO_SUMMARY.md`

## 3. Existing Checklist / Plan Files (Các file kế hoạch/checklist hiện có)
- `docs/plans/day_01_checklist.md`
- `docs/plans/day_02_checklist.md`
- `edge-vision-uav-landing/daily_logs/day_01.md`
- `edge-vision-uav-landing/daily_logs/day_02.md`

## 4. Project Structure Observed (Cấu trúc dự án quan sát được)
- Project 1: `edge-vision-uav-landing/src`, `configs`, `tests`, `scripts`, `logs` ...
- Support Workspace: `edge-ai-training/datasets`, `experiments`, `models`, `logs`, `scripts`, `reports`

## 5. Progress by Area (Tiến độ theo từng khu vực)

### Workspace Root: edge-vision-precision-landing
- Môi trường, Gitignore, và các file cơ bản đã được thiết lập.

### Project 1: Edge Vision Precision Landing & AI Target Tracking for UAV SITL
- `perception.yaml` và `overlay.py` đã được triển khai.
- `VideoReader` và `ArucoDetector` đã được triển khai.
- Pipeline `run_perception.py` đang hoạt động, xuất log real-time ra file `perception_baseline.csv`.

### Support Workspace: edge-ai-training
- Đã chạy thành công 10 epochs để test YOLO baseline.

### Project 2: Gimbal-Aware Video Stabilization & Tracking Quality Analyzer
- Trì hoãn cho đến khi foundation (nền tảng) của Project 1 ổn định.

## 6. Progress by Day (Tiến độ theo ngày)

### Previous Day 1 (Ngày 1 trước đó)
- Khởi tạo repository.
- Tạo các file tài liệu cốt lõi (Core docs).
- Thiết lập thư mục monorepo.
- Định nghĩa log schema (cấu trúc log).

### Previous Day 2 (Ngày 2 trước đó)
- Đọc video bằng OpenCV kèm thuật toán nhận diện ArUco.
- Vẽ overlay lên frame (Frame overlay).
- Sinh file log ghi nhận pixel error theo thời gian thực (real-time metric log).
- Đã xác thực YOLO baseline trên GPU.

### Current DAY_03 (Hôm nay: Ngày 3)
- Sẵn sàng bắt đầu. Mục tiêu: Camera calibration (Hiệu chuẩn camera) + Pose estimation (Ước lượng tư thế 3D).

## 7. Progress by Machine/Role (Tiến độ theo máy/vai trò)

### Machine A / Role A (Laptop)
- Đã có perception pipeline hoàn chỉnh cho ArUco.
- Đã log pixel errors theo thời gian thực.

### Machine B / Role B (PC GPU)
- Môi trường Ultralytics hoạt động tốt.
- Đã chạy thành công YOLO baseline đầu tiên.

## 8. Completed Items (Các hạng mục đã hoàn thành)
- Hoàn thành các mục tiêu của Day 1 và Day 2 dựa theo ROADMAP.

## 9. Existing but Needs Review (Đã có nhưng cần review)
- Hiện tại không có yếu tố nào gây cản trở (blocking).

## 10. Pending Items (Các hạng mục đang chờ xử lý)
- Task của Day 3: Camera calibration và pose estimation.
- Đánh giá mô hình YOLO v0.1.

## 11. Blocked / Unclear Items (Các hạng mục bị chặn / Chưa rõ ràng)
- Không phát hiện hạng mục nào bị chặn.

## 12. Risks and Mismatches (Rủi ro và điểm chưa khớp)
- Các vấn đề như Linux V4L2 timeout và cv2.flip được phát hiện ở Day 2 đã được giải quyết bằng các quyết định rõ ràng trong log Day 2.
- Lỗi đường dẫn output mặc định của YOLO đã được khắc phục bằng cách sử dụng đường dẫn tuyệt đối.

## 13. Recommended Next Step (Bước tiếp theo đề xuất)
- Tiến hành thực thi DAY_03 Execution Plan (Camera calibration + pose estimation).

## 14. What Not To Do Yet (Những việc CHƯA ĐƯỢC làm)
- Không triển khai Project 2.
- Không bắt đầu phần PID control (thuộc task Day 4) trước khi hoàn thành calibration.
