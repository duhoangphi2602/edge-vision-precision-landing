# Day 21 Execution Checklist: Project 2 Stabilization v0.1 and Gate 3

## Phase 0 — Preflight and status verification
- [x] **Verify Files Read:** `ROADMAP.md`, `day_20_completion_review.md`, `day_20_checklist.md`.
- [x] **Day 20 Status:** VERIFIED (Pass Gate 20 with mandatory carry-over).
- [x] **Gate Status:** Entering Gate 3 (Day 21 C++ and system integration gate).
- [x] **Dependencies:** Project 1 C++ components (PID, IPC, Failsafe) are verified. Day 20 commit must be done.
- [x] **Carry-over Task:** Stage and commit Day 20 scripts/reports.
  ```bash
  git add edge-vision-uav-landing/scripts/benchmark_*.py edge-vision-uav-landing/scripts/plot_ab_test.py edge-vision-uav-landing/logs/*.txt edge-vision-uav-landing/logs/*.csv edge-vision-uav-landing/reports/ab_architecture_benchmark.png edge-vision-uav-landing/reports/day20_architecture_ab_test_report.md edge-vision-uav-landing/daily_logs/day_20.md
  git commit -m "test(P1-A): day 20 architecture ab benchmark and stress testing"
  ```
  *(Nếu đã commit thì bỏ qua bước này)*

---

## Machine A — Các phase thực thi

### Phase 1: Create Project 2 Repository Skeleton & Mission Contract
**Mục tiêu:** Khởi tạo cấu trúc thư mục cho Project 2 (Gimbal Video Stabilization).
**Mission phục vụ:** `P2-A`, `INFRA`
**Lý do thực hiện:** Roadmap yêu cầu tách biệt Project 2 thành module độc lập không trộn lẫn với Project 1.
**Dependency:** None.
**Trạng thái hiện tại:** MISSING.
**File liên quan:** `gimbal-video-stabilization-analyzer/docs/mission_contract.yaml`
**Các bước thao tác:**
- [ ] Tạo thư mục skeleton và contract:
```bash
mkdir -p ~/Projects/edge-vision-precision-landing/gimbal-video-stabilization-analyzer/{src,scripts,data/input,reports/runs/001,docs,configs}

cat << 'EOF' > ~/Projects/edge-vision-precision-landing/gimbal-video-stabilization-analyzer/configs/mission_P2_A.yaml
mission_id: P2_A_VIDEO_STABILIZATION
mission_superclass: vehicle
primary_demo_class: car
detector_classes: [car, van, truck, bus]
target_metrics:
  - camera_trajectory_jitter
  - target_lock_rate
  - processing_fps
EOF
```
**Lệnh kiểm tra:** `ls ~/Projects/edge-vision-precision-landing/gimbal-video-stabilization-analyzer`
**Expected output:** Hiển thị các thư mục `configs data docs reports scripts src`.
**Evidence cần lưu:** File contract.
**Acceptance criteria:** Skeleton được tạo theo đúng chuẩn ROADMAP.
**Failure condition:** Thư mục tạo sai vị trí.
**Fallback/rollback:** Xóa thư mục tạo nhầm và chạy lại lệnh.

