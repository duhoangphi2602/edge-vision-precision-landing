# Day 12 Manual Execution Checklist: Robustness v0.1 and constrained-runtime baseline

## Cảnh báo lộ trình (Roadmap Alignment)
*Day 12 chia làm 2 nhiệm vụ song song trên 2 máy: Machine A tập trung vào đo lường độ bền của hệ thống (system degradation, failsafe behavior) dưới các điều kiện lỗi và giới hạn CPU. Machine B tập trung vào benchmark các định dạng runtime (ONNX/TFLite/TensorRT) trên thiết bị nhúng giả lập. Fallback policy: Nếu runtime nào export lỗi, hãy giữ lại log lỗi và sử dụng ONNX làm baseline bắt buộc.*

---

## Phase 0 — Preflight và status verification

### Task 0.1: Kiểm tra trạng thái hệ thống
- **Các file đã đọc:** 
  - `ROADMAP.md`
  - `edge-vision-uav-landing/daily_logs/day_11.md`
- **Trạng thái Day trước (Day 11):** VERIFIED (PASS)
- **Gate hiện tại:** Bắt đầu Day 12.
- **Git status:** Clean (Đã được commit vào cuối Day 11).
- **Dependency:** `hybrid_sitl_runner.py` từ Day 11, các file weights `yolo26n.pt` / `yolo26s.pt`.
- **Blocker:** Không.
- **Task carry-over hợp lệ:** Không.

---

## Machine A — Các phase thực thi

### Phase 1: Robustness Setup & Fault Injection

#### Task 1.1: Tạo kịch bản nhiễu loạn (Robustness Scenarios YAML)
- **Mục tiêu:** Định nghĩa các kịch bản test có chứa noise, blur, occlusion, packet delay, frame drop.
- **Mission phục vụ:** P1-A
- **Lý do thực hiện:** Roadmap yêu cầu "Run replay and SITL/hybrid tests with noise, blur, occlusion, delay, frame drop, and CPU restriction".
- **Dependency:** Script đọc YAML từ cấu trúc hạ tầng hiện tại.
- **Trạng thái hiện tại:** MISSING
- **File liên quan:** `edge-vision-uav-landing/configs/missions/robustness_sitl_scenarios_v0.1.yaml`
- **Các bước thao tác:**
  - Chạy lệnh sau để tạo file YAML định nghĩa lỗi:
```bash
cat << 'EOF' > edge-vision-uav-landing/configs/missions/robustness_sitl_scenarios_v0.1.yaml
mission_id: P1_A_ROBUSTNESS_TEST
scenarios:
  - id: "fault_delay_100ms"
    initial_offset_x: 1.0
    initial_offset_y: 1.0
    network_delay_sec: 0.1
    frame_drop_rate: 0.0
    cpu_restriction_hz: 30
  - id: "fault_frame_drop_50"
    initial_offset_x: 1.0
    initial_offset_y: 1.0
    network_delay_sec: 0.01
    frame_drop_rate: 0.5
    cpu_restriction_hz: 30
  - id: "fault_cpu_throttle_10hz"
    initial_offset_x: 1.0
    initial_offset_y: 1.0
    network_delay_sec: 0.01
    frame_drop_rate: 0.0
    cpu_restriction_hz: 10
EOF
```
- **Lệnh kiểm tra:** `cat edge-vision-uav-landing/configs/missions/robustness_sitl_scenarios_v0.1.yaml`
- **Expected output:** YAML hiển thị chính xác các scenario id và parameters.
- **Evidence cần lưu:** File `robustness_sitl_scenarios_v0.1.yaml`.
- **Acceptance criteria:** YAML file tồn tại và đúng syntax.
- **Failure condition:** Command lỗi bash hoặc permission denied.
- **Fallback hoặc rollback:** Tạo file thủ công.

#### Task 1.2: Nâng cấp Hybrid SITL Runner để bơm lỗi (Fault Injector)
- **Mục tiêu:** Viết logic giả lập delay, drop packet và giả lập CPU bottleneck vào `hybrid_sitl_runner.py` (hoặc tạo file mới `robust_hybrid_runner.py`).
- **Mission phục vụ:** P1-A
- **Lý do thực hiện:** Cần giả lập môi trường thực tế để ép controller bộc lộ điểm yếu (failsafe reaction, stale rejections).
- **Dependency:** Task 1.1
- **Trạng thái hiện tại:** MISSING
- **File liên quan:** `edge-vision-uav-landing/src/control_py/robust_hybrid_runner.py`
- **Các bước thao tác:**
  - Viết script Python mô phỏng nhận packet bị trễ, drop ngẫu nhiên theo xác suất, và Sleep() để giả lập CPU chạy chậm. Chạy lệnh sau để tạo script:
