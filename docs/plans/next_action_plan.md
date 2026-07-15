# Next Action Plan (Kế hoạch hành động tiếp theo)

## 1. Current State (Trạng thái hiện tại)
Day 1 (Khởi tạo) và Day 2 (ArUco Detection + Video Reader) đã hoàn thành. Perception pipeline đang tính toán pixel errors (lỗi độ lệch pixel) theo thời gian thực và môi trường YOLO trên GPU đã được kiểm chứng.

## 2. Current ROADMAP Day: DAY_03 (Ngày hiện tại trong Roadmap: Ngày 3)

## 3. Immediate Next Step (Bước tiếp theo ngay lập tức)
Bắt đầu triển khai DAY_03: Camera calibration (Hiệu chuẩn camera) và Pose estimation (Ước lượng tư thế 3D).
Mục tiêu là chuyển đổi 2D pixel errors thành 3D metric distances (khoảng cách thực tế bằng mét).

## 4. Machine A Tasks (Nhiệm vụ của Machine A / Laptop)
- Lập trình file `src/estimation/camera_calibration.py`.
- Lập trình file `src/estimation/pose_estimator.py`.
- Tạo file cấu hình `configs/camera.yaml`.
- Viết báo cáo `reports/calibration_report.md`.

## 5. Machine B Tasks (Nhiệm vụ của Machine B / PC GPU)
- Train mô hình YOLO v0.1 trên dataset UAV/landing thực tế.
- Lưu lại mô hình tốt nhất (best model) và tạo báo cáo training ban đầu (results.csv, confusion matrix).

## 6. Shared Tasks (Nhiệm vụ chung)
- Commit các thay đổi code cho Day 3 lên Git.

## 7. Commands User Should Run Manually (Các lệnh người dùng nên tự chạy)
(Kiểm tra môi trường)
```bash
lsb_release -a
uname -a
python3 --version
git status
```

## 8. Files User Should Create/Edit Manually (Các file người dùng nên tự tạo/sửa)
- Cung cấp các hình ảnh mẫu (sample images) để chạy camera calibration hoặc quyết định dùng phương pháp synthetic calibration (hiệu chuẩn mô phỏng giả lập).

## 9. Verification (Xác minh)
- File `pose_estimator.py` phải chạy được và xuất ra translation vector 3D (tvec).
- Báo cáo `reports/calibration_report.md` phải chứa các thông số camera intrinsic parameters (thông số nội tại của camera).

## 10. Risks (Rủi ro)
- Quá trình hiệu chuẩn (Calibration) đòi hỏi ảnh mẫu phải tốt. Nếu ảnh thực tế quá mờ hoặc nhiễu, pose estimation sẽ không chính xác. Có thể cần sử dụng synthetic calibration làm phương án dự phòng (fallback).

## 11. Stop Conditions (Điều kiện dừng)
- Dừng lại sau khi DAY_03 Execution Plan được người dùng duyệt.

## 12. Review Checklist Before Continuing (Checklist cần xem lại trước khi tiếp tục)
- [ ] Đọc DAY_03 Execution Plan.
- [ ] Chốt phương pháp hiệu chuẩn (Option A: Dùng ảnh thật, Option B: Synthetic).
