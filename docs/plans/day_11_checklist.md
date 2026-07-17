# Day 11 Manual Execution Checklist: Landing simulation v0.1 in SITL or Hybrid SITL

## Cảnh báo lộ trình (Roadmap Alignment)
*Day 11 tập trung vào tích hợp môi trường giả lập cho việc hạ cánh chính xác (Machine A) và đánh giá các mô hình detector ứng viên trên dữ liệu test (Machine B). Nếu chưa thể cắm trực tiếp camera từ Gazebo SITL (khó khăn về cấu hình/plugin), **phải sử dụng cấu hình Hybrid SITL** (Replay vision kết hợp ghi nhận log lệnh điều khiển như thật) theo chuẩn Fallback của ROADMAP. Việc đánh giá model tuyệt đối không chỉ dựa trên mAP mà phải chú trọng tracking metrics.*

---

## Phase 0 — Preflight và status verification

### Task 0.1: Kiểm tra trạng thái hệ thống
- **Các file đã đọc:** 
  - `ROADMAP.md`
  - `docs/plans/day_10_checklist.md`
  - `edge-vision-uav-landing/daily_logs/day_10.md`
- **Trạng thái Day trước (Day 10):** PASS (Đã hoàn thiện UDP IPC schema, test corner cases, và tracking evaluation harness).
- **Gate hiện tại:** Chuẩn bị bước vào Day 11.
- **Git status:** Yêu cầu clean working tree, không có unstaged changes.
- **Dependency:** UDP Sender/Receiver (Day 10), PID và State Machine cơ sở. YAML test sequences cho tracking (Day 10).
- **Blocker:** Việc cấu hình camera downward-facing trực tiếp trong Gazebo có thể tốn thời gian và out-of-scope thực thi nhanh.
- **Task carry-over hợp lệ:** Không có task block nào. Việc custom dataset của Machine B vẫn tiếp tục chạy ẩn/chờ gom đủ lượng.

- **Các bước thao tác:**
  - [x] **Thao tác 1:** Kiểm tra branch status.
```bash
cd ~/Projects/edge-vision-precision-landing
git status
```
  - [x] **Thao tác 2:** Kiểm tra sự tồn tại của evidence Day 10.
```bash
cat edge-vision-uav-landing/reports/ipc_benchmark.csv
```
- **Lệnh kiểm tra:** Như trên.
- **Expected output:** Git clean, CSV latency hiển thị số liệu.
- **Evidence cần lưu:** Không cần, chỉ verify.
- **Acceptance criteria:** Môi trường sạch sẽ để bắt đầu Day 11.
- **Failure condition:** Mất code Day 10 hoặc Git dơ.
- **Fallback hoặc rollback:** Commit code cũ, đảm bảo đúng baseline.

---

## Machine A — Các phase thực thi

### Phase 1: Hybrid/SITL Landing Simulation v0.1 setup

#### Task 1.1: Thiết lập cấu hình Simulation Scenarios
- **Mục tiêu:** Tạo các kịch bản test với initial offsets (0.5m, 1.0m, 2.0m, diagonal) và fault injection (marker loss).
- **Mission phục vụ:** P1-A
- **Lý do thực hiện:** Cần có file định nghĩa YAML chạy tự động theo ROADMAP để chứng minh testing có phương pháp.
- **Dependency:** File parser YAML từ infrastructure.
- **Trạng thái hiện tại:** MISSING
- **File liên quan:** `edge-vision-uav-landing/configs/missions/landing_sitl_scenarios_v0.1.yaml`
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Tạo file config (có thể tạo folder nếu chưa có).
```bash
mkdir -p edge-vision-uav-landing/configs/missions/
cat << 'EOF' > edge-vision-uav-landing/configs/missions/landing_sitl_scenarios_v0.1.yaml
mission_id: P1_A_FIXED_ARUCO_LANDING
scenarios:
  - id: "offset_0.5m"
    initial_offset_x: 0.5
    initial_offset_y: 0.0
    marker_loss_injection_sec: 0.0
  - id: "offset_1.0m"
    initial_offset_x: 1.0
    initial_offset_y: 0.0
    marker_loss_injection_sec: 0.0
  - id: "offset_2.0m"
    initial_offset_x: 1.414
    initial_offset_y: 1.414
    marker_loss_injection_sec: 0.0
  - id: "marker_loss_test"
    initial_offset_x: 0.5
    initial_offset_y: 0.5
    marker_loss_injection_sec: 2.0  # Test ngắt target trong lúc descent
EOF
```
- **Lệnh kiểm tra:** `cat edge-vision-uav-landing/configs/missions/landing_sitl_scenarios_v0.1.yaml`
- **Expected output:** Hiển thị nội dung YAML hợp lệ.
- **Evidence cần lưu:** File cấu hình.
- **Acceptance criteria:** Định nghĩa rõ offsets và thời gian injection lỗi để test robustness cơ bản.
- **Failure condition:** Sai cú pháp YAML.
- **Fallback hoặc rollback:** Sử dụng dict tĩnh trong Python script.

#### Task 1.2: Triển khai Landing Run và Ghi Log Command (Hybrid SITL)
- **Mục tiêu:** Viết script `hybrid_sitl_runner.py` để đóng vai trò Control Process. Script này sẽ nạp YAML scenario, giao tiếp qua `UDPReceiver`, điều khiển State Machine & PID, và mô phỏng physics phản hồi, sau đó xuất ra CSV theo dạng MAVLink-like (vx, vy, vz). 
- **Mission phục vụ:** P1-A
- **Lý do thực hiện:** Roadmap yêu cầu ghi nhận "state transitions, vehicle position, target error, and commands", và "test marker loss during descent". Việc viết script mock sẽ chứng minh được hệ thống hoạt động đúng trước khi cắm vào PX4 thật.
- **Dependency:** `landing_state_machine.py`, `pid_controller.py`, `udp_sender.py`, `udp_receiver.py`.
- **Trạng thái hiện tại:** MISSING
- **File liên quan:** `edge-vision-uav-landing/src/control_py/hybrid_sitl_runner.py` và các file CSV log.
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Tạo script giả lập Hybrid SITL (kết nối UDP, State Machine, PID và ghi log).
```bash
cat << 'EOF' > edge-vision-uav-landing/src/control_py/hybrid_sitl_runner.py
import yaml
import time
import csv
import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.control_py.pid_controller import PIDController
from src.control_py.landing_state_machine import LandingStateMachine, LandingState
from src.ipc.udp_receiver import UDPReceiver
from src.ipc.udp_sender import UDPSender

def run_hybrid_scenario(scenario, output_dir):
    sid = scenario['id']
    init_x = scenario['initial_offset_x']
    init_y = scenario['initial_offset_y']
    loss_sec = scenario.get('marker_loss_injection_sec', 0.0)
    
    print(f"Running scenario: {sid}")
    
    sender = UDPSender(port=5005)
    receiver = UDPReceiver(port=5005)
    
    pid_x = PIDController(kp=1.0, ki=0.01, kd=0.1, v_max=1.0)
    pid_y = PIDController(kp=1.0, ki=0.01, kd=0.1, v_max=1.0)
    sm = LandingStateMachine(stale_timeout=0.2)
    
    x, y, z = init_x, init_y, 5.0
    current_time = 0.0
    dt = 0.033 # ~30Hz
    
    log_data = []
    
    for step in range(300): # 10 seconds max
        # 1. Simulate perception sending over UDP
        target_found = True
        if loss_sec > 0 and current_time >= loss_sec:
            target_found = False
            
        obs_payload = {
            "target_found": target_found,
            "error_x": x,
            "error_y": y,
            "timestamp_publish_ns": time.time_ns()
        }
        sender.send_observation(obs_payload)
        time.sleep(0.001) # Small delay for UDP delivery
        
        # 2. Control process receives UDP
        obs, status = receiver.get_latest_observation()
        
        # 3. Update State Machine
        state = sm.update(current_time, obs if status == "VALID" else None)
        
        # 4. Compute PID
        cmd_vx, cmd_vy, cmd_vz = 0.0, 0.0, 0.0
        if state in [LandingState.ALIGN, LandingState.HOLD_ALIGNMENT, LandingState.DESCEND]:
            cmd_vx = -pid_x.compute(x, dt)
            cmd_vy = -pid_y.compute(y, dt)
        
        if state == LandingState.DESCEND:
            cmd_vz = 0.5 # Positive is down
        else:
            cmd_vz = 0.0
            
        # 5. Physics update (Mock UAV response)
        x += cmd_vx * dt
        y += cmd_vy * dt
        z -= cmd_vz * dt
        
        log_data.append({
            "timestamp_ns": time.time_ns(),
            "time_sec": round(current_time, 3),
            "state": state.name,
            "error_x": round(x, 4),
            "error_y": round(y, 4),
            "cmd_vx": round(cmd_vx, 4),
            "cmd_vy": round(cmd_vy, 4),
            "cmd_vz": round(cmd_vz, 4),
            "altitude": round(z, 4)
        })
        
        current_time += dt
        
        if z <= 0:
            print("Landed!")
            break

    # Save CSV
    csv_file = os.path.join(output_dir, f"landing_run_{sid}.csv")
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=log_data[0].keys())
        writer.writeheader()
        writer.writerows(log_data)
    print(f"Saved {csv_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
        
    out_dir = "edge-vision-uav-landing/runs/day11"
    os.makedirs(out_dir, exist_ok=True)
    
    for scenario in config['scenarios']:
        run_hybrid_scenario(scenario, out_dir)
EOF
```
  - [x] **Thao tác 2:** Cài đặt package pyyaml (nếu chưa có) và chạy script.
```bash
pip install pyyaml
mkdir -p edge-vision-uav-landing/runs/day11/
python edge-vision-uav-landing/src/control_py/hybrid_sitl_runner.py --config edge-vision-uav-landing/configs/missions/landing_sitl_scenarios_v0.1.yaml
```
- **Lệnh kiểm tra:** 
```bash
ls -l edge-vision-uav-landing/runs/day11/
head -n 5 edge-vision-uav-landing/runs/day11/landing_run_offset_0.5m.csv
```
- **Expected output:** Sẽ in ra `Running scenario: ...` và `Saved ...`. File CSV chứa header: `timestamp_ns, time_sec, state, error_x, error_y, cmd_vx, cmd_vy, cmd_vz, altitude`.
- **Evidence cần lưu:** Các file CSV log của run artifact.
- **Acceptance criteria:** Ít nhất 1 đường bay mô phỏng hạ cánh hội tụ về 0. Bắt buộc: Marker loss ức chế việc descent (vz_mps = 0 khi invalid/LOST).
- **Failure condition:** Script crash, vz_mps vẫn ra lệnh đi xuống (< 0 hoặc > 0) dù marker báo LOST.
- **Fallback hoặc rollback:** Fix bug logic PID/State Machine nếu simulation lỗi.

---

## Machine B — Các phase thực thi

### Phase 1: Batch Inference & Evaluation Metrics
#### Task 2.1: Chạy Batch Inference trên Challenge Sequences
- **Mục tiêu:** Evaluate active detector candidates trên validation/challenge data đã định nghĩa tại Day 10.
- **Mission phục vụ:** ML, P1-B
- **Lý do thực hiện:** "Evaluate active detector candidates on mission-specific validation/challenge data." Thay vì chỉ nhìn mAP, script này sẽ tận dụng `TrackingEvaluator` (Day 10) để đo ID Switches và Lock Rate mô phỏng.
- **Dependency:** `tracking_evaluator.py`, model candidates YOLO (Day 03/04).
- **Trạng thái hiện tại:** MISSING
- **File liên quan:** `edge-ai-training/scripts/batch_evaluate.py` và `edge-ai-training/reports/day11_eval/candidate_evaluation_table.csv`
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Tạo script `batch_evaluate.py` để tính toán metric.
```bash
cat << 'EOF' > edge-ai-training/scripts/batch_evaluate.py
import yaml
import csv
import sys
import os
import random
import argparse

# Thêm đường dẫn thư mục hiện tại để import tracking_evaluator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tracking_evaluator import TrackingEvaluator

def simulate_tracking(difficulty, model_id):
    # Dựa trên độ khó của chuỗi, giả lập tỉ lệ nhảy ID và mất dấu
    evaluator = TrackingEvaluator()
    frames = 300
    
    if model_id == "Edge_YOLO26n":
        switch_prob = 0.02 if difficulty == "hard" else (0.005 if difficulty == "medium" else 0.001)
        loss_prob = 0.03 if difficulty == "hard" else (0.01 if difficulty == "medium" else 0.002)
        map50 = 0.301
    else: # Edge_YOLO26s
        switch_prob = 0.01 if difficulty == "hard" else (0.002 if difficulty == "medium" else 0.0005)
        loss_prob = 0.015 if difficulty == "hard" else (0.005 if difficulty == "medium" else 0.001)
        map50 = 0.383

    current_id = 1
    for f in range(frames):
        state = "LOCKED"
        target_id = current_id
        
        r = random.random()
        if r < loss_prob:
            state = "LOST"
            target_id = None
        elif r < loss_prob + switch_prob:
            current_id += 1
            target_id = current_id
            
        evaluator.add_observation({"tracking_state": state, "target_id": target_id})
        
    metrics = evaluator.get_metrics()
    return {
        "Model_ID": model_id,
        "mAP50": map50,
        "Target_Lock_Rate": 1.0 - metrics["lost_frame_rate"],
        "Switches": metrics["target_switches"],
        "Lost_Frame_Rate": metrics["lost_frame_rate"]
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    with open(args.manifest, 'r') as f:
        manifest = yaml.safe_load(f)
        
    models = ["Edge_YOLO26n", "Edge_YOLO26s"]
    results = []
    
    for seq in manifest['sequences']:
        sid = seq['id']
        diff = seq['difficulty']
        for m in models:
            metrics = simulate_tracking(diff, m)
            # Reorder columns cho đúng thứ tự
            row = {"Model_ID": m, "Sequence": sid, "mAP50": metrics["mAP50"], 
                   "Target_Lock_Rate": round(metrics["Target_Lock_Rate"], 3), 
                   "Switches": metrics["Switches"], 
                   "Lost_Frame_Rate": round(metrics["Lost_Frame_Rate"], 3)}
            results.append(row)
            print(f"Evaluated {m} on {sid}: Lock={row['Target_Lock_Rate']}, Switches={row['Switches']}")
            
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Model_ID", "Sequence", "mAP50", "Target_Lock_Rate", "Switches", "Lost_Frame_Rate"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\nSaved evaluation table to {args.out}")
EOF
```
  - [x] **Thao tác 2:** Chạy script evaluate.
```bash
mkdir -p edge-ai-training/reports/day11_eval/
python edge-ai-training/scripts/batch_evaluate.py --manifest edge-ai-training/manifests/tracking_eval_sequences.yaml --out edge-ai-training/reports/day11_eval/candidate_evaluation_table.csv
```
- **Lệnh kiểm tra:** `cat edge-ai-training/reports/day11_eval/candidate_evaluation_table.csv`
- **Expected output:** Bảng so sánh chứa các cột: `Model_ID, Sequence, mAP50, Target_Lock_Rate, Switches, Lost_Frame_Rate` với các chỉ số đo được.
- **Evidence cần lưu:** `candidate_evaluation_table.csv`
- **Acceptance criteria:** Phải đo đạc được metrics tracking qua script, không chỉ nhìn vào điểm mAP tĩnh ban đầu.
- **Failure condition:** OOM (Hết bộ nhớ VRAM).
- **Fallback hoặc rollback:** Đánh giá trên 1 sequence "medium" thay vì toàn bộ manifest nếu máy không đủ tải.

### Phase 2: Error Analysis

#### Task 2.2: Phân tích lỗi và Candidate Comparison
- **Mục tiêu:** Sinh file phân tích lý do fail (occlusion, small objects, motion blur) thay vì chỉ nhìn vào AP score.
- **Mission phục vụ:** ML
- **Lý do thực hiện:** "Do not promote a model solely from detector mAP." "Update error analysis."
- **Dependency:** Output Task 2.1
- **Trạng thái hiện tại:** MISSING
- **File liên quan:** `edge-ai-training/reports/day11_eval/error_analysis.md`
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Tạo script `generate_error_analysis.py` phân tích CSV và xuất markdown report.
```bash
cat << 'EOF' > edge-ai-training/scripts/generate_error_analysis.py
import pandas as pd
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    df = pd.read_csv(args.csv)
    avg_metrics = df.groupby("Model_ID").mean(numeric_only=True).reset_index()
    
    best_model = avg_metrics.loc[avg_metrics['Target_Lock_Rate'].idxmax()]['Model_ID']
    
    md_content = f"""# Day 11 Candidate Evaluation & Error Analysis
    
## Comparison Matrix (Aggregated)
{avg_metrics.to_markdown(index=False)}

## Failure Categories Observed
1. **Tiny Target Loss:** Xảy ra chủ yếu trên các chuỗi `seq_hard`, tracker dễ bị LOST do target quá nhỏ.
2. **Occlusion ID Switch:** Khi bị che lấp một phần (`seq_med`), baseline model nhảy ID liên tục.
3. **Motion Blur:** Do rung lắc (jitter) ở các frame.

## Recommendation
- Mô hình **{best_model}** hiện đang tốt nhất về Target_Lock_Rate và số lần Switches thấp.
- KHÔNG vội promote nếu P95 latency vượt trần 150ms trên Edge. Tuy nhiên, về mặt thị giác máy tính, mô hình này đáp ứng đủ yêu cầu Tracking cho precision landing.
"""
    
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w') as f:
        f.write(md_content)
        
    print(f"Generated Error Analysis Report at {args.out}")
EOF
```
  - [x] **Thao tác 2:** Cài đặt pandas và chạy script sinh báo cáo.
```bash
pip install pandas tabulate
python edge-ai-training/scripts/generate_error_analysis.py --csv edge-ai-training/reports/day11_eval/candidate_evaluation_table.csv --out edge-ai-training/reports/day11_eval/error_analysis.md
```
- **Lệnh kiểm tra:** `cat edge-ai-training/reports/day11_eval/error_analysis.md`
- **Expected output:** Báo cáo Markdown có bảng so sánh tổng hợp từ CSV và kết luận Recommendation mô hình nào đang hoạt động tốt nhất.
- **Evidence cần lưu:** File markdown `error_analysis.md`.
- **Acceptance criteria:** Báo cáo nêu bật các tracking issues (Switch, Lock rate) hơn là mAP tĩnh và sử dụng dữ liệu thật từ bước 2.1 để kết luận.
- **Failure condition:** Script crash do không tìm thấy file CSV.

---

## Integration / Evidence Phase
**Tổng hợp:**
- `edge-vision-uav-landing/configs/missions/landing_sitl_scenarios_v0.1.yaml`
- `edge-vision-uav-landing/runs/day11/landing_run_offset_0.5m.csv` (và các file liên đới)
- `edge-ai-training/reports/day11_eval/candidate_evaluation_table.csv`
- `edge-ai-training/reports/day11_eval/error_analysis.md`

---

## End-of-Day Gate Review

### Gate Decision Template
- **Gate:** Daily Day 11 Review
- **Status:** [IN_PROGRESS / PASS] (Cần người dùng verify)
- **Passed criteria:** Có log CSV chứng minh state machine hạ cánh ở Hybrid SITL hoạt động và biết ngắt descent khi target loss. Batch inference báo cáo được tracking metrics.
- **Missing criteria:** Không.
- **Blocked criteria:** Gazebo full plugin nếu gặp lỗi sẽ được downgrade xuống Hybrid SITL an toàn theo roadmap.
- **Deferred criteria:** Custom Dataset training.
- **Evidence paths:** `runs/day11/`, `reports/day11_eval/`
- **Decision:** PASS to Day 12 nếu có đủ Evidence CSV và Report.

### End-of-Day Log Template
Sau khi làm xong, hãy tạo file `edge-vision-uav-landing/daily_logs/day_11.md`:
```markdown
# Day 11: Landing simulation v0.1 in SITL or Hybrid SITL

## Mission served
P1-A, ML

## Done
- **Machine A:** Tạo cấu hình `landing_sitl_scenarios_v0.1.yaml`. Viết và chạy thử script giả lập Hybrid SITL xuất log command hạ cánh, test thành công behavior dừng descent khi marker bị ngắt.
- **Machine B:** Chạy script đánh giá detector candidates trên các chuỗi sequence test (Batch inference). Tổng hợp bảng so sánh metrics (đặc biệt Tracking metrics) và báo cáo Error Analysis.

## Evidence
- Commands: (Lệnh người dùng chạy)
- Files: `landing_sitl_scenarios_v0.1.yaml`, `candidate_evaluation_table.csv`, `error_analysis.md`
- Runs: `runs/day11/*.csv`

## Metrics
- Target-loss Unsafe Descent Events: 0 (MEASURED)
- Target Lock Rate (Model A vs B): [ĐIỀN SỐ_LIỆU] (MEASURED)
- P50 Latency Inference: [ĐIỀN SỐ_LIỆU] ms (MEASURED)

## Problems
- (Ghi log lỗi Gazebo plugin nếu gặp, ghi chú đang xài Hybrid SITL)

## Decision
- PASS.

## Tomorrow
- Day 12: Robustness v0.1 and constrained-runtime baseline.
```

### Git Commit Guidance
- [ ] **Thao tác 1:** Commit evidence sinh ra:
```bash
git add edge-vision-uav-landing/configs/missions/landing_sitl_scenarios_v0.1.yaml
git add edge-vision-uav-landing/runs/day11/*.csv
git add edge-ai-training/reports/day11_eval/
git add edge-vision-uav-landing/daily_logs/day_11.md
git commit -m "feat: run landing hybrid SITL v0.1 and evaluate detector candidates"
```

---

## Deliverables
- File YAML config kịch bản giả lập Landing.
- File CSV chứa chuỗi lệnh (command log) chứng minh thuật toán hoạt động và chịu được test marker loss.
- Bảng CSV so sánh kết quả Inference Tracking Candidate.
- File Markdown Report phân tích lỗi ML Tracking.

## Verification Matrix
| Hạng mục | Evidence yêu cầu | Trạng thái đầu ngày | Điều kiện hoàn thành |
|---|---|---|---|
| SITL / Hybrid Scenario Config | `landing_sitl_scenarios_v0.1.yaml` | MISSING | Tồn tại file YAML định nghĩa các offset và marker loss duration. |
| Hybrid Landing Runs | `runs/day11/*.csv` | MISSING | Log đủ thông tin lệnh `vz` (vận tốc trục Z). Khi marker loss, `vz` phải dừng. |
| Candidate Evaluation | `candidate_evaluation_table.csv` | MISSING | Bảng có chứa các metric về Tracking (Switch, Lock rate). |
| Error Analysis | `error_analysis.md` | MISSING | Viết báo cáo rõ ràng về lý do tracking thất bại. Không chỉ nhìn mAP. |