```bash
cat << 'EOF' > edge-vision-uav-landing/src/control_py/robust_hybrid_runner.py
import yaml
import time
import csv
import sys
import os
import argparse
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.control_py.pid_controller import PIDController
from src.control_py.landing_state_machine import LandingStateMachine, LandingState
from src.ipc.udp_receiver import UDPReceiver
from src.ipc.udp_sender import UDPSender

def run_robust_scenario(scenario, output_dir):
    sid = scenario['id']
    init_x = scenario['initial_offset_x']
    init_y = scenario['initial_offset_y']
    net_delay = scenario.get('network_delay_sec', 0.0)
    frame_drop = scenario.get('frame_drop_rate', 0.0)
    cpu_hz = scenario.get('cpu_restriction_hz', 30.0)
    
    print(f"Running scenario: {sid}")
    
    sender = UDPSender(port=5006)
    receiver = UDPReceiver(port=5006)
    
    pid_x = PIDController(kp=1.0, ki=0.01, kd=0.1, v_max=1.0)
    pid_y = PIDController(kp=1.0, ki=0.01, kd=0.1, v_max=1.0)
    sm = LandingStateMachine(stale_timeout=0.2)
    
    x, y, z = init_x, init_y, 5.0
    current_time = 0.0
    dt = 1.0 / cpu_hz
    
    log_data = []
    
    for step in range(int(10.0 / dt)): # 10 seconds max
        target_found = True
            
        # Inject Frame Drop (mất gói tin)
        if random.random() >= frame_drop:
            obs_payload = {
                "target_found": target_found,
                "error_x": x,
                "error_y": y,
                "timestamp_publish_ns": time.time_ns()
            }
            sender.send_observation(obs_payload)
            
        # Inject Network Delay
        time.sleep(net_delay)
        
        # Nhận UDP
        obs, status = receiver.get_latest_observation()
        
        # Inject CPU Throttle (Chạy chậm)
        time.sleep(dt)
        current_time += dt
        
        # Cập nhật State Machine
        state = sm.update(current_time, obs if status == "VALID" else None)
        
        cmd_vx, cmd_vy, cmd_vz = 0.0, 0.0, 0.0
        if state in [LandingState.ALIGN, LandingState.HOLD_ALIGNMENT, LandingState.DESCEND]:
            cmd_vx = -pid_x.compute(x, dt)
            cmd_vy = -pid_y.compute(y, dt)
        if state == LandingState.DESCEND:
            cmd_vz = 0.5 
            
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
        
        if z <= 0:
            print("Landed!")
            break

    csv_file = os.path.join(output_dir, f"robustness_run_{sid}.csv")
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
        
    out_dir = "edge-vision-uav-landing/runs/day12"
    os.makedirs(out_dir, exist_ok=True)
    
    for scenario in config['scenarios']:
        run_robust_scenario(scenario, out_dir)
EOF
```
  - Chạy thử script:
```bash
python edge-vision-uav-landing/src/control_py/robust_hybrid_runner.py --config edge-vision-uav-landing/configs/missions/robustness_sitl_scenarios_v0.1.yaml
```
- **Lệnh kiểm tra:** `ls -l edge-vision-uav-landing/runs/day12/`
- **Expected output:** Các file CSV log tương ứng với mỗi scenario được tạo ra (chứa cột đo latency, state).
- **Evidence cần lưu:** CSV log files.
- **Acceptance criteria:** Log CSV chứa đầy đủ metrics chứng minh hệ thống phản ứng với các mức độ lỗi khác nhau. Controller không được crash.
- **Failure condition:** Script crash khi CPU throttle.
- **Fallback hoặc rollback:** Chỉ test `network_delay_sec` nếu mô phỏng CPU gặp khó khăn phức tạp.

---

## Machine B — Các phase thực thi

### Phase 2: Runtime Optimization & Benchmarking

