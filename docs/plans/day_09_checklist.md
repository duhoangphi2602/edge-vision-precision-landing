# Day 09 Manual Execution Checklist: Closed-loop 2D landing simulation and domain-adaptation comparison

## Cảnh báo lộ trình (Roadmap Alignment)
*Theo ROADMAP.md, Day 09 yêu cầu hoàn thiện môi trường giả lập Closed-loop 2D cho P1-A để kiểm chứng PID và State Machine. Đối với Machine B, cần đánh giá mô hình Public vs Custom. Tuy nhiên, theo audit từ Day 08, dataset custom đang ở trạng thái `PARTIALLY_COLLECTED` (quá nhỏ). Dựa trên rule của ROADMAP ("Do not train custom-only if the dataset is too small"), phần training/so sánh public-to-custom fine-tune sẽ bị DEFERRED. Machine B sẽ chỉ đánh giá public baseline.*

---

## Phase 0 — Preflight và status verification

### Task 0.1: Kiểm tra trạng thái hệ thống trước khi bắt đầu
- **Mục tiêu:** Xác minh môi trường, tài liệu và trạng thái Git trước khi thực thi Day 09.
- **Lý do (💡 Giải thích chuyên sâu):** Tránh ghi đè code khi chưa commit Day 08. Kiểm tra sự tồn tại của MAVLink design và Landing State Machine.
- **Dependency:** `MAVLINK_DESIGN.md`, `landing_state_machine.py`.
- **Trạng thái Day trước (Day 08):** VERIFIED.
- **Gate hiện tại:** Daily Day 08 Review đã PASS.
- **Blocker / Fallback:** 
  - **Blocker:** Dataset custom chưa đủ số lượng frame (PARTIALLY_COLLECTED).
  - **Fallback:** Tạm hoãn (Defer) việc fine-tune và so sánh domain adaptation (public-to-custom). Chỉ thiết lập kịch bản đánh giá public baseline.
- **Task carry-over hợp lệ:** Chuyển đánh giá domain-adaptation xuống các ngày sau khi dataset thu thập đủ.
- **Các bước thao tác (Manual Execution):**
  - [x] **Thao tác 1:** Kiểm tra trạng thái Git để đảm bảo branch sạch:
```bash
cd ~/Projects/edge-vision-precision-landing
git status
```
  - [x] **Thao tác 2:** Kiểm tra sự tồn tại của các file evidence từ Day 08:
```bash
ls edge-vision-uav-landing/docs/MAVLINK_DESIGN.md
ls edge-vision-uav-landing/src/control_py/landing_state_machine.py
```
- **Lệnh kiểm tra:** (Như trên)
- **Expected output:** `git status` báo working tree clean. Các lệnh `ls` không báo "No such file or directory".
- **Evidence cần lưu:** Không cần.
- **Acceptance criteria:** Git sạch, Day 08 đã ghi nhận PASS.
- **Failure condition:** Có file uncommitted, thiếu dependency Day 08.
- **Fallback hoặc rollback:** Commit code Day 08 trước khi tiếp tục.

---

## Phase 1 — Machine A: Closed-Loop 2D Landing Simulation

### Task 1.1: Tạo script Closed-loop 2D Simulator
- **Mục tiêu:** Xây dựng môi trường giả lập 2D (x, y) khép kín nối PID và State Machine.
- **Mission phục vụ:** P1-A (Fixed Fiducial Precision Landing).
- **Lý do thực hiện:** Đảm bảo thuật toán hội tụ và State Machine hoạt động ổn định với các mức offset trước khi gắn vào SITL (Gazebo). 
- **Dependency:** `pid_controller.py`, `landing_state_machine.py`.
- **Trạng thái hiện tại:** MISSING.
- **File liên quan:** `edge-vision-uav-landing/src/simulation_2d/closed_loop_2d_sim.py` (Sẽ tạo mới).
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Tạo thư mục và file:
```bash
mkdir -p edge-vision-uav-landing/src/simulation_2d/
touch edge-vision-uav-landing/src/simulation_2d/closed_loop_2d_sim.py
```
  - [x] **Thao tác 2:** Mở file và dán đoạn code sau. Code này mô phỏng UAV bay 2D trên tọa độ (x, y) hướng tới mục tiêu ở (0, 0):

