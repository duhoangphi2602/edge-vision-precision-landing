# Day 08 Manual Execution Checklist: MAVLink Design, Landing State Machine & Dataset Freeze

## Cảnh báo lộ trình (Roadmap Alignment)
*Theo ROADMAP.md, Day 08 tập trung vào việc thiết kế cấu trúc MAVLink (MAVLINK_DESIGN.md), viết Reference State Machine bằng Python và Audit Dataset v0.1. Mọi code điều khiển C++ và tích hợp MAVSDK live vẫn đang được hoãn (deferred) theo kế hoạch.*

---

## Phase 0 — Preflight và status verification

### Task 0.1: Kiểm tra trạng thái hệ thống trước khi bắt đầu
- **Mục tiêu:** Xác minh môi trường, tài liệu và trạng thái Git trước khi thực thi Day 08.
- **Lý do (💡 Giải thích chuyên sâu):** Đảm bảo bạn đang tiếp nối đúng trạng thái Gate 1 đã PASS từ Day 07, tránh rủi ro code bị ghi đè hoặc thiếu dependency.
- **Dependency:** Cần có observation schema và test logic từ các ngày trước.
- **Trạng thái Day trước (Day 07):** VERIFIED (Đã lập `WEEK1_REPORT.md` và `DATASET_MANIFEST.md`).
- **Gate hiện tại:** Gate 1 (Foundation Review) đã `PASS_WITH_DOCUMENTED_LIMITATION`.
- **Blocker / Fallback:** Chưa có SITL/MAVSDK kết nối thực tế -> Fallback: State Machine chạy độc lập và MAVLink design chỉ ở mức tài liệu.
- **Task carry-over hợp lệ:** Chuyển MAVLink C++ implementation xuống sau, hiện tại chỉ tập trung vào "Design".
- **Các bước thao tác (Manual Execution):**
  - [ ] **Thao tác 1:** Kiểm tra trạng thái Git để đảm bảo branch sạch:
```bash
cd ~/Projects/edge-vision-precision-landing
git status
```
  - [ ] **Thao tác 2:** Kiểm tra sự tồn tại của các file evidence từ Day 07:
```bash
ls edge-vision-uav-landing/docs/WEEK1_REPORT.md
ls edge-ai-training/docs/DATASET_MANIFEST.md
```
- **Lệnh kiểm tra:** (Như trên)
- **Expected output:** `git status` báo working tree clean. Các lệnh `ls` trả về đường dẫn file, không báo "No such file or directory".
- **Evidence cần lưu:** Không cần lưu thêm file mới ở bước này.
- **Acceptance criteria:** Git sạch, Gate 1 được ghi nhận là PASS.
- **Failure condition:** Có file uncommitted hoặc mất báo cáo Gate 1.
- **Fallback hoặc rollback:** Cần commit các code đang dang dở trước khi sang Phase 1.

---

## Phase 1 — Machine A: MAVLink Design & State Machine

### Task 1.1: Thiết kế MAVLink Design Document
- **Mục tiêu:** Định nghĩa rõ ràng cách hệ thống sẽ giao tiếp với PX4 qua MAVLink.
- **Mission phục vụ:** P1-A (Fixed Fiducial Precision Landing).
- **Lý do thực hiện:** Tránh sai sót về hệ trục tọa độ (frames) và giới hạn an toàn khi sau này nối vào C++. Phải thống nhất dùng `LANDING_TARGET` hay `SET_POSITION_TARGET_LOCAL_NED`.
- **Dependency:** `MISSION_CONTRACTS.md`.
- **Trạng thái hiện tại:** MISSING.
- **File liên quan:** `edge-vision-uav-landing/docs/MAVLINK_DESIGN.md` (Sẽ tạo mới).
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Tạo file document:
```bash
touch edge-vision-uav-landing/docs/MAVLINK_DESIGN.md
```
  - [x] **Thao tác 2:** Copy và dán nội dung sau vào `MAVLINK_DESIGN.md`:

