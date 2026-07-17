# DAY_03 Execution Plan (Kế hoạch triển khai Ngày 3)

## 1. Goal of DAY_03 (Mục tiêu của Ngày 3)
- Ước lượng tư thế 3D (3D pose estimation) của ArUco marker bằng cách sử dụng các thông số camera intrinsic parameters.
- Chuyển đổi pixel error (2D) thành metric error (tọa độ 3D tính bằng mét).
- Train mô hình UAV-Domain YOLO baseline v0.1 đầu tiên có khả năng sử dụng được trên PC GPU (Thay vì đồ chơi COCO8).

## 2. What Previous Days Already Completed (Những gì các ngày trước đã hoàn thành)
- Hệ thống nhận diện ArUco marker (Perception pipeline).
- Tính toán 2D pixel error.
- Vẽ overlay và xuất log metric ra file CSV.
- Khởi tạo ML workspace và kiểm chứng PyTorch.

## 3. What Must Be Finished Before Starting DAY_03 (Những gì phải xong trước khi bắt đầu Ngày 3)
- Code từ Day 1 và Day 2 phải được commit thành công lên Git. (Đã xong)

## 4. Scope (Phạm vi công việc)
- Ước lượng thông số camera (Calibration).
- Thuật toán ước lượng tư thế bằng `solvePnP` (Pose estimation math).
- Cập nhật YOLO training pipeline để train trên dataset thật (phiên bản v0.1, VisDrone). Khởi tạo luồng Dataset Engineering (Manifest, Audit).

## 5. Out of Scope (Ngoài phạm vi)
- PID control.
- Tích hợp drone (PX4/SITL).
- Dự án Gimbal.

## 6. Machine A Tasks (Nhiệm vụ Machine A - Laptop)
- Tạo `src/estimation/camera_calibration.py` (Script để tính toán hoặc load camera matrix).
- Tạo `src/estimation/pose_estimator.py` (Class thực thi `cv2.solvePnP` trên tọa độ góc của ArUco marker).
- Tạo `configs/camera.yaml` (Lưu thông số intrinsics).
- Viết báo cáo `reports/calibration_report.md`.

## 7. Machine B Tasks (Nhiệm vụ Machine B - PC GPU)
- Khởi tạo thư mục Dataset Manifest và Audit.
- Tải dataset UAV cho target tracking (VisDrone).
- Train UAV-domain YOLO baseline v0.1: `yolo detect train data=VisDrone.yaml ... name=EXP_001_visdrone_yolo26n_640_baseline`
- Lưu lại mô hình `best.pt`, file `results.csv`, và các metrics chứng minh (evidence).

## 8. Shared Tasks (Nhiệm vụ chung)
- Đảm bảo hệ tọa độ (Camera vs Marker frames) được tài liệu hóa chính xác để tránh nhầm lẫn.

## 9. Files/Folders Expected to Change After User Approval (File/Thư mục dự kiến thay đổi sau khi được duyệt)
- `edge-vision-uav-landing/configs/camera.yaml`
- `edge-vision-uav-landing/src/estimation/__init__.py`
- `edge-vision-uav-landing/src/estimation/camera_calibration.py`
- `edge-vision-uav-landing/src/estimation/pose_estimator.py`
- `edge-vision-uav-landing/reports/calibration_report.md`
- `edge-ai-training/experiments/` (Logs và models cho bản v0.1)
- `edge-ai-training/datasets/manifests/`
- `edge-ai-training/reports/`
- `edge-vision-uav-landing/daily_logs/day_03.md` (Sau khi kết thúc ngày)

## 10. Commands User Should Run Manually (Lệnh người dùng tự chạy)
(Trên Laptop)
```bash
git status
git branch
git checkout -b day03/pose-estimation
# Chạy script hiệu chuẩn camera (script sẽ được cung cấp sau)
python scripts/calibrate_camera.py
```
(Trên PC GPU)
```bash
# Chạy lệnh smoke test để đảm bảo môi trường
yolo detect train data=coco8.yaml model=yolo26n.pt epochs=1 project=experiments name=SMOKE_coco8_yolo26n
# Sau khi pass, chạy lệnh training baseline thật
yolo detect train data=VisDrone.yaml model=yolo26n.pt epochs=30 patience=10 batch=-1 imgsz=640 project=experiments name=EXP_001_visdrone_yolo26n_640_baseline
```

## 11. Verification Commands (Lệnh kiểm tra)
```bash
# Kiểm tra kết quả đầu ra của pose estimation
python src/estimation/pose_estimator.py
```

## 12. Risks (Rủi ro)
- Hàm `solvePnP` của OpenCV có thể gặp tình trạng ambiguity (mơ hồ) nếu marker quá nhỏ hoặc ở quá xa, dẫn đến hiện tượng lật tọa độ (flip errors).

## 13. Acceptance Criteria (Tiêu chí nghiệm thu)
- Ước lượng 3D pose (tvec, rvec) được in ra hoặc log lại thành công.
- Các thông số camera intrinsics được lưu vào `configs/camera.yaml`.
- Mô hình YOLO v0.1 xuất ra thành công trọng số (`weights`).

## 14. Stop Conditions (Điều kiện dừng)
- Dừng lại và chờ người dùng duyệt trước khi sửa/tạo bất kỳ đoạn code nào.
