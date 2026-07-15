# Ghi chú Training: TRN_001_visdrone_yolo11n_640

## Bối cảnh
- **Mục tiêu**: Đánh giá Baseline của mô hình YOLOv11 nano trên bộ dữ liệu VisDrone2019 (Góc nhìn UAV từ trên cao).
- **Môi trường**: Machine B (PC GPU) - NVIDIA GeForce RTX 3060 (12GB VRAM).
- **Lệnh thực thi**: Lấy từ `COMMAND.txt`.

## Thông số kỹ thuật (Từ args.yaml)
- **Model**: `yolo11n.pt` (Pretrained weights).
- **Dataset**: `VisDrone.yaml`.
- **Epochs**: 30 (Patience = 10).
- **Batch Size**: `-1` (AutoBatch - Tự động giãn nở batch size để fill VRAM, max 60% VRAM sử dụng).
- **Image Size**: 640.
- **Cache**: `disk` (Giúp tăng tốc dataloader nhưng chiếm ~30GB đĩa).
- **Tính xác định**: `seed = 42` và `deterministic = True`.

## Quan sát và Sự cố (Failure Cases & Curves)
- Ban đầu YOLO lưu các biểu đồ (curves) như `results.png`, `PR_curve.png` và các batch ảnh test (e.g. `val_batch0_pred.jpg`). Tuy nhiên để giải phóng không gian cho Git Repository, các file ảnh nặng này đã bị xóa an toàn.
- Metric đánh giá chính xác đã được lưu trong `results.csv`.
- Sự cố nổi bật: Độ chính xác trên class `tricycle` và `awning-tricycle` rất thấp do Class Imbalance (Được phát hiện thông qua biểu đồ `labels.jpg`). Hơn 90% bounding boxes là small objects (chiếm < 10% diện tích ảnh).