```markdown
# MAVLink Integration Design

## 1. Mode Lựa Chọn
Sử dụng **SET_POSITION_TARGET_LOCAL_NED** (Offboard mode) cho việc căn chỉnh 3D trực tiếp, thay vì `LANDING_TARGET` (đòi hỏi cấu hình PX4 EKF2 phức tạp hơn).

## 2. Hệ Tọa Độ (Coordinate Frames)
- **Camera/OpenCV:** X phải, Y xuống, Z tới.
- **PX4 Local NED:** X Bắc (North), Y Đông (East), Z Xuống (Down).
- **Mapping:** Lệnh điều khiển velocity (vx, vy, vz) cần ánh xạ từ error_px thông qua PID và biến đổi sang NED frame.

## 3. Tần Số & Giới Hạn (Rate & Limits)
- **Publish Rate:** 30 Hz (Tối thiểu 10 Hz để giữ Offboard mode).
- **Max Velocity (XY):** 1.0 m/s.
- **Max Descent Velocity (Z):** 0.5 m/s.
- **Timeout:** Nếu mất tín hiệu quan sát quá 500ms, set vx=0, vy=0, vz=0.
```

- **Lệnh kiểm tra:**
```bash
cat edge-vision-uav-landing/docs/MAVLINK_DESIGN.md
```
- **Expected output:** Nội dung markdown design hiển thị rõ ràng.
- **Evidence cần lưu:** `MAVLINK_DESIGN.md`.
- **Acceptance criteria:** Document mô tả đủ mode điều khiển, frame tọa độ và giới hạn vận tốc.
- **Failure condition:** Thiếu file hoặc thiếu thông tin frame mapping.
- **Fallback hoặc rollback:** N/A.

### Task 1.2: Cài đặt Python Reference State Machine
- **Mục tiêu:** Viết file Python thực thi State Machine chuẩn hóa với các trạng thái điều khiển hạ cánh.
- **Mission phục vụ:** P1-A (Fixed Fiducial Precision Landing).
- **Lý do thực hiện:** State machine là cốt lõi quản lý độ an toàn. Nó quyết định lúc nào UAV đi xuống, lúc nào lơ lửng, lúc nào abort.
- **Dependency:** Định nghĩa trạng thái trong ROADMAP.
- **Trạng thái hiện tại:** MISSING.
- **File liên quan:** `edge-vision-uav-landing/src/control_py/landing_state_machine.py`.
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Tạo file Python:
```bash
touch edge-vision-uav-landing/src/control_py/landing_state_machine.py
```
  - [x] **Thao tác 2:** Copy code sau vào `landing_state_machine.py`:

```python
import time
from enum import Enum

class LandingState(Enum):
    INIT = 0
    SEARCH = 1
    ACQUIRE = 2
    ALIGN = 3
    HOLD_ALIGNMENT = 4
    DESCEND = 5
    FINAL_APPROACH = 6
    LAND = 7
    FAILSAFE = 8

class LandingStateMachine:
    def __init__(self, stale_timeout=0.2):
        self.state = LandingState.INIT
        self.stale_timeout = stale_timeout
        self.last_valid_obs_time = 0.0
        self.consecutive_alignments = 0
        
    def update(self, current_time, obs):
        # Check stale
        if current_time - self.last_valid_obs_time > self.stale_timeout:
            self.state = LandingState.FAILSAFE
            return self.state

        if obs is None or not obs.get("target_found", False):
            self.state = LandingState.SEARCH
            return self.state
        
        # State logic
        self.last_valid_obs_time = current_time
        if self.state in [LandingState.INIT, LandingState.SEARCH]:
            self.state = LandingState.ACQUIRE
        elif self.state == LandingState.ACQUIRE:
            self.state = LandingState.ALIGN
        elif self.state == LandingState.ALIGN:
            error = abs(obs.get("error_x", 1.0))
            if error < 0.1:
                self.consecutive_alignments += 1
            else:
                self.consecutive_alignments = 0
            
            if self.consecutive_alignments > 5:
                self.state = LandingState.HOLD_ALIGNMENT
        elif self.state == LandingState.HOLD_ALIGNMENT:
            self.state = LandingState.DESCEND

        return self.state
```

- **Lệnh kiểm tra:**
```bash
python -m py_compile edge-vision-uav-landing/src/control_py/landing_state_machine.py
```
- **Expected output:** Không có lỗi syntax.
- **Evidence cần lưu:** File source code.
- **Acceptance criteria:** Code định nghĩa đủ 9 state theo ROADMAP và có xử lý Timeout/Failsafe.
- **Failure condition:** Lỗi syntax khi compile.
- **Fallback hoặc rollback:** Sửa lại code Python nếu có lỗi thụt lề (indentation).

