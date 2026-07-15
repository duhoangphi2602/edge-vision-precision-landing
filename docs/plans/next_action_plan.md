# Next Action Plan: Day 05

## Mục tiêu (Day 05)
1. **Replay Mode (Phát lại Video):** Tích hợp video thực tế từ drone (có kèm nhiễu thật) vào đường ống nhận diện để thay thế cho bộ ảnh tĩnh.
2. **Fault Injection (Bơm lỗi):** Giả lập các tình huống xấu (nhòe khung hình, mất tín hiệu tạm thời, gió giật làm mờ camera) để kiểm tra sức chịu đựng của bộ điều khiển PID.
3. **Tracking Integration:** Tích hợp bộ Tracker (ByteTrack/BoTSORT) vào để bù đắp các khung hình bị mất.

## Thao tác chuẩn bị
- [ ] Chuẩn bị video test (Flight logs/Video thực tế).
- [ ] Viết script Replay kết nối thẳng vào `ArucoDetector` hoặc `YOLODetector`.
- [ ] Viết module `FaultInjector` để chủ động drop frame.
- [ ] Xác nhận PID vẫn hoạt động mượt mà (Settling Time < 5s) dưới các điều kiện khắc nghiệt.
