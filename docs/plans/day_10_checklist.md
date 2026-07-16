# Day 10 Manual Execution Checklist: UDP IPC schema, receiver prototype, and tracking evaluation harness

## Cảnh báo lộ trình (Roadmap Alignment)
*Day 10 tập trung vào việc thiết lập giao thức giao tiếp chuẩn (UDP IPC) giữa module Perception và Control (Machine A), và xây dựng công cụ đánh giá tracking (Evaluation Harness) với nhiều chuỗi video cho Machine B. Phần ML training trên dataset custom vẫn tiếp tục bị DEFERRED theo quy định từ Day 09 cho đến khi dataset đủ số lượng.*

---

## Phase 0 — Preflight và status verification

### Task 0.1: Kiểm tra trạng thái hệ thống
- **Mục tiêu:** Xác minh trạng thái của Day 09, đảm bảo Git branch sạch trước khi bắt đầu Day 10.
- **Lý do (💡 Giải thích chuyên sâu):** Phải đảm bảo logic PID và State Machine từ Day 09 đã được commit để không mất code khi tích hợp IPC.
- **Dependency:** Code simulation 2D (`closed_loop_2d_sim.py`) và log (`day_09.md`).
- **Trạng thái Day trước (Day 09):** PASS_WITH_DOCUMENTED_LIMITATION.
- **Gate hiện tại:** Daily Day 09 Review đã PASS.
- **Blocker / Fallback:** 
  - **Blocker:** Dataset cho custom model vẫn đang thiếu.
  - **Fallback:** Tiếp tục thiết lập Evaluation Harness sử dụng public test sequences.
- **Task carry-over hợp lệ:** Không có task block nào ngăn cản UDP IPC và Evaluation Harness.
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Kiểm tra trạng thái Git.
```bash
cd ~/Projects/edge-vision-precision-landing
git status
```
  - [x] **Thao tác 2:** Kiểm tra existence của báo cáo Day 09.
```bash
cat edge-vision-uav-landing/docs/closed_loop_2d_v0.md
```
- **Lệnh kiểm tra:** (Như trên)
- **Expected output:** Git working tree clean, file báo cáo Day 09 hiển thị kết quả đo lường 2D sim.
- **Evidence cần lưu:** Không cần.
- **Acceptance criteria:** Bắt đầu ngày mới với branch sạch.
- **Failure condition:** Có unstaged changes hoặc missing reports.
- **Fallback hoặc rollback:** Commit code Day 09.

---

## Phase 1 — Machine A: UDP IPC Schema & Implementation

### Task 1.1: Định nghĩa Interface Contract
- **Mục tiêu:** Cập nhật schema v1 vào tài liệu chuẩn `INTERFACE_CONTRACTS.md`.
- **Mission phục vụ:** P1-A, INFRA.
- **Lý do thực hiện:** Đảm bảo có một contract rõ ràng cho message truyền qua UDP giữa Perception và Control, bao gồm version, timestamp, sequence, và heartbeat.
- **Trạng thái hiện tại:** MISSING.
- **File liên quan:** `docs/INTERFACE_CONTRACTS.md` (Sẽ tạo mới/cập nhật).
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Viết file contract.
```bash
mkdir -p docs/
cat << 'EOF' > docs/INTERFACE_CONTRACTS.md
# Interface Contracts

## Observation Schema v1 (Perception to Control)
**Protocol:** UDP
**Format:** JSON (string payload)

```json
{
  "schema_version": "1.0",
  "mission_id": "P1_A_FIXED_ARUCO_LANDING",
  "timestamp_capture_ns": 1680000000000000000,
  "timestamp_publish_ns": 1680000000050000000,
  "sequence_id": 1234,
  "frame_id": 1234,
  "source_type": "gazebo",
  "target_found": true,
  "marker_dictionary": "DICT_4X4_50",
  "marker_id": 0,
  "center_px": {"x": 320.0, "y": 240.0},
  "error_px": {"x": 0.0, "y": 0.0},
  "normalized_error": {"x": 0.0, "y": 0.0},
  "pose_valid": true,
  "translation_camera_m": {"x": 0.0, "y": 0.0, "z": 5.0},
  "rotation_rvec": [0.0, 0.0, 0.0],
  "detection_latency_ms": 15.5
}
```

## Control Rules
- Control node MUST reject malformed packets.
- Control node MUST reject stale packets (timeout configurable, default 200ms).
- Control node MUST handle out-of-order packets (drop if sequence_id < last_processed).
EOF
```
- **Expected output:** File được tạo thành công.
- **Acceptance criteria:** Document phản ánh đầy đủ observation schema v1 từ ROADMAP.