#### Task 2.1: Export YOLO models (ONNX Runtime Baseline)
- **Mục tiêu:** Chuyển đổi file trọng số `.pt` của YOLO sang `.onnx`. Cố gắng export thêm TFLite/TensorRT nếu hệ thống cho phép.
- **Mission phục vụ:** ML, P1-B
- **Lý do thực hiện:** Roadmap yêu cầu "Benchmark runtime candidates under controlled conditions", "Export YOLO models to ONNX/TFLite/TensorRT". ONNX là mandatory baseline.
- **Dependency:** Các file `best.pt` từ Day 11. Thư viện `ultralytics`.
- **Trạng thái hiện tại:** MISSING
- **File liên quan:** `edge-ai-training/models/onnx/`
- **Các bước thao tác:**
  - Chạy lệnh export thông qua CLI của YOLO:
```bash
mkdir -p edge-ai-training/models/optimized/
yolo export model=edge-ai-training/experiments/TRN_001_visdrone_yolo26n_640/weights/best.pt format=onnx simplify=True
yolo export model=edge-ai-training/experiments/TRN_003_visdrone_yolo26s_640/weights/best.pt format=onnx simplify=True
# Di chuyển file onnx vừa tạo về thư mục optimized
mv edge-ai-training/experiments/TRN_001_visdrone_yolo26n_640/weights/best.onnx edge-ai-training/models/optimized/yolo26n_640.onnx
mv edge-ai-training/experiments/TRN_003_visdrone_yolo26s_640/weights/best.onnx edge-ai-training/models/optimized/yolo26s_640.onnx
```
- **Lệnh kiểm tra:** `ls -l edge-ai-training/models/optimized/*.onnx`
- **Expected output:** 2 file `.onnx` xuất hiện với dung lượng tương đương hoặc nhẹ hơn file `.pt`.
- **Evidence cần lưu:** File `.onnx`.
- **Acceptance criteria:** Xuất thành công định dạng ONNX.
- **Failure condition:** Lỗi `onnx` hoặc thư viện chưa được cài (`pip install onnx onnxruntime`).
- **Fallback hoặc rollback:** Fallback policy: Bắt buộc dùng ONNX. Nếu TFLite/TensorRT lỗi, bỏ qua và giữ nguyên ONNX làm baseline.

#### Task 2.2: Benchmark Inference Latency
- **Mục tiêu:** Đo đạc chính xác P50, P95 latency của ONNX runtime (và PyTorch baseline để so sánh).
- **Mission phục vụ:** ML, P1-B
- **Lý do thực hiện:** Roadmap yêu cầu đo "P50/P95 latency" để đảm bảo khả năng tracking real-time ở Edge.
- **Dependency:** Task 2.1
- **Trạng thái hiện tại:** MISSING
- **File liên quan:** `edge-ai-training/reports/day12/runtime_benchmark.csv`
  - Tạo script Python đo lường P50 và P95 Latency và xuất ra CSV bằng lệnh sau:
```bash
mkdir -p edge-ai-training/reports/day12/
cat << 'EOF' > edge-ai-training/scripts/benchmark_latency.py
import time
import numpy as np
import csv
import os
import argparse
from ultralytics import YOLO
import torch

def benchmark_model(model_path, iterations=100):
    print(f"Loading {model_path}...")
    model = YOLO(model_path, task='detect')
    dummy_input = torch.zeros(1, 3, 640, 640)
    
    # Warmup
    for _ in range(10):
        model(dummy_input, verbose=False)
        
    latencies = []
    print("Running benchmark...")
    for _ in range(iterations):
        start = time.time()
        model(dummy_input, verbose=False)
        end = time.time()
        latencies.append((end - start) * 1000.0) # convert to ms
        
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    
    return round(p50, 2), round(p95, 2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    models_to_test = [
        "edge-ai-training/experiments/TRN_001_visdrone_yolo26n_640/weights/best.pt",
        "edge-ai-training/models/optimized/yolo26n_640.onnx",
        "edge-ai-training/experiments/TRN_003_visdrone_yolo26s_640/weights/best.pt",
        "edge-ai-training/models/optimized/yolo26s_640.onnx"
    ]
    
    results = []
    for path in models_to_test:
        if os.path.exists(path):
            p50, p95 = benchmark_model(path)
            model_name = os.path.basename(path)
            model_type = "ONNX" if path.endswith(".onnx") else "PyTorch"
            size = "YOLO26s" if "26s" in path else "YOLO26n"
            results.append({
                "Model": size,
                "Format": model_type,
                "P50_Latency_ms": p50,
                "P95_Latency_ms": p95
            })
            print(f"{size} ({model_type}): P50={p50}ms, P95={p95}ms")
            
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Model", "Format", "P50_Latency_ms", "P95_Latency_ms"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved benchmark to {args.out}")
EOF
```
  - Chạy thử script:
```bash
python edge-ai-training/scripts/benchmark_latency.py --out edge-ai-training/reports/day12/runtime_benchmark.csv
```
- **Lệnh kiểm tra:** `cat edge-ai-training/reports/day12/runtime_benchmark.csv`
- **Expected output:** Bảng so sánh tốc độ xử lý (FPS / Latency ms) giữa bản `.pt` và bản `.onnx`.
- **Evidence cần lưu:** File `runtime_benchmark.csv`.
- **Acceptance criteria:** Latency phải được đo lường (MEASURED). Mục tiêu engineering là <100ms.
- **Failure condition:** Quá trình benchmark bị OOM hoặc treo.
- **Fallback hoặc rollback:** Benchmark trên lượng ảnh nhỏ hơn.

---

## Integration / Evidence Phase
**Tổng hợp:**
- test: Chạy SITL với fault injection.
- benchmark: Lấy latency ONNX/PyTorch.
- report: Viết báo cáo `robustness_v0_1.md`.
- run artifact: Các file CSV từ `runs/day12/`.
- model: Các file `.onnx` trong thư mục optimized.

#### Task 3.1: Tổng hợp Robustness & Latency Report
- **Mục tiêu:** Viết báo cáo `robustness_v0_1.md` theo yêu cầu ROADMAP.
  - Tạo script Python tổng hợp báo cáo bằng lệnh sau:
```bash
cat << 'EOF' > edge-vision-uav-landing/src/control_py/generate_robustness_report.py
import pandas as pd
import os
import argparse

def generate_report(runs_dir, benchmark_csv, out_file):
    report = "# Day 12: Robustness v0.1 & Latency Report\n\n"
    
    report += "## 1. Latency Benchmark (ONNX vs PyTorch)\n"
    if os.path.exists(benchmark_csv):
        df_bench = pd.read_csv(benchmark_csv)
        report += df_bench.to_markdown(index=False) + "\n\n"
        
        onnx_n = df_bench[(df_bench['Model'] == 'YOLO26n') & (df_bench['Format'] == 'ONNX')]
        if not onnx_n.empty:
            p50 = onnx_n.iloc[0]['P50_Latency_ms']
            if p50 < 100:
                report += f"**Conclusion:** YOLO26n ONNX đạt yêu cầu realtime với P50 = {p50}ms (<100ms).\n\n"
            else:
                report += f"**Conclusion:** YOLO26n ONNX chưa đạt yêu cầu realtime (P50 = {p50}ms).\n\n"
    else:
        report += "Benchmark data not found.\n\n"

    report += "## 2. Controller Failsafe Evaluation (Hybrid SITL)\n"
    for file in os.listdir(runs_dir):
        if file.startswith("robustness_run_") and file.endswith(".csv"):
            df_run = pd.read_csv(os.path.join(runs_dir, file))
            scenario_name = file.replace("robustness_run_", "").replace(".csv", "")
            
            # Kiểm tra xem UAV có bị đâm (descend khi không an toàn) hay không
            # Rule: Không được DESCEND nếu Target không tìm thấy liên tục hoặc quá Stale
            unsafe_descends = df_run[(df_run['state'] == 'DESCEND') & (df_run['error_x'] > 0.5)] # Giả định đơn giản
            
            report += f"### Scenario: {scenario_name}\n"
            report += f"- Total steps simulated: {len(df_run)}\n"
            report += f"- Final Altitude: {df_run.iloc[-1]['altitude']}m\n"
            report += f"- Failsafe Triggered (HOLD/SEARCH state): {'Yes' if 'HOLD_ALIGNMENT' in df_run['state'].values or 'SEARCH' in df_run['state'].values else 'No'}\n"
            report += "\n"

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w') as f:
        f.write(report)
    print(f"Generated {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs_dir", required=True)
    parser.add_argument("--benchmark_csv", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    generate_report(args.runs_dir, args.benchmark_csv, args.out)
EOF
```
  - Chạy script tổng hợp báo cáo:
```bash
python edge-vision-uav-landing/src/control_py/generate_robustness_report.py \
  --runs_dir edge-vision-uav-landing/runs/day12/ \
  --benchmark_csv edge-ai-training/reports/day12/runtime_benchmark.csv \
  --out edge-vision-uav-landing/reports/robustness_v0_1.md
```
- **Nội dung bắt buộc:** Phải đề cập khả năng phục hồi khi network delay 100ms và CPU drop 10Hz; tốc độ P50/P95 của ONNX model.

---

## Deliverables
- `edge-vision-uav-landing/configs/missions/robustness_sitl_scenarios_v0.1.yaml`
- `edge-vision-uav-landing/runs/day12/*.csv`
- `edge-ai-training/models/optimized/*.onnx`
- `edge-ai-training/reports/day12/runtime_benchmark.csv`
- `edge-vision-uav-landing/reports/robustness_v0_1.md`
- `edge-vision-uav-landing/daily_logs/day_12.md`

## Verification Matrix
| Hạng mục | Evidence yêu cầu | Trạng thái đầu ngày | Điều kiện hoàn thành |
|---|---|---|---|
| Robustness Scenarios | File YAML | MISSING | Chứa tham số delay, frame drop, cpu limit |
| SITL Log (Fault injected) | `runs/day12/*.csv` | MISSING | Log chứng minh system không crash khi bị nhiễu |
| Optimized Models | `*.onnx` files | MISSING | File được tạo hợp lệ, test pass |
| Latency Benchmark | `runtime_benchmark.csv` | MISSING | P50/P95 đo bằng mili-giây (MEASURED) |
| Báo cáo Robustness | `robustness_v0_1.md` | MISSING | Đánh giá failsafe reaction và recovery |

---

## End-of-Day Gate Review

### Gate Decision Template
- **Gate:** Daily Day 12 Review
- **Status:** [IN_PROGRESS / PASS / FAIL]
- **Passed criteria:** Báo cáo `robustness_v0_1.md` chứng minh controller có khả năng xử lý fault (stale rejections, failsafe) và ONNX runtime được benchmark.
- **Missing criteria:** Trống
- **Blocked criteria:** Trống
- **Deferred criteria:** Trống
- **Evidence paths:** `runs/day12/`, `reports/robustness_v0_1.md`, `models/optimized/`
- **Decision:** [Chờ đánh giá]

### End-of-Day Log Template
Sau khi làm xong, hãy tạo file `edge-vision-uav-landing/daily_logs/day_12.md`:
```markdown
# Day 12: Robustness v0.1 and constrained-runtime baseline

## Mission served
P1-A, P1-B, ML

## Done
- **Machine A:** Cập nhật Hybrid SITL với fault injection (network delay, packet drop, CPU throttle). Chạy các kịch bản nhiễu để verify failsafe reaction.
- **Machine B:** Export YOLO26n và YOLO26s sang định dạng ONNX. Chạy benchmark đo tốc độ inference latency (P50/P95). Tổng hợp báo cáo Robustness.

## Evidence
- Files: `robustness_sitl_scenarios_v0.1.yaml`, `runtime_benchmark.csv`, `robustness_v0_1.md`
- Runs: `runs/day12/*.csv`
- Models: `models/optimized/yolo26n_640.onnx`, `yolo26s_640.onnx`

## Metrics
- P50 Latency (ONNX): [ĐIỀN SỐ_LIỆU] ms (MEASURED)
- P95 Latency (ONNX): [ĐIỀN SỐ_LIỆU] ms (MEASURED)
- Stale packet rejection rate (tại 100ms delay): [ĐIỀN SỐ_LIỆU]% (MEASURED)

## Problems
- (Ghi nhận nếu model bị suy giảm tốc độ hoặc Controller bị fail dưới 10Hz CPU)

## Decision
- PASS.

## Tomorrow
- Day 13: Vehicle tracking mode, ONNX integration, and challenge evaluation.
```

### Git Commit Guidance
- Chỉ thực hiện commit sau khi hoàn thành toàn bộ Phase.
```bash
git add edge-vision-uav-landing/configs/missions/robustness_sitl_scenarios_v0.1.yaml
git add edge-vision-uav-landing/runs/day12/
git add edge-ai-training/reports/day12/runtime_benchmark.csv
git add edge-vision-uav-landing/reports/robustness_v0_1.md
git add edge-vision-uav-landing/daily_logs/day_12.md
git commit -m "test: implement fault injection simulation and export ONNX baseline"
```
*(Lưu ý: TRÁNH commit các file weights `.onnx` nếu kích thước quá lớn, nên bỏ vào .gitignore)*