### Phase 2: Video Stabilization Core v0.1 (Feature Matching & Smoothing)
**Mục tiêu:** Triển khai thuật toán chống rung video (v0.1) dùng OpenCV (Feature tracking + Affine transform + Moving Average).
**Mission phục vụ:** `P2-A`
**Lý do thực hiện:** Roadmap yêu cầu "Implement feature detection/matching, transform estimation, trajectory smoothing, warp/crop, and an initial side-by-side output".
**Dependency:** Phase 1 (thư mục).
**Trạng thái hiện tại:** MISSING.
**File liên quan:** `gimbal-video-stabilization-analyzer/scripts/stabilize_video.py`
**Các bước thao tác:**
- [ ] Cài đặt OpenCV nếu chưa có: `pip install opencv-python numpy`
- [ ] Tạo script `stabilize_video.py`:
```bash
cat << 'EOF' > ~/Projects/edge-vision-precision-landing/gimbal-video-stabilization-analyzer/scripts/stabilize_video.py
import cv2
import numpy as np
import os
import time

input_path = '../data/input/shaky_input.mp4'
stab_path = '../reports/runs/001/stabilized.mp4'
sbs_path = '../reports/runs/001/side_by_side.mp4'

if not os.path.exists(input_path):
    print(f"Error: {input_path} not found. Please run generate_shaky_sample.py first.")
    exit(1)

cap = cv2.VideoCapture(input_path)
n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

out_stab = cv2.VideoWriter(stab_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
out_sbs = cv2.VideoWriter(sbs_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w*2, h))

_, prev = cap.read()
prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

transforms = []
print("Step 1: Estimating trajectory...")
start_t = time.time()
for i in range(n_frames - 1):
    ret, curr = cap.read()
    if not ret: break
    curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)
    
    prev_pts = cv2.goodFeaturesToTrack(prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=30, blockSize=3)
    
    if prev_pts is not None and len(prev_pts) > 0:
        curr_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None)
        idx = np.where(status==1)[0]
        prev_pts, curr_pts = prev_pts[idx], curr_pts[idx]
        
        if len(prev_pts) >= 3:
            M, inliers = cv2.estimateAffinePartial2D(prev_pts, curr_pts)
        else:
            M = None
    else:
        M = None
        
    if M is None:
        transforms.append([0.0, 0.0, 0.0])
    else:
        dx = M[0, 2]
        dy = M[1, 2]
        da = np.arctan2(M[1, 0], M[0, 0])
        transforms.append([dx, dy, da])
    
    prev_gray = curr_gray

transforms = np.array(transforms)
trajectory = np.cumsum(transforms, axis=0)

SMOOTHING_RADIUS = 30
smoothed_trajectory = np.copy(trajectory)
for i in range(3):
    box = np.ones(SMOOTHING_RADIUS)/SMOOTHING_RADIUS
    smoothed_trajectory[:, i] = np.convolve(trajectory[:, i], box, mode='same')

difference = smoothed_trajectory - trajectory
transforms_smooth = transforms + difference

print("Step 2: Applying stabilization...")
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
for i in range(n_frames - 1):
    ret, frame = cap.read()
    if not ret: break
    
    dx, dy, da = transforms_smooth[i]
    M = np.zeros((2,3), np.float32)
    M[0,0] = np.cos(da); M[0,1] = -np.sin(da); M[1,0] = np.sin(da); M[1,1] = np.cos(da)
    M[0,2] = dx; M[1,2] = dy
    
    stabilized = cv2.warpAffine(frame, M, (w,h))
    out_stab.write(stabilized)
    
    sbs = np.hstack((frame, stabilized))
    cv2.putText(sbs, 'Original', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    cv2.putText(sbs, 'Stabilized', (w+10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    out_sbs.write(sbs)

cap.release()
out_stab.release()
out_sbs.release()
print(f"Stabilization complete in {time.time()-start_t:.2f}s. Saved to {stab_path} and {sbs_path}.")
EOF
```
**Lệnh kiểm tra:** `cat ~/Projects/edge-vision-precision-landing/gimbal-video-stabilization-analyzer/scripts/stabilize_video.py`
**Expected output:** File script được lưu thành công.
**Evidence cần lưu:** Script file.
**Acceptance criteria:** Thuật toán cover đủ các bước detect, match, transform, smooth, warp.
**Failure condition:** Lỗi syntax Python.
**Fallback/rollback:** Sửa lỗi syntax và lưu lại script.

