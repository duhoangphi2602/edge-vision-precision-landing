# Closed-Loop 2D Simulation Report v0

## Mission
P1-A Fixed Fiducial Precision Landing

## Mục Tiêu (Goals)
Chứng minh Controller (PID) và Landing State Machine hội tụ an toàn trong môi trường 2D giả lập trước khi deploy lên SITL.

## Metrics Đo Lường
- **Kịch bản:** 0.5m, 1.0m, 2.0m, diagonal (1.5m, 1.5m).
- **Settling time:** < 8s.
- **Overshoot:** Không đáng kể.
- **State Check:** Xác nhận State cập nhật đúng trình tự từ ACQUIRE -> ALIGN -> HOLD_ALIGNMENT -> DESCEND.

## Kết quả
- PID hội tụ thành công với error < 0.05m cho tất cả các kịch bản trong thời gian giả lập 10s.
- Các file log chi tiết:
  - `reports/sim_2d_0.5m.csv`
  - `reports/sim_2d_1.0m.csv`
  - `reports/sim_2d_2.0m.csv`
  - `reports/sim_2d_diagonal.csv`

## Hướng đi tiếp theo (Next Steps)
Sẵn sàng cho việc gửi lệnh qua MAVLink UDP (Day 10) và tích hợp vào SITL (Day 11).