### Task 1.2: Implement UDP Sender and Receiver
- **Mục tiêu:** Viết code Python cho Sender và Receiver hỗ trợ latest-observation bounded-queue.
- **Mission phục vụ:** P1-A.
- **Trạng thái hiện tại:** MISSING.
- **File liên quan:** `edge-vision-uav-landing/src/ipc/udp_sender.py`, `edge-vision-uav-landing/src/ipc/udp_receiver.py`.
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Tạo UDP modules.
```bash
mkdir -p edge-vision-uav-landing/src/ipc/
touch edge-vision-uav-landing/src/ipc/__init__.py
```
  - [x] **Thao tác 2:** Cập nhật `udp_sender.py`.
```bash
cat << 'EOF' > edge-vision-uav-landing/src/ipc/udp_sender.py
import socket
import json
import time

class UDPSender:
    def __init__(self, ip="127.0.0.1", port=5000):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence_id = 0

    def send_observation(self, obs_data):
        self.sequence_id += 1
        obs_data["sequence_id"] = self.sequence_id
        obs_data["schema_version"] = "1.0"
        if "timestamp_publish_ns" not in obs_data:
            obs_data["timestamp_publish_ns"] = time.time_ns()
        
        payload = json.dumps(obs_data).encode('utf-8')
        self.sock.sendto(payload, (self.ip, self.port))
EOF
```
  - [x] **Thao tác 3:** Cập nhật `udp_receiver.py`.
```bash
cat << 'EOF' > edge-vision-uav-landing/src/ipc/udp_receiver.py
import socket
import json
import time

class UDPReceiver:
    def __init__(self, ip="127.0.0.1", port=5000, stale_threshold_s=0.2):
        self.ip = ip
        self.port = port
        self.stale_threshold_ns = int(stale_threshold_s * 1e9)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.sock.setblocking(False)
        self.last_seq = -1

    def get_latest_observation(self):
        latest_data = None
        # Drain the buffer for latest observation (bounded queue behavior essentially dropping older packets in OS buffer)
        while True:
            try:
                data, addr = self.sock.recvfrom(4096)
                latest_data = data
            except BlockingIOError:
                break
            except Exception as e:
                break
        
        if not latest_data:
            return None, "NO_DATA"
            
        try:
            obs = json.loads(latest_data.decode('utf-8'))
        except json.JSONDecodeError:
            return None, "MALFORMED"
            
        if "schema_version" not in obs or "sequence_id" not in obs:
            return None, "MALFORMED"
            
        # Out of order check
        if obs["sequence_id"] <= self.last_seq:
            return None, "OUT_OF_ORDER"
            
        self.last_seq = obs["sequence_id"]
        
        # Stale check
        now_ns = time.time_ns()
        publish_time = obs.get("timestamp_publish_ns", 0)
        if (now_ns - publish_time) > self.stale_threshold_ns:
            return obs, "STALE"
            
        return obs, "VALID"
EOF
```
- **Lệnh kiểm tra:** `python -m py_compile edge-vision-uav-landing/src/ipc/udp_sender.py edge-vision-uav-landing/src/ipc/udp_receiver.py`
- **Expected output:** Không có lỗi syntax.
- **Acceptance criteria:** Sender và Receiver hỗ trợ latest-observation, bắt lỗi out-of-order, malformed.

