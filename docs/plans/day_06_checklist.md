# Day 06 Manual Execution Checklist: Production Alignment & IPC Setup

## Mục tiêu tổng thể (Goal)
Hoàn thành các task `ALIGN_001` đến `ALIGN_005` (thuộc Infrastructure và P1-A) theo chuẩn "Production-Oriented" của Roadmap mới. Tách biệt Perception Process và Control Process bằng IPC (UDP), tạo tiền đề tích hợp SITL ở Day 07. Giữ nguyên mọi code xử lý thuật toán (ArUco, PID, YOLO) đã chạy ổn định ở Day 1-5, chỉ nâng cấp lớp vỏ bao bọc (Wrapper/Config) bên ngoài.

---

## Phase 1 — ALIGN_001 & ALIGN_002: Thiết lập Mission Config & Schema (Infrastructure)

**Mục tiêu:** Định nghĩa chuẩn file cấu hình YAML và chuẩn dữ liệu đầu ra JSON để các Process giao tiếp với nhau mà không bị lỗi tương thích.
**Lý do:** Tránh hard-code. Khi phỏng vấn hoặc chạy demo thực tế, Engineer chỉ cần truyền một file config để cấu hình tham số, không được mở file Python ra sửa biến.

- [ ] **[Machine A - Laptop] Thao tác 1:** Tạo thư mục cấu hình.
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
mkdir -p configs/missions configs/schemas
touch configs/missions/fixed_aruco_landing_v1.yaml
```

- [ ] **[Machine A - Laptop] Thao tác 2:** Điền cấu hình `fixed_aruco_landing_v1.yaml`.
**Đầu vào (Input):** Thông số từ `ROADMAP.md` (mission_id, marker_dictionary, v.v.).
**Cách triển khai:** Copy nội dung sau:
```yaml
mission_id: P1_A_FIXED_ARUCO_LANDING
marker_type: aruco
marker_dictionary: DICT_4X4_50
marker_id: 0
marker_size_m: 0.20
landing_pad_motion: fixed
transport: udp
bind_address: 127.0.0.1
perception_to_control_port: 5600
stale_timeout_ms: 200
```

- [ ] **[Machine A - Laptop] Thao tác 3:** Tạo file Schema Hợp đồng (Interface Contract).
```bash
touch src/ipc/target_observation_schema.json
```
**Cách triển khai:** Copy nội dung Schema chuẩn JSON từ ROADMAP (Phần 3.1.5) dán vào file này để tham chiếu cho C++ và Python.

---

## Phase 2 — Tách luồng IPC: Perception Server (P1-A)

**Mục tiêu:** Nâng cấp script chạy Perception để nó bắn data qua UDP thay vì gọi trực tiếp PID trong cùng một file python.
**Lý do:** Trong SITL, PID thường chạy ở vòng lặp rất cao (30-50Hz), trong khi Camera/AI chạy ở 15-30Hz. Phải tách riêng Process để không chặn (block) lẫn nhau.

- [ ] **[Machine A - Laptop] Thao tác 4:** Tạo module UDP Sender.
```bash
touch src/ipc/udp_sender.py
```
**Cách triển khai:** Viết class `UDPSender` sử dụng thư viện `socket` của Python, có hàm `send_observation(json_data)`.
**File bị ảnh hưởng:** `src/ipc/udp_sender.py` (Mới).

- [ ] **[Machine A - Laptop] Thao tác 5:** Cập nhật script nhận diện (Wrapper).
```bash
touch scripts/run_perception.py
```
**Cách triển khai:** 
- Đọc config bằng thư viện `yaml`.
- Khởi tạo `ReplaySource` hoặc `cv2.VideoCapture` dựa vào args `--source`.
- Chạy vòng lặp lấy frame -> Gọi `ArucoDetector` -> Tính `error_px` -> Tạo chuỗi JSON theo chuẩn `target_observation_schema.json` -> Dùng `UDPSender` bắn đi.
**File bị ảnh hưởng:** `scripts/run_perception.py` (Mới).

---

## Phase 3 — Tách luồng IPC: Control Receiver (P1-A)

**Mục tiêu:** Tạo Process thứ 2 (Control) liên tục lắng nghe UDP và chạy PID loop.
**Lý do:** Giữ PID Loop luôn ở tần số 30Hz, nếu quá `200ms` không nhận được JSON từ Perception -> Chuyển state sang `TARGET_LOST` và ngưng cấp PID (Anti-windup/Failsafe).

- [ ] **[Machine A - Laptop] Thao tác 6:** Tạo module UDP Receiver.
```bash
touch src/ipc/udp_receiver.py
```
**Cách triển khai:** Viết class `UDPReceiver` có hàm `get_latest_observation()`, lưu ý xử lý non-blocking hoặc dùng thread.

- [ ] **[Machine A - Laptop] Thao tác 7:** Chạy Control Loop mô phỏng.
```bash
touch scripts/run_control.py
```
**Cách triển khai:** 
- Vòng lặp `while True:` với `time.sleep(1/30)`.
- Gọi `get_latest_observation()`.
- Tính thời gian trễ. Nếu `< 200ms`, gọi hàm PID có sẵn (`src/control_py/pid_controller.py`). Nếu `> 200ms`, báo mất tín hiệu.

---

## Phase 4 — Chạy thử nghiệm và Verification (P1-A)

- [ ] **[Machine A - Laptop] Thao tác 8:** Kiểm tra (Test).
**Lệnh kiểm tra:** (Mở 2 Terminal)
*Terminal 1:*
```bash
python scripts/run_control.py --config configs/missions/fixed_aruco_landing_v1.yaml
```
*Terminal 2:*
```bash
python scripts/run_perception.py --mission marker_landing --source replay --input videos/test_landing.mp4 --config configs/missions/fixed_aruco_landing_v1.yaml
```

**Expected Output:** 
- Terminal 1 (Control) in ra log liên tục: "Nhận data chậm trễ: 15ms. Lệnh PID XYZ".
- Khi bạn chủ động bấm Ctrl+C ở Terminal 2 (tắt camera/Perception), Terminal 1 phải báo: "CẢNH BÁO: Mất tín hiệu quá 200ms. Failsafe kích hoạt. PID set 0."

**Acceptance Criteria (Tiêu chí nghiệm thu):** 
1. Hệ thống không bị văng lỗi khi thiếu luồng.
2. Failsafe timeout 200ms hoạt động chính xác.
3. Không sửa bất kỳ logic tính toán toán học nào trong core ArUco/PID của Day 2/4.

**Evidence Cần Lưu:** Lưu lại log output của Terminal 1 vào thư mục `logs/ipc_test_day06.txt`. Khởi tạo `MISSION_CONTRACTS.md` ghi dấu mốc.

**Fallback khi lỗi:** Nếu UDP mất quá nhiều gói tin trên localhost, fallback về ZeroMQ (ZMQ) publish-subscribe. Nhưng với localhost, UDP (socket) là đủ tốt.

---

## Phase 5 (Song song) — ML Error Analysis (ML Lifecycle)

- [ ] **[Machine B - PC GPU] Thao tác 9:** Hoàn thiện task Day 5 còn tồn đọng:
Đọc tập validation `TRN_002` (YOLO), điền thủ công kết quả sai lệch vào `reports/yolo_v0_1_report.md` (False Positives, False Negatives) để chuẩn bị cho chiến lược data augment Day 11.