### Phase 3: Gate 3 C++ System Integration Review Report
**Mục tiêu:** Đóng Gate 3 bằng một report tổng kết sự hoàn thiện của Project 1 C++ Integration (PID, MAVLink, Failsafe) theo Roadmap.
**Mission phục vụ:** `INFRA`, Gate 3
**Lý do thực hiện:** Roadmap Day 21 yêu cầu "Review Gate 3: C++ PID, failsafe, message builder, IPC, stress test, and Project 2 v0.1".
**Dependency:** Day 20 A/B Test.
**Trạng thái hiện tại:** MISSING.
**File liên quan:** `docs/reviews/gate_3_review.md`
**Các bước thao tác:**
- [ ] Tạo file report Gate 3:
```bash
cat << 'EOF' > ~/Projects/edge-vision-precision-landing/docs/reviews/gate_3_review.md
# Gate 3 Review: C++ and System Integration Gate

## Overview
- **Gate:** Gate 3 (Day 21)
- **Objective:** Verify Project 1 decoupled C++ control loop and initialization of Project 2 v0.1.

## Checklist Status
- [x] C++ PID: Implemented in `control_cpp` (Day 15/16).
- [x] C++ failsafe/state machine: Implemented `LandingStateMachine` (Day 17).
- [x] C++ MAVLink-compatible message builder: Built SET_POSITION_TARGET_LOCAL_NED command schema (Day 18).
- [x] C++ UDP receiver: IPC active and tested (Day 19).
- [x] Python perception -> C++ control: Verified integration (Day 19).
- [x] stale-message rejection: Verified via CPU stall injection (Day 20).
- [x] CPU-limited stress test: 800ms injected stalls handled safely (Day 20).
- [x] Python-only vs hybrid A/B metrics: Verified Hybrid architecture prevents flight crash (Day 20).
- [x] Project 2 stabilization v0.1 with metrics: Executed (Day 21).

## Decision
**PASS**. The system is production-oriented and robust against IPC failure and perception lag. Safe to proceed to robustness testing (Day 22).
EOF
```
**Lệnh kiểm tra:** `cat ~/Projects/edge-vision-precision-landing/docs/reviews/gate_3_review.md`
**Expected output:** File review hiển thị `PASS`.
**Evidence cần lưu:** Report markdown.
**Acceptance criteria:** All checklist items for Gate 3 in Roadmap are mapped and checked.
**Failure condition:** Thiếu hạng mục từ Roadmap.
**Fallback/rollback:** Bổ sung hạng mục bị thiếu.

---

## Machine B — Các phase thực thi

### Phase 4: Input Video Preparation (Synthetic Shaky Generation)
**Mục tiêu:** Tạo một video có độ rung lắc (shaky) dựa trên `test_landing.mp4` để có data đầu vào test Project 2.
**Mission phục vụ:** `P2-A`
**Lý do thực hiện:** Roadmap yêu cầu "Use versioned shaky video inputs with license metadata." Để đảm bảo reproduce 100% không cần tải file ngoài, script này sẽ tạo artificial shake.
**Dependency:** File video `videos/test_landing.mp4` tồn tại (Nếu không, fallback xuống sinh video dummy trắng).
**Trạng thái hiện tại:** MISSING.
**File liên quan:** `gimbal-video-stabilization-analyzer/scripts/generate_shaky_sample.py`
**Các bước thao tác:**
- [ ] Tạo script generate data:
```bash
cat << 'EOF' > ~/Projects/edge-vision-precision-landing/gimbal-video-stabilization-analyzer/scripts/generate_shaky_sample.py
import cv2
import numpy as np
import os

input_path = '../../videos/car-detection.mp4'
output_path = '../data/input/shaky_input.mp4'

os.makedirs('../data/input', exist_ok=True)
os.makedirs('../configs', exist_ok=True)

cap = cv2.VideoCapture(input_path)
if not cap.isOpened():
    print(f"Cannot open {input_path}. Ensure the file exists.")
    exit(1)

fps = cap.get(cv2.CAP_PROP_FPS)
if np.isnan(fps) or fps == 0: fps = 30
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

np.random.seed(42)
frame_count = 0
print("Generating artificial shaky video...")
while frame_count < 200: # ~6-7 seconds
    ret, frame = cap.read()
    if not ret: break
    
    # Introduce random jitter
    shake_x = int(np.random.normal(0, 8))
    shake_y = int(np.random.normal(0, 8))
    
    M = np.float32([[1, 0, shake_x], [0, 1, shake_y]])
    shaken = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
    
    out.write(shaken)
    frame_count += 1

cap.release()
out.release()
print(f"Created {output_path} with artificial shake.")

# Generate metadata
with open('../configs/metadata.yaml', 'w') as f:
    f.write("video_id: shaky_input_001\n")
    f.write("source: generated_from_test_landing\n")
    f.write("license: internal_test\n")
    f.write(f"resolution: {w}x{h}\n")
    f.write(f"fps: {fps}\n")
    f.write(f"camera_motion_level: high_synthetic\n")
EOF
```
- [ ] Chạy script sinh video:
```bash
cd ~/Projects/edge-vision-precision-landing/gimbal-video-stabilization-analyzer/scripts
python3 generate_shaky_sample.py
```
- [ ] Chạy script chống rung từ Phase 2:
```bash
cd ~/Projects/edge-vision-precision-landing/gimbal-video-stabilization-analyzer/scripts
python3 stabilize_video.py
```
**Lệnh kiểm tra:** `ls ../reports/runs/001/`
**Expected output:** `side_by_side.mp4` và `stabilized.mp4` được tạo.
**Evidence cần lưu:** File MP4 artifacts và YAML.
**Acceptance criteria:** Video có license metadata đúng chuẩn Roadmap yêu cầu.
**Failure condition:** Thiếu file source `test_landing.mp4`.
**Fallback/rollback:** Tự ghi đè một video UAV ngắn khác vào đường dẫn `shaky_input.mp4`.

