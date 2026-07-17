# Gate 1 Foundation Review & Week 1 Report

## 1. Trạng thái tổng quan
**Quyết định:** `PASS_WITH_DOCUMENTED_LIMITATION`

## 2. Kết quả kiểm tra (Checklist)
| Hạng mục | Phân loại | Ghi chú / Evidence |
|---|---|---|
| ArUco `DICT_4X4_50`, ID 0 | Verified | Log output: PASS (test_aruco_wrong_id) |
| Correct-ID / Wrong-ID tests | Verified | Log output: Rejected marker ID != 0 |
| Pixel-error & Sign convention | Verified | Trục x, y chuẩn OpenCV |
| Python PID tests & Metrics | Verified | `reports/pid_simulation_summary.csv` |
| Replay Pipeline & Fault Injection | Verified | Xử lý được drop frame, noise |
| Mission Config & Schema (JSON/UDP) | Verified | `MISSION_CONTRACTS.md` |
| PX4/Gazebo Startup / Hybrid SITL | Deferred | Đang xử lý ở Phase SITL kế tiếp |

## 3. Blockers / Limitations
- **Limitation 1:** Giao tiếp UDP Python <-> C++ chưa thực thi (được dời sang Day 15+). Hiện tại đang test thuần Python.
- **Limitation 2:** SITL Gazebo chưa bay thực tế, mới đo đạc controller độc lập.
