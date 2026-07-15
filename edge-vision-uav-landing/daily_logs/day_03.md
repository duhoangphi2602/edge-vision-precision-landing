# Day 03: Camera calibration + Pose estimation

## Done
- [Machine A] Khởi tạo thư mục `src/estimation` và tạo schema `camera.yaml` cho thông số camera matrix.
- [Machine A] Hoàn thiện class `CameraCalibration` để load thông số intrinsics.
- [Machine A] Hoàn thiện class `PoseEstimator` áp dụng `solvePnP` chuyển từ 2D pixels qua tọa độ 3D mét (tvec, rvec). Đã test giả lập chạy mượt mà.
- [Machine A] Xuất báo cáo Calibration giả lập.
- [Machine B] Đã xác minh CUDA và môi trường YOLO.
- [Machine B] Đã hoàn thành COCO8 smoke test.
- [Machine B] Đã tạo dataset manifest và audit report cho VisDrone (Đảm bảo 100% data sạch).
- [Machine B] Đã train xong baseline UAV-domain v0.1 (YOLO11n, TRN_001). Đạt mAP50 = 27.3%, mAP50-95 = 15.3%. Đã lưu Artifacts.

## Next
- Đẩy source code lên git (`feat/day3-calibration-and-gpu-setup`).
- Chạy đánh giá error analysis trên model baseline (Day 04).