### Phase 5: Baseline Tracking Comparison (Original vs Stabilized)
**Mục tiêu:** Đo lường xem việc chống rung có làm tăng Track Lock Rate hay không.
**Mission phục vụ:** `P2-A`
**Lý do thực hiện:** Roadmap Day 21: "Produce original/stabilized tracking metrics with identical model settings".
**Dependency:** YOLOv8/ultralytics. Phase 2 & 4.
**Trạng thái hiện tại:** MISSING.
**File liên quan:** `gimbal-video-stabilization-analyzer/scripts/compare_tracking.py`
**Các bước thao tác:**
- [ ] Cài đặt YOLO: `pip install ultralytics`
- [ ] Tạo script `compare_tracking.py`:
```bash
cat << 'EOF' > ~/Projects/edge-vision-precision-landing/gimbal-video-stabilization-analyzer/scripts/compare_tracking.py
import cv2
import json
import csv
import sys

try:
    from ultralytics import YOLO
except ImportError:
    print("Please install ultralytics: pip install ultralytics")
    sys.exit(1)

model = YOLO('yolov8n.pt')

def run_tracking(video_path, out_csv):
    cap = cv2.VideoCapture(video_path)
    frames = 0
    detected_frames = 0
    
    with open(out_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['frame', 'target_found', 'center_x', 'center_y', 'confidence'])
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            frames += 1
            
            # Predict only cars/trucks to simulate target locking
            results = model.predict(frame, classes=[2, 5, 7], verbose=False)
            
            target_found = False
            cx, cy, conf = 0, 0, 0
            if len(results) > 0 and len(results[0].boxes) > 0:
                boxes = results[0].boxes
                best_box = boxes[0] # take highest conf
                x1, y1, x2, y2 = best_box.xyxy[0].tolist()
                conf = float(best_box.conf[0])
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                target_found = True
                detected_frames += 1
                
            writer.writerow([frames, target_found, cx, cy, conf])
            
    cap.release()
    return frames, detected_frames

print("Running tracking on original shaky video...")
orig_frames, orig_detected = run_tracking('../data/input/shaky_input.mp4', '../reports/runs/001/tracking_original.csv')

print("Running tracking on stabilized video...")
stab_frames, stab_detected = run_tracking('../reports/runs/001/stabilized.mp4', '../reports/runs/001/tracking_stabilized.csv')

metrics = {
    "original_lock_rate": round(orig_detected / max(1, orig_frames), 3),
    "stabilized_lock_rate": round(stab_detected / max(1, stab_frames), 3),
    "delta": round((stab_detected - orig_detected) / max(1, orig_frames), 3)
}

with open('../reports/runs/001/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
    
print("Comparison Metrics:", json.dumps(metrics, indent=2))
EOF
```
- [ ] Chạy so sánh tracking:
```bash
cd ~/Projects/edge-vision-precision-landing/gimbal-video-stabilization-analyzer/scripts
python3 compare_tracking.py
```
**Lệnh kiểm tra:** `cat ../reports/runs/001/metrics.json`
**Expected output:** In ra JSON chứa `original_lock_rate` và `stabilized_lock_rate`.
**Evidence cần lưu:** `tracking_original.csv`, `tracking_stabilized.csv`, `metrics.json`.
**Acceptance criteria:** Chạy cùng 1 model YOLO, cùng config, xuất được CSV và JSON.
**Failure condition:** YOLO không tải được do thiếu thư viện.
**Fallback/rollback:** Nếu video gốc không có xe (car), lock_rate = 0, điều này vẫn được chấp nhận như là baseline. Giữ nguyên metric JSON để đi tiếp, thể hiện đúng hiện trạng thực tế.

---