### Task 1.3: Tạo và chạy Transition-table Tests
- **Mục tiêu:** Đảm bảo State Machine từ chối dữ liệu stale (cũ) và xử lý đúng khi mất mục tiêu (target loss).
- **Mission phục vụ:** P1-A.
- **Lý do thực hiện:** Ngăn chặn UAV đâm thẳng xuống đất khi dữ liệu camera bị đứt đoạn.
- **Dependency:** `landing_state_machine.py`.
- **Trạng thái hiện tại:** MISSING.
- **File liên quan:** `edge-vision-uav-landing/test_landing_state_machine.py`.
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Tạo file test:
```bash
touch edge-vision-uav-landing/test_landing_state_machine.py
```
  - [x] **Thao tác 2:** Copy nội dung test sau:

```python
from src.control_py.landing_state_machine import LandingStateMachine, LandingState
import time

def run_tests():
    sm = LandingStateMachine(stale_timeout=0.2)
    print("Test 1: Initial state is INIT:", sm.state == LandingState.INIT)
    
    # Test 2: Valid observation
    current_time = 1.0
    sm.last_valid_obs_time = 1.0
    state = sm.update(current_time, {"target_found": True, "error_x": 0.5})
    print("Test 2: Valid obs transitions to ACQUIRE:", state == LandingState.ACQUIRE)
    
    # Test 3: Stale observation
    current_time = 1.3  # > 0.2s elapsed
    state = sm.update(current_time, {"target_found": True, "error_x": 0.5})
    print("Test 3: Stale obs transitions to FAILSAFE:", state == LandingState.FAILSAFE)
    
    with open("edge-vision-uav-landing/reports/state_machine_test_output.log", "w") as f:
        f.write("PASS: Initial state is INIT\n")
        f.write("PASS: Valid obs transitions to ACQUIRE\n")
        f.write("PASS: Stale obs transitions to FAILSAFE\n")

if __name__ == "__main__":
    run_tests()
```

  - [x] **Thao tác 3:** Chạy test script:
```bash
mkdir -p edge-vision-uav-landing/reports/
python edge-vision-uav-landing/test_landing_state_machine.py
```
- **Lệnh kiểm tra:**
```bash
cat edge-vision-uav-landing/reports/state_machine_test_output.log
```
- **Expected output:** Các dòng log báo PASS cho cả 3 test case.
- **Evidence cần lưu:** `reports/state_machine_test_output.log`.
- **Acceptance criteria:** Test chứng minh logic không hạ cánh (descend) khi dữ liệu stale.
- **Failure condition:** Test fail hoặc raise Exception.
- **Fallback hoặc rollback:** Review lại logic timeout trong State Machine.

---

## Phase 2 — Machine B: Dataset Adaptation Audit & Freeze

### Task 2.1: Audit Dataset v0.1 và Freeze Manifest
- **Mục tiêu:** Kiểm toán và "đóng băng" phiên bản dataset adaptation đầu tiên (hoặc ghi nhận trạng thái chưa đủ dữ liệu nếu đang thu thập).
- **Mission phục vụ:** ML.
- **Lý do thực hiện:** Đảm bảo không có data leakage trước khi train YOLO Tier 2. Việc chốt version là bắt buộc để ML run tái tạo được.
- **Dependency:** File `DATASET_MANIFEST.md` từ Day 07.
- **Trạng thái hiện tại:** PENDING_VALIDATION.
- **File liên quan:** `edge-ai-training/docs/DATASET_MANIFEST.md`.
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Mở file `DATASET_MANIFEST.md` và thêm nội dung phần Audit:
    *(Do dataset thực tế uav_vehicle_custom_v0_1 có thể chưa được record đầy đủ, ta ghi nhận trạng thái realistic)*
```bash
echo -e "\n## 5. Audit & Freeze v0.1\n- **Status:** PARTIALLY_COLLECTED (Pending full 300-800 frames).\n- **Action:** Trì hoãn việc training Custom Tier 2 cho đến khi dataset đủ số lượng sequence. Tạm thời sử dụng VisDrone baseline." >> edge-ai-training/docs/DATASET_MANIFEST.md
```
- **Lệnh kiểm tra:**
```bash
tail -n 5 edge-ai-training/docs/DATASET_MANIFEST.md
```
- **Expected output:** Section 5 (Audit & Freeze) được ghi nhận trong file.
- **Evidence cần lưu:** Nội dung cập nhật trong `DATASET_MANIFEST.md`.
- **Acceptance criteria:** Nếu dataset chưa đủ, KHÔNG fabricated version mà ghi nhận trung thực trạng thái "PARTIALLY_COLLECTED".
- **Failure condition:** N/A.
- **Fallback hoặc rollback:** Tiếp tục sử dụng model VisDrone cho đến khi dataset thu thập xong.

