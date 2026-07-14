# Day 02: OpenCV reader + ArUco detection

## Done
- [Machine A] Hoàn thiện cấu hình `perception.yaml` và module `overlay.py`.
- [Machine A] Triển khai thành công `VideoReader` (V4L2 + YUYV fix) và `ArucoDetector` (flatten ID matrix fix).
- [Machine A] Hoàn thành pipeline `run_perception.py`, hiện overlay chuẩn xác pixel error. Đã tự động hóa khởi tạo thư mục log.
- [Machine A] Đã xuất log thành công ra `perception_baseline.csv` đúng chuẩn thiết kế Day 1.
- [Machine B] Đã chạy thành công 10 epochs YOLO baseline để chứng minh năng lực training môi trường PC GPU (RTX 3060 CUDA:0).

## Metrics
- FPS: ~18-20 FPS (Định dạng không nén YUYV qua USB, hoàn toàn đạt giới hạn băng thông thực tế)
- Latency: ~55 ms (Giai đoạn CV truyền thống)
- Error: Đã map đúng (`error_x`, `error_y` thời gian thực nhảy mượt mà khi di chuyển marker)
- CPU/RAM: Dưới 15% CPU (Rất nhẹ nhờ OpenCV)
- Test pass/fail: N/A (Chưa tới giai đoạn viết Unit test)

## Problems
- **OpenCV Timeout (Linux):** Gặp lỗi V4L2 timeout do luồng video bị nghẽn (phát sinh khi ngắt chương trình bằng Ctrl+C).
- **Mirror Effect:** Lỗi nhận diện ArUco do cố gắng lật hình (flip) cho thuận mắt khiến thuật toán không đọc được mã.
- **YOLO Runs Path:** YOLO tự động tạo thư mục `runs/` ở gốc thay vì thư mục `experiments/` do bị ảnh hưởng bởi cấu hình Global mặc định.

## Decision
- **Keep:** Tiếp tục sử dụng `V4L2` và `YUYV` cho camera trên Linux để đảm bảo không vỡ hình.
- **Cut:** Nghiêm cấm sử dụng phím `Ctrl+C` để tắt camera, bắt buộc dùng phím `q`. Không sử dụng `cv2.flip` để giữ đúng tọa độ quang học (optical frame).
- **Fix:** Luôn sử dụng đường dẫn tuyệt đối (`project=/path/...`) cho lệnh train YOLO để ép nó lưu vào đúng thư mục `experiments/`.

## Tomorrow
- **Laptop (Machine A):** Bắt tay vào Day 03 - Camera calibration & pose estimation (Biến pixel error 2D thành khoảng cách mét 3D).
- **PC GPU (Machine B):** Chuẩn bị train YOLO bản v0.1 trên bộ data bãi đáp thực tế.
