# Day 26 Log: Stabilizer Analyzer & Multi-Sequence Comparison

## Mission served: `P2-A`

## Done:
- **Machine A:** Hoàn thiện `stabilizer_analyzer.py` (sử dụng Affine Transform, Moving Average Smoothing, Jitter calculation). Khắc phục thành công sự cố với thư viện Numpy (`np.pad`).
- **Machine B:** Chạy kịch bản Batch Evaluation thực tế trên 4 video (1 gốc, 3 mức độ rung lắc: low, med, high).
  - Tích hợp pipeline xuất ra 8 video theo dõi Bounding Box của YOLO ONNX (trước và sau chống rung).
  - Bổ sung lệnh chuyển đổi FFmpeg H.264 (viewable) trực tiếp trên trình duyệt.
- Viết báo cáo phân tích thực tế `RESULTS.md` cho Project 2 dựa vào dữ liệu Jitter sinh ra từ CSV.

## Evidence:
- `gimbal-video-stabilization-analyzer/src/stabilizer_analyzer.py`
- `gimbal-video-stabilization-analyzer/data/output/comparison.csv`
- `gimbal-video-stabilization-analyzer/docs/RESULTS.md`
- 8 Video kết quả Tracking MP4.

## Metrics:
- Jitter giảm cực kỳ hiệu quả (từ 15.21 px xuống 3.68 px ở mức rung động mạnh). Hiệu năng khử rung lên đến ~75%.
- Cung cấp 8 video Tracking (H.264 MP4) với Bbox rõ nét.

## Problems:
- Quá trình chạy YOLO tracking và tạo video tốn thời gian CPU.
- Phần mềm tạo viền đen khi crop warpAffine.

## Decision:
- **PASS Day 26.** Project 2 P2-A cơ bản đã hoàn thiện về mặt nghiên cứu và Proof-of-concept.

## Tomorrow:
- Day 27 — Clean Clone, Documentation (README), Docker, One-command demo (Portfolio Gate E).