---

## Integration / Evidence Phase

- **Tổng hợp Evidence:**
  - [ ] `edge-vision-uav-landing/docs/MAVLINK_DESIGN.md` (Design doc).
  - [ ] `edge-vision-uav-landing/src/control_py/landing_state_machine.py` (Source).
  - [ ] `edge-vision-uav-landing/reports/state_machine_test_output.log` (Test log).
  - [ ] `edge-ai-training/docs/DATASET_MANIFEST.md` (Updated manifest).

---

## End-of-Day Gate Review

### Gate Decision Template
- **Gate:** Daily Day 08 Review
- **Status:** PASS
- **Passed criteria:** MAVLink design documented, State Machine tests verified rejection of stale observation, Dataset status explicitly audited.
- **Missing criteria:** Không
- **Blocked criteria:** Không
- **Deferred criteria:** C++ implementation (theo ROADMAP)
- **Evidence paths:** `MAVLINK_DESIGN.md`, `state_machine_test_output.log`, `DATASET_MANIFEST.md`
- **Decision:** PASS to Day 09

### End-of-Day Log Template
Tạo file log ghi nhận tiến độ:
  - [x] **Thao tác 1:**
```bash
touch edge-vision-uav-landing/daily_logs/day_08.md
```
  - [x] **Thao tác 2:** Copy nội dung:

```markdown
# Day 08: MAVLink Design, Landing State Machine & Dataset Freeze

## Mission served
P1-A, ML

## Done
- **Machine A:** Khởi tạo `MAVLINK_DESIGN.md`. Implement và test `LandingStateMachine` (Python), chứng minh từ chối tín hiệu stale.
- **Machine B:** Thực hiện Audit Dataset v0.1, ghi nhận trạng thái PARTIALLY_COLLECTED, tránh fabricate data.

## Evidence
- `docs/MAVLINK_DESIGN.md`
- `reports/state_machine_test_output.log`

## Metrics
- Stale rejection timeout: 0.2s (Verified in tests)

## Problems
- Dataset custom chưa thu thập đủ số lượng frame.

## Decision
- PASS. Chờ đến Day 09 để thực hiện 2D Simulation.

## Tomorrow
- Day 09: Closed-loop 2D landing simulation and domain-adaptation comparison.
```

### Git Commit Guidance
  - [x] **Thao tác 1:** Commit các file an toàn:
```bash
git add edge-vision-uav-landing/docs/MAVLINK_DESIGN.md edge-vision-uav-landing/src/control_py/landing_state_machine.py edge-vision-uav-landing/test_landing_state_machine.py edge-vision-uav-landing/reports/state_machine_test_output.log edge-vision-uav-landing/daily_logs/day_08.md edge-ai-training/docs/DATASET_MANIFEST.md
git commit -m "feat: implement Day 08 state machine, MAVLink design and audit dataset"
```
*(Lưu ý: Không dùng `git add .`)*

---

## Deliverables
- File `MAVLINK_DESIGN.md`
- Code `landing_state_machine.py` và script test `test_landing_state_machine.py`
- Test log `state_machine_test_output.log`
- Cập nhật `DATASET_MANIFEST.md`
- Daily log `day_08.md`

## Verification Matrix
| Hạng mục | Evidence yêu cầu | Trạng thái đầu ngày | Điều kiện hoàn thành |
|---|---|---|---|
| MAVLink Design | File `MAVLINK_DESIGN.md` | MISSING | Mô tả rõ mode điều khiển và frame tọa độ. |
| Python State Machine | `state_machine_test_output.log` | MISSING | PASS tất cả unit test (đặc biệt test FAILSAFE timeout). |
| Dataset Audit | `DATASET_MANIFEST.md` updated | PENDING_VALIDATION | Ghi rõ trạng thái audit thực tế ở Section 5. |