### Task 1.3: Contract Tests và Benchmarking
- **Mục tiêu:** Kiểm tra các corner cases (malformed, duplicate, out-of-order, stale) và đo P50/P95 IPC latency.
- **Mission phục vụ:** P1-A.
- **Trạng thái hiện tại:** MISSING.
- **File liên quan:** `edge-vision-uav-landing/src/ipc/test_udp_ipc.py`, `edge-vision-uav-landing/reports/ipc_benchmark.csv`.
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Viết script test & benchmark.
```bash
cat << 'EOF' > edge-vision-uav-landing/src/ipc/test_udp_ipc.py
import time
import json
import socket
import csv
import numpy as np
from udp_sender import UDPSender
from udp_receiver import UDPReceiver

def test_corner_cases():
    receiver = UDPReceiver(port=5001)
    sender = UDPSender(port=5001)
    
    # 1. Normal
    sender.send_observation({"data": "valid"})
    time.sleep(0.01)
    obs, status = receiver.get_latest_observation()
    assert status == "VALID", f"Expected VALID, got {status}"
    
    # 2. Out of order (send seq 1 manually after normal send which bumped seq)
    old_obs = {"sequence_id": 1, "schema_version": "1.0", "timestamp_publish_ns": time.time_ns()}
    sender.sock.sendto(json.dumps(old_obs).encode(), ("127.0.0.1", 5001))
    time.sleep(0.01)
    obs, status = receiver.get_latest_observation()
    assert status == "OUT_OF_ORDER", f"Expected OUT_OF_ORDER, got {status}"
    
    # 3. Malformed
    sender.sock.sendto(b"malformed_string_not_json", ("127.0.0.1", 5001))
    time.sleep(0.01)
    obs, status = receiver.get_latest_observation()
    assert status == "MALFORMED", f"Expected MALFORMED, got {status}"
    
    # 4. Stale
    stale_obs = {"schema_version": "1.0", "sequence_id": 100, "timestamp_publish_ns": time.time_ns() - int(0.3 * 1e9)}
    sender.sock.sendto(json.dumps(stale_obs).encode(), ("127.0.0.1", 5001))
    time.sleep(0.01)
    obs, status = receiver.get_latest_observation()
    assert status == "STALE", f"Expected STALE, got {status}"

    print("All corner case tests passed.")

def benchmark_ipc():
    receiver = UDPReceiver(port=5002)
    sender = UDPSender(port=5002)
    latencies = []
    
    print("Running latency benchmark (1000 packets)...")
    for i in range(1000):
        start_ns = time.time_ns()
        sender.send_observation({"test": "data"})
        
        # busy wait until received for benchmark precision
        while True:
            obs, status = receiver.get_latest_observation()
            if status == "VALID":
                end_ns = time.time_ns()
                latencies.append((end_ns - start_ns) / 1e6) # ms
                break
            time.sleep(0.0001)
            
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    
    print(f"IPC Latency - P50: {p50:.3f} ms, P95: {p95:.3f} ms")
    
    import os
    os.makedirs("../../reports", exist_ok=True)
    with open("../../reports/ipc_benchmark.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value_ms"])
        writer.writerow(["P50_latency", f"{p50:.3f}"])
        writer.writerow(["P95_latency", f"{p95:.3f}"])
    print("Benchmark saved to reports/ipc_benchmark.csv")

if __name__ == "__main__":
    test_corner_cases()
    benchmark_ipc()
EOF
```
  - [x] **Thao tác 2:** Chạy test và benchmark.
```bash
cd edge-vision-uav-landing/src/ipc/
python test_udp_ipc.py
cd ../../../
```
- **Lệnh kiểm tra:**
```bash
cat edge-vision-uav-landing/reports/ipc_benchmark.csv
```
- **Expected output:** `All corner case tests passed.` và `IPC Latency - P50: ... ms, P95: ... ms`. File CSV được tạo.
- **Evidence cần lưu:** `reports/ipc_benchmark.csv`, console output.
- **Acceptance criteria:** Rejects packet lỗi; IPC metric được lưu (Engineering target cho nội bộ IPC là rất nhỏ < 10ms).
- **Failure condition:** Assert errors.

---

## Phase 2 — Machine B: Tracking Evaluation Harness