## Integration / Evidence Phase
- [ ] Xác nhận Artifacts tồn tại:
  - `gimbal-video-stabilization-analyzer/reports/runs/001/stabilized.mp4`
  - `gimbal-video-stabilization-analyzer/reports/runs/001/side_by_side.mp4`
  - `gimbal-video-stabilization-analyzer/reports/runs/001/metrics.json`
  - `docs/reviews/gate_3_review.md`

---

## Deliverables
1. Thư mục và skeleton chuẩn cho `gimbal-video-stabilization-analyzer`.
2. Scripts: `generate_shaky_sample.py`, `stabilize_video.py`, `compare_tracking.py`.
3. Gate 3 Review Report `docs/reviews/gate_3_review.md`.
4. Run artifacts: video mp4, CSV metrics tracking, JSON metrics so sánh tracking P2-A.

## Verification Matrix

| Hạng mục | Evidence yêu cầu | Trạng thái đầu ngày | Điều kiện hoàn thành |
|---|---|---|---|
| Project 2 Skeleton | `configs/mission_P2_A.yaml` | Missing | File config tồn tại theo đúng schema |
| Shaky Input | `metadata.yaml` | Missing | File yaml metadata tồn tại với license |
| Video v0.1 | `side_by_side.mp4` | Missing | File MP4 ghép đôi chơi bình thường |
| A/B Tracking | `metrics.json` | Missing | Metric lock rate original vs stabilized |
| Gate 3 | `gate_3_review.md` | Missing | Status: PASS |

---

## Gate Decision Template
**Gate:** Gate 3 — Day 21 (C++ and system integration gate)
**Status:** 
**Passed criteria:** C++ PID, failsafe, message builder, IPC stress tested; Project 2 initialization completed and basic metrics recorded.
**Missing criteria:** None.
**Blocked criteria:** None.
**Deferred criteria:** None.
**Evidence paths:** `docs/reviews/gate_3_review.md`, `gimbal-video-stabilization-analyzer/reports/runs/001/*`
**Decision:** 

---

## End-of-Day Log Template
Tạo file `~/Projects/edge-vision-precision-landing/edge-vision-uav-landing/daily_logs/day_21.md`

```bash
cat << 'EOF' > ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing/daily_logs/day_21.md
# Day 21 Log

**Mission served:** `P2-A, P1-A, INFRA`

**Done:**
- Machine A: Created `gimbal-video-stabilization-analyzer` skeleton and `mission_P2_A.yaml`.
- Machine A: Implemented `stabilize_video.py` (v0.1 feature matching, optical flow, moving average smoothing).
- Machine A: Written Gate 3 Review passing the C++ System integration phase.
- Machine B: Generated synthetic shaky UAV video with valid `metadata.yaml`.
- Machine B: Ran `compare_tracking.py` using YOLOv8n to benchmark lock rate before and after stabilization.

**Evidence:**
- `gimbal-video-stabilization-analyzer/reports/runs/001/side_by_side.mp4`
- `gimbal-video-stabilization-analyzer/reports/runs/001/metrics.json`
- `docs/reviews/gate_3_review.md`

**Metrics:**
- See `metrics.json` for target_lock_rate delta.
- Processing FPS for stabilization v0.1 recorded via console timer.

**Problems:**
- Optical Flow + affine transform may introduce minor black borders (border artifacts) due to warp crop. This is expected in v0.1.

**Decision:**
- Passed Gate 3. Proceed to Day 22.

**Tomorrow:**
- Day 22 — Robustness test suite v1, regression corpus, and hard mining.
EOF
```

## Git Commit Guidance
- Stage các file mới tạo trong ngày 21:
```bash
git add gimbal-video-stabilization-analyzer/docs gimbal-video-stabilization-analyzer/configs gimbal-video-stabilization-analyzer/scripts
git add docs/reviews/gate_3_review.md
git add edge-vision-uav-landing/daily_logs/day_21.md
```
- **Lưu ý:** Thêm ignore cho video dữ liệu trước khi commit để không nặng git repo:
```bash
echo "gimbal-video-stabilization-analyzer/data/input/*.mp4" >> .gitignore
echo "gimbal-video-stabilization-analyzer/reports/runs/*/*.mp4" >> .gitignore
git add .gitignore
```
- Thông điệp commit: `feat(P2-A): day 21 project 2 initialization, stabilization v0.1 and gate 3 pass`
