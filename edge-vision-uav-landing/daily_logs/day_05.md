# Day 05: Replay Mode, Fault Injection & Error Analysis

## Done
- [x] Tạo `ReplaySource` class với tính năng giả lập thời gian thực.
- [x] Cài đặt `FaultInjector` với Config YAML (Gaussian noise, Blur, Frame Drop, Occlusion).
- [x] Chạy test và sinh log `fault_injection_log.csv`.
- [x] Viết báo cáo Error Analysis cho mô hình YOLO 960px (`yolo_v0_1_report.md`).
- [x] Khởi tạo quy trình xuất báo cáo Dataset Audit Delta.

## Metrics
- Replay FPS: Đạt chuẩn 30 FPS theo mock video.
- Tỉ lệ frame drop giả lập: ~10% (theo YAML).

## Problems
- Fault Injection làm giảm tỉ lệ phát hiện đáng kể (Occlusion che mất 50% mục tiêu). Sẽ cần Tracker (như ByteTrack) để giữ ID khi mục tiêu bị che khuất.

## Decision
- Áp dụng Tracking algorithm (Day 06) để bù đắp các frame bị rớt do Fault Injection.

## Tomorrow
- Laptop: Tích hợp YOLO Tracking logic.