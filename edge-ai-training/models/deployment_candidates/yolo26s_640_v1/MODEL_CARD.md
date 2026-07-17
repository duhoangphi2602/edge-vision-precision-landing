# Model Card: yolo26s_640_v1

## Intended Use
- Primary: Single vehicle tracking (P1-B).
- Hardware: Edge CPU via ONNX Runtime.

## Training Data
- Public datasets (VisDrone, COCO subsets).
- **Limitation:** Chưa có adaptation data từ thực tế bay UAV của dự án (Domain Gap hiện tại là góc nhìn camera và kích thước).

## Metrics & Thresholds
- Confidence Threshold: 0.40
- NMS IoU Threshold: 0.45
- Expected CPU Latency: ~35 - 50 ms.

## Cautions & Fallbacks
- Có thể gặp lỗi bám nhầm (false positive) hoặc khung bounding box to hơn mục tiêu thực. Trong trường hợp đó, thuật toán Target Selection Policy (Nearest to Center) sẽ đóng vai trò Fallback để giữ vững mục tiêu.