### Task 2.1: Chuẩn bị Sequence Manifest
- **Mục tiêu:** Tạo manifest liệt kê 3 easy, 3 medium, 3 hard sequences cho P1-B.
- **Mission phục vụ:** P1-B.
- **Trạng thái hiện tại:** MISSING.
- **File liên quan:** `edge-ai-training/manifests/tracking_eval_sequences.yaml`.
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Tạo thư mục và file.
```bash
mkdir -p edge-ai-training/manifests
cat << 'EOF' > edge-ai-training/manifests/tracking_eval_sequences.yaml
mission_id: P1_B_SINGLE_VEHICLE_TRACKING
sequences:
  - id: "seq_easy_01"
    difficulty: "easy"
    source: "visdrone"
    path: "data/val/seq_easy_01.mp4"
  - id: "seq_easy_02"
    difficulty: "easy"
    source: "visdrone"
    path: "data/val/seq_easy_02.mp4"
  - id: "seq_easy_03"
    difficulty: "easy"
    source: "visdrone"
    path: "data/val/seq_easy_03.mp4"
  - id: "seq_med_01"
    difficulty: "medium"
    source: "visdrone"
    path: "data/val/seq_med_01.mp4"
  - id: "seq_med_02"
    difficulty: "medium"
    source: "visdrone"
    path: "data/val/seq_med_02.mp4"
  - id: "seq_med_03"
    difficulty: "medium"
    source: "visdrone"
    path: "data/val/seq_med_03.mp4"
  - id: "seq_hard_01"
    difficulty: "hard"
    source: "visdrone"
    path: "data/val/seq_hard_01.mp4"
  - id: "seq_hard_02"
    difficulty: "hard"
    source: "visdrone"
    path: "data/val/seq_hard_02.mp4"
  - id: "seq_hard_03"
    difficulty: "hard"
    source: "visdrone"
    path: "data/val/seq_hard_03.mp4"
EOF
```
- **Acceptance criteria:** Manifest hợp lệ yaml và phân nhóm theo độ khó.

### Task 2.2: Implement Tracking Evaluator Prototype
- **Mục tiêu:** Viết script tính toán các metric (switches, fragmentation, lost_duration).
- **Mission phục vụ:** P1-B.
- **Trạng thái hiện tại:** MISSING.
- **File liên quan:** `edge-ai-training/scripts/tracking_evaluator.py`.
- **Các bước thao tác:**
  - [x] **Thao tác 1:** Viết file evaluator.
```bash
mkdir -p edge-ai-training/scripts
cat << 'EOF' > edge-ai-training/scripts/tracking_evaluator.py
import json

class TrackingEvaluator:
    def __init__(self):
        self.target_switches = 0
        self.frames_lost = 0
        self.frames_total = 0
        self.last_target_id = None
        
    def add_observation(self, obs):
        self.frames_total += 1
        
        state = obs.get("tracking_state")
        target_id = obs.get("target_id")
        
        if state in ["LOST", "OCCLUDED"]:
            self.frames_lost += 1
            
        if target_id is not None:
            if self.last_target_id is not None and target_id != self.last_target_id:
                self.target_switches += 1
            self.last_target_id = target_id
            
    def get_metrics(self):
        return {
            "target_switches": self.target_switches,
            "lost_frame_rate": self.frames_lost / max(1, self.frames_total),
            "frames_total": self.frames_total
        }

if __name__ == "__main__":
    # Smoke test
    evaluator = TrackingEvaluator()
    evaluator.add_observation({"tracking_state": "LOCKED", "target_id": 1})
    evaluator.add_observation({"tracking_state": "LOST", "target_id": 1})
    evaluator.add_observation({"tracking_state": "REACQUIRED", "target_id": 2})
    metrics = evaluator.get_metrics()
    print("Evaluator Test Metrics:", metrics)
    assert metrics["target_switches"] == 1
    assert metrics["lost_frame_rate"] == 1/3
    print("Evaluator logic works.")
EOF
```
- **Lệnh kiểm tra:** `python edge-ai-training/scripts/tracking_evaluator.py`
- **Expected output:** `Evaluator logic works.`
- **Acceptance criteria:** Evaluator sẵn sàng đọc dữ liệu JSON tracking để tổng hợp metric theo ROADMAP.

---

## Integration / Evidence Phase