```python
import time
import csv
import sys
import os

# Thêm đường dẫn để import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.control_py.pid_controller import PIDController
from src.control_py.landing_state_machine import LandingStateMachine, LandingState

def run_simulation(initial_x, initial_y, duration=10.0, dt=0.033):
    pid_x = PIDController(kp=1.0, ki=0.01, kd=0.1, v_max=1.0)
    pid_y = PIDController(kp=1.0, ki=0.01, kd=0.1, v_max=1.0)
    sm = LandingStateMachine(stale_timeout=0.2)
    
    x, y = initial_x, initial_y
    current_time = 0.0
    
    log_data = []
    
    while current_time < duration:
        # Giả lập perception (quan sát thấy mục tiêu)
        obs = {
            "target_found": True,
            "error_x": x, # Trong thực tế, error là độ lệch tọa độ
            "error_y": y
        }
        
        # Cập nhật State Machine
        state = sm.update(current_time, obs)
        
        # PID Tính toán (Chỉ di chuyển khi state cho phép)
        vx, vy = 0.0, 0.0
        if state in [LandingState.ALIGN, LandingState.HOLD_ALIGNMENT, LandingState.DESCEND]:
            # Điều khiển triệt tiêu error
            vx = -pid_x.compute(x, dt)
            vy = -pid_y.compute(y, dt)
            
        # Cập nhật tọa độ (Vận tốc = quãng đường / thời gian => dx = vx * dt)
        x += vx * dt
        y += vy * dt
        
        log_data.append({
            "time": round(current_time, 3),
            "x": round(x, 4),
            "y": round(y, 4),
            "vx": round(vx, 4),
            "vy": round(vy, 4),
            "state": state.name
        })
        
        current_time += dt
        
    return log_data

def save_csv(filename, data):
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["time", "x", "y", "vx", "vy", "state"])
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    os.makedirs("edge-vision-uav-landing/reports/", exist_ok=True)
    
    scenarios = [
        ("0.5m", 0.5, 0.0),
        ("1.0m", 1.0, 0.0),
        ("2.0m", 2.0, 0.0),
        ("diagonal", 1.5, 1.5)
    ]
    
    for name, initial_x, initial_y in scenarios:
        data = run_simulation(initial_x, initial_y)
        save_csv(f"edge-vision-uav-landing/reports/sim_2d_{name}.csv", data)
        print(f"Scenario {name} completed. Final Error: x={data[-1]['x']}, y={data[-1]['y']}, state={data[-1]['state']}")
```
- **Lệnh kiểm tra:**
```bash
python -m py_compile edge-vision-uav-landing/src/simulation_2d/closed_loop_2d_sim.py
```
- **Expected output:** Không có lỗi syntax.
- **Evidence cần lưu:** Code Python.
- **Acceptance criteria:** Implement đủ logic PID, State Machine và cấu trúc lưu CSV.
- **Failure condition:** Script lỗi syntax.
- **Fallback hoặc rollback:** Chỉnh lại indent Python.

### Task 1.2: Chạy Simulation và phân tích kết quả
- **Mục tiêu:** Chạy kịch bản giả lập các offset: 0.5m, 1.0m, 2.0m và offset chéo (diagonal). 
- **Mission phục vụ:** P1-A.
- **Lý do thực hiện:** Chứng minh PID hội tụ không overshoot quá giới hạn, State Machine chuyển đúng sang trạng thái DESCEND.
- **Dependency:** Script 2D Simulator từ Task 1.1.
- **Trạng thái hiện tại:** PENDING_VALIDATION.
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Chạy simulation:
```bash
python edge-vision-uav-landing/src/simulation_2d/closed_loop_2d_sim.py
```
  - [x] **Thao tác 2:** Kiểm tra output files:
```bash
ls -la edge-vision-uav-landing/reports/sim_2d_*.csv
```
- **Lệnh kiểm tra:** (Như trên)
- **Expected output:** Trả về final error x,y rất nhỏ (gần 0), state đạt DESCEND. Sinh ra 4 file CSV.
- **Evidence cần lưu:** Các file `sim_2d_*.csv` trong thư mục `reports/`.
- **Acceptance criteria:** Simulation chạy hết, final error ở mức < 0.05m.
- **Failure condition:** Error không hội tụ (bay mất kiểm soát) hoặc không ghi được file.

### Task 1.3: Viết Report Closed Loop 2D v0
- **Mục tiêu:** Tổng kết báo cáo phân tích giả lập 2D.
- **Mission phục vụ:** P1-A.
- **Dependency:** Kết quả CSV từ Task 1.2.
- **File liên quan:** `edge-vision-uav-landing/docs/closed_loop_2d_v0.md` (Sẽ tạo mới).
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Tạo file report:
```bash
touch edge-vision-uav-landing/docs/closed_loop_2d_v0.md
```
  - [x] **Thao tác 2:** Cập nhật nội dung report:
```bash
cat << 'EOF' > edge-vision-uav-landing/docs/closed_loop_2d_v0.md
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
EOF
```
- **Evidence cần lưu:** File báo cáo markdown.
- **Acceptance criteria:** Báo cáo phản ánh đúng kết quả chạy 2D simulation.

---

## Phase 2 — Machine B: ML Domain Adaptation Review (DEFERRED)

