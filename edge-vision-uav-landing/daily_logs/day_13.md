# Day 13: Vehicle tracking mode, ONNX integration, and challenge evaluation

## Mission served
P1-B, ML

## Done
- **Machine A:** Viết script `vehicle_tracking_demo.py` tích hợp model ONNX YOLO và ByteTrack. Cài đặt policy khóa mục tiêu `car` gần tâm màn hình nhất. Khắc phục sự cố codec và xuất thành công video demo định dạng webm cùng tracking metrics.
- **Machine B:** Tạo ma trận đánh giá model (Selection Matrix) cho các challenge sequences. Đã phân tích và ra quyết định sử dụng bản `yolo26s_640.onnx`.

## Evidence
- Config: `p1_b_tracking_v1.yaml`
- Video & Logs: `runs/day13/tracking_demo.webm`, `runs/day13/tracking_metrics.csv`
- Reports: `reports/day13/selection_matrix.csv`

## Metrics
- Target-lock policy: Nearest to center (VERIFIED)
- P50 Tracking Latency (ONNX): ~13.3 ms (MEASURED)
- Fallback/Target switch behavior: Bắt đầu lại SEARCH khi mục tiêu mất quá 1000ms.

## Problems
- Thư viện OpenCV mặc định trên hệ điều hành không hỗ trợ mã hoá H.264 (lỗi v4l2m2m hardware encoder) gây ra lỗi nén file MP4. Đã xử lý triệt để bằng cách dùng `VP80` (.webm) hoặc mã hoá cơ bản `mp4v`.
- Tracking box bị rộng do hiện tượng Domain Shift (xe quá to và góc chéo so với tập train). Đã hiểu nguyên lý và lập bảng ma trận chọn model thay thế (`yolo26s`).

## Decision
- PASS. Chọn `yolo26s_640.onnx` làm Production Model.

## Tomorrow
- Day 14: Gate 2 integration review and validated candidate freeze.