- **Tổng hợp Evidence:**
  - [x] `docs/INTERFACE_CONTRACTS.md`
  - [x] `edge-vision-uav-landing/src/ipc/udp_sender.py` & `udp_receiver.py`
  - [x] `edge-vision-uav-landing/reports/ipc_benchmark.csv`
  - [x] `edge-ai-training/manifests/tracking_eval_sequences.yaml`
  - [x] `edge-ai-training/scripts/tracking_evaluator.py`

---

## End-of-Day Gate Review

### Gate Decision Template
- **Gate:** Daily Day 10 Review
- **Status:** PASS
- **Passed criteria:** IPC UDP rejection hoạt động, đo được P50/P95, tracking evaluator tính đúng switch và lost rate.
- **Missing criteria:** Không
- **Blocked criteria:** Không
- **Deferred criteria:** Không (Duy trì hoãn dataset từ Day 09).
- **Evidence paths:** `reports/ipc_benchmark.csv`, `INTERFACE_CONTRACTS.md`, stdout test.
- **Decision:** PASS to Day 11 (nếu test passed).

### End-of-Day Log Template
Sau khi hoàn thành, tạo file `edge-vision-uav-landing/daily_logs/day_10.md` với nội dung sau:
```markdown
# Day 10: UDP IPC schema, receiver prototype, and tracking evaluation harness

## Mission served
P1-A, P1-B, INFRA

## Done
- **Machine A:** Cập nhật schema v1 vào INTERFACE_CONTRACTS.md. Implement UDP sender/receiver hỗ trợ bounds buffer và stale check. Viết bài test contract và bench IPC.
- **Machine B:** Tạo cấu trúc đánh giá P1-B với yaml sequence manifest và class evaluator đo độ vỡ track và chuyển đổi ID.

## Evidence
- `docs/INTERFACE_CONTRACTS.md`
- `edge-vision-uav-landing/reports/ipc_benchmark.csv`
- `edge-vision-uav-landing/src/ipc/test_udp_ipc.py`
- `edge-ai-training/manifests/tracking_eval_sequences.yaml`

## Metrics
- Local IPC P50 Latency: [ĐIỀN TỪ OUTPUT] ms (MEASURED)
- Local IPC P95 Latency: [ĐIỀN TỪ OUTPUT] ms (MEASURED)
- Target Switch count test: Passed (MEASURED)

## Problems
- Không có.

## Decision
- PASS. Sẵn sàng cho Day 11.

## Tomorrow
- Day 11: Landing simulation v0.1 in SITL or Hybrid SITL.
```

### Git Commit Guidance
- [ ] **Thao tác 1:** Commit các file sau khi chạy thành công:
```bash
git add docs/INTERFACE_CONTRACTS.md
git add edge-vision-uav-landing/src/ipc/
git add edge-vision-uav-landing/reports/ipc_benchmark.csv
git add edge-ai-training/manifests/
git add edge-ai-training/scripts/tracking_evaluator.py
git add edge-vision-uav-landing/daily_logs/day_10.md
git commit -m "feat: implement Day 10 UDP IPC schema and tracking evaluator harness"
```

---

## Deliverables
- `docs/INTERFACE_CONTRACTS.md`
- Code Sender / Receiver UDP Python.
- Test script và kết quả Benchmark CSV của UDP.
- Manifest file YAML cho test sequence tracking.
- Script Python Tracking Evaluator cơ bản.

## Verification Matrix
| Hạng mục | Evidence yêu cầu | Trạng thái đầu ngày | Điều kiện hoàn thành |
|---|---|---|---|
| UDP Schema | `docs/INTERFACE_CONTRACTS.md` | MISSING | Có định dạng JSON payload và rule reject UDP. |
| UDP IPC Tests | stdout của `test_udp_ipc.py` | MISSING | Tất cả corner cases (malformed, out_of_order, stale) PASS. |
| IPC Benchmark | `reports/ipc_benchmark.csv` | MISSING | Đo được P50, P95. |
| Evaluation Harness | `manifests/tracking_eval_sequences.yaml`, `scripts/tracking_evaluator.py` | MISSING | Manifest tồn tại 9 chuỗi, Evaluator chạy pass logic test. |