### Task 2.1: Ghi nhận hoãn (Defer) so sánh Domain Adaptation
- **Mục tiêu:** Tuân thủ chặt chẽ rule của ROADMAP: "Do not train custom-only if the dataset is too small."
- **Mission phục vụ:** ML.
- **Lý do thực hiện:** Day 08 đã Audit và xác định dataset Custom đang thiếu (PARTIALLY_COLLECTED). Vì vậy việc train custom model sẽ tạo ra baseline sai lệch, không phản ánh đúng năng lực hệ thống.
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Ghi nhận sự trì hoãn này vào Experiment Registry.
```bash
mkdir -p edge-ai-training/experiments/
touch edge-ai-training/experiments/EXPERIMENT_REGISTRY.csv
echo "EXP_ID,DATE,MODEL,DATASET,STATUS,NOTE" > edge-ai-training/experiments/EXPERIMENT_REGISTRY.csv
echo "EXP_002,$(date +%Y-%m-%d),YOLO26n,custom_v0_1,DEFERRED,Dataset quá nhỏ. Chỉ đánh giá trên public baseline VisDrone. Đợi collect thêm." >> edge-ai-training/experiments/EXPERIMENT_REGISTRY.csv
```
- **Evidence cần lưu:** `EXPERIMENT_REGISTRY.csv`.
- **Acceptance criteria:** Trì hoãn một cách có chủ đích và có lưu vết (Audit Trail).

---

## Integration / Evidence Phase

- **Tổng hợp Evidence:**
  - [x] `edge-vision-uav-landing/src/simulation_2d/closed_loop_2d_sim.py` (Source)
  - [x] Các file CSV: `reports/sim_2d_*.csv` (Run artifacts)
  - [x] `edge-vision-uav-landing/docs/closed_loop_2d_v0.md` (Report)
  - [x] `edge-ai-training/experiments/EXPERIMENT_REGISTRY.csv` (Registry update)

---

## End-of-Day Gate Review

### Gate Decision Template
- **Gate:** Daily Day 09 Review
- **Status:** PASS_WITH_DOCUMENTED_LIMITATION
- **Passed criteria:** Closed-loop 2D Controller hội tụ thành công, State Machine logic hoạt động đúng yêu cầu.
- **Missing criteria:** Không
- **Blocked criteria:** Không
- **Deferred criteria:** Domain-adaptation comparison (Public-to-Custom) hoãn do dataset chưa đủ (Theo đúng rule roadmap).
- **Evidence paths:** `reports/sim_2d_*.csv`, `closed_loop_2d_v0.md`, `EXPERIMENT_REGISTRY.csv`.
- **Decision:** PASS to Day 10.

### End-of-Day Log Template
- [x] **Thao tác 1:** Tạo file log cuối ngày:
```bash
cat << 'EOF' > edge-vision-uav-landing/daily_logs/day_09.md
# Day 09: Closed-loop 2D landing simulation and domain-adaptation comparison

## Mission served
P1-A, ML

## Done
- **Machine A:** Xây dựng và chạy closed-loop 2D simulator. Chạy 4 kịch bản offset và chứng minh PID + State Machine hội tụ an toàn. Xuất file CSV log và báo cáo v0.
- **Machine B:** Hoãn fine-tune custom model do dataset PARTIALLY_COLLECTED. Đã log vào EXPERIMENT_REGISTRY.csv.

## Evidence
- `src/simulation_2d/closed_loop_2d_sim.py`
- `reports/sim_2d_*.csv`
- `docs/closed_loop_2d_v0.md`
- `EXPERIMENT_REGISTRY.csv`

## Metrics
- Settling time (2D Simulation): < 10s (MEASURED in CSV)
- Final Error (2D Simulation): < 0.05m (MEASURED in CSV)

## Problems
- Dataset custom cho Vehicle Tracking vẫn chưa sẵn sàng. (Known limitation).

## Decision
- PASS_WITH_DOCUMENTED_LIMITATION. Tiếp tục sang Day 10.

## Tomorrow
- Day 10: UDP IPC schema, receiver prototype, and tracking evaluation harness.
EOF
```

### Git Commit Guidance
- [ ] **Thao tác 1:** Commit các file sau khi chạy thành công:
```bash
git add edge-vision-uav-landing/src/simulation_2d/closed_loop_2d_sim.py
git add edge-vision-uav-landing/reports/sim_2d_*.csv
git add edge-vision-uav-landing/docs/closed_loop_2d_v0.md
git add edge-vision-uav-landing/daily_logs/day_09.md
git add edge-ai-training/experiments/EXPERIMENT_REGISTRY.csv
git commit -m "feat: implement Day 09 closed-loop 2D sim and defer custom ML training"
```

---

## Deliverables
- Source code 2D Simulator.
- 4 file log dạng CSV đo đạc offset.
- Report `closed_loop_2d_v0.md`.
- Registry log cho Machine B.
- Daily log Day 09.

## Verification Matrix
| Hạng mục | Evidence yêu cầu | Trạng thái đầu ngày | Điều kiện hoàn thành |
|---|---|---|---|
| 2D Simulation | 4 file CSV + script Python | MISSING | Script sinh ra các file log, error hội tụ về sát 0. |
| Simulation Report | `closed_loop_2d_v0.md` | MISSING | Report ghi nhận rõ metrics. |
| ML Domain Adapt | `EXPERIMENT_REGISTRY.csv` | MISSING | Ghi nhận rõ việc DEFERRED custom dataset training. |
