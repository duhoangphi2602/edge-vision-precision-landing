# Day 01: Khởi tạo Kiến trúc Monorepo

## Done
- [Machine A] Khởi tạo thành công kiến trúc Monorepo `edge-vision-precision-landing`.
- [Machine A] Khởi tạo bộ khung dự án chính `edge-vision-uav-landing` với sự phân tách rõ ràng giữa `perception` (Python) và `control_cpp` (C++).
- [Machine A] Tạo thành công 11 file tài liệu nền tảng (README, PROBLEM, REQUIREMENTS, v.v.) định chuẩn chất lượng công nghiệp.
- [Machine B] Khởi tạo thành công `edge-ai-training` - không gian huấn luyện ML tách biệt hoàn toàn khỏi mã nguồn triển khai.
- [Shared] Thiết lập thành công `.gitignore` và `requirements.txt` chuẩn để quản lý môi trường và chặn file rác (model weights, datasets).
- [Shared] Định nghĩa thành công schema cho file log `perception_baseline.csv` (timestamp_ns, frame_id, detected, error_x, error_y, latency_ms) để ép chuẩn đầu ra cho thuật toán.

## Metrics
- FPS: N/A (Giai đoạn khởi tạo)
- Latency: N/A
- Error: N/A
- CPU/RAM: N/A
- Test pass/fail: N/A

## Problems
- Ban đầu có sự nhầm lẫn giữa thư mục Monorepo và thư mục Project con, dẫn đến đặt sai vị trí các file code và Markdown. Đã khắc phục và chuẩn hóa lại cấu trúc 100%. Môi trường trên cả 2 máy hoàn toàn sẵn sàng.

## Decision
- Áp dụng triết lý MLOps: Tách riêng thư mục `edge-ai-training` khỏi `edge-vision-uav-landing` để tránh làm phình to Git repo khi triển khai lên máy bay (UAV).
- Áp dụng triết lý Design by Contract: Định nghĩa file CSV header ngay từ đầu để các module độc lập bám theo.
- Quyết định dùng `.venv` cho prototyping 5 ngày đầu, và sẽ dùng `Docker` cho C++ IPC sau này.

## Tomorrow (Day 2 Plan)
- Laptop: Bắt đầu code module `video_reader.py` và thuật toán nhận diện ArUco Marker `aruco_detector.py`.
- PC GPU: Bắt đầu tải và chuẩn bị dataset nhỏ cho YOLO.
