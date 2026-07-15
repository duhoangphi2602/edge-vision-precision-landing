# Roadmap 30 ngày — Deep Dive

## Edge Vision Precision Landing + AI Target Tracking + Gimbal Video Stabilization

## 1. Mục tiêu 30 ngày

Xây dựng 2 project portfolio chạy trên laptop/PC, không cần mua phần cứng drone, nhưng vẫn chứng minh được năng lực AI Engineer / Edge AI / Computer Vision / UAV Perception Intern.

### Project chính

Edge Vision Precision Landing & AI Target Tracking for UAV SITL

### Project phụ

Gimbal-Aware Video Stabilization & Tracking Quality Analyzer

## 2. Chiến lược triển khai

- Laptop = System / UAV / Integration / C++ Control / SITL / Docker / Report
- PC GPU = ML / Dataset / YOLO Training / ONNX Export / Benchmark / Batch Evaluation

## 3. Các lựa chọn kỹ thuật chính

## 3. Các lựa chọn kỹ thuật chính và Operational Modes

Roadmap định nghĩa rõ project có hai operational mode khác nhau. YOLO vehicle tracking là extension, không thay thế precision landing core. Không dùng vehicle bounding box như một `LANDING_TARGET` nếu không có thiết kế và kiểm chứng phù hợp. Không claim autonomous pursuit hoặc landing lên phương tiện chuyển động. Phần ML không được làm chậm các deliverable bắt buộc (C++ PID, failsafe, IPC, control timing, robustness tests, SITL/replay integration).

### Mode A — Precision Landing Core (Bắt buộc)
```text
Camera / Replay / Gazebo
→ ArUco hoặc AprilTag
→ Pixel error / pose estimation
→ PID centering
→ State machine
→ Failsafe
→ LANDING_TARGET hoặc velocity setpoint
```

### Mode B — AI Vehicle Tracking Extension
```text
UAV-domain video
→ YOLO detector
→ Target selection
→ Tracker
→ Center error / tracking metrics
→ Optional simulated target-centering
```

### Mission Class Mapping v1
Primary mission group: `ground_vehicle`. Included trong v0.1: `car`, `van`, `truck`, `bus`. Không thuộc scope v0.1: `pedestrian`, `people`, `bicycle`, `motor`, `tricycle`, `awning-tricycle`.
Quy tắc:
- Public baseline có thể train trên toàn bộ 10 class gốc của VisDrone để giữ tính benchmark.
- Target selector của project chỉ chấp nhận các class thuộc `ground_vehicle`.
- Việc remap các class thành một class chung `vehicle` là một experiment riêng. Không trộn metric.
- Artifact: `edge-ai-training/datasets/manifests/CLASS_MAPPING.md`.

### Dataset Strategy
Hệ thống có ba tầng dataset rõ ràng:
- **Tier 0 — Smoke test**: Dùng `coco8.yaml`. Chỉ 1–3 epochs. Experiment name bắt đầu bằng `SMOKE_`. Không dùng metric trong portfolio.
- **Tier 1 — Public UAV-domain baseline**: Ưu tiên VisDrone2019-DET cho detection, UAVDT hoặc VisDrone-VID cho tracking. Baseline portfolio bắt buộc dùng UAV-domain dataset.
- **Tier 2 — Project-specific adaptation set**: 300–800 frame từ tối thiểu 5–10 sequence. Yêu cầu source, license, annotation guideline, review, sequence-based split, held-out test sequences. Chất lượng và độ đa dạng quan trọng hơn số lượng 300 frame.

### Optimization Objective và Pareto Selection
Trước mỗi optimization experiment phải ghi: Mục tiêu, Baseline, Biến được thay đổi, Biến giữ nguyên, Hard constraints, Expected metric, Stop condition.
Hard constraints ban đầu:
- Batch size inference = 1.
- CPU FPS tối thiểu ≥ 10. Stretch goal ≥ 15 FPS.
- P95 latency ≤ 150 ms.
- Không làm control/failsafe nghẽn.
- Model export được sang runtime mục tiêu và Memory phù hợp deployment machine.

Không chọn model chỉ dựa vào mAP. Trong các model vượt hard constraints, ưu tiên: (1) Ground-vehicle recall, (2) AP small, (3) Target-lock rate, (4) P95 latency, (5) Model size, (6) mAP50-95.
Tạo `reports/model_selection_matrix.csv` và `reports/model_selection_decision.md`.

- Hardware constraint: cpulimit, Docker CPU/memory limit, stress test.

## 4. Chuẩn đầu ra sau 30 ngày

### Project chính cần có

```text
edge-vision-uav-landing/
├── README.md
├── TECHNICAL_DESIGN.md
├── PROBLEM.md
├── REQUIREMENTS.md
├── TEST_PLAN.md
├── RESULTS.md
├── LIMITATIONS.md
├── MODEL_CARD.md
├── DATASET_MANIFEST.md
├── Dockerfile
├── docker-compose.yml
├── configs/
├── src/
│   ├── perception/          # Python
│   ├── control_cpp/         # C++ PID + failsafe
│   ├── interface_cpp/       # C++ MAVLink bridge
│   ├── ipc/                 # UDP/TCP/Unix socket schema
│   ├── edge/                # ONNX/OpenVINO benchmark
│   ├── evaluation/
│   └── utils/
├── tests/
│   ├── python/
│   └── cpp/
├── scripts/
├── reports/
├── logs/
├── models/
└── videos/
```

### Project phụ cần có

```text
gimbal-video-stabilization-analyzer/
├── README.md
├── METHOD.md
├── RESULTS.md
├── LIMITATIONS.md
├── src/
│   ├── stabilize.py
│   ├── motion_estimator.py
│   ├── trajectory_smoother.py
│   ├── track_quality.py
│   └── metrics.py
├── scripts/
├── reports/
└── videos/
```

### ML Support Workspace cần có
Quy tắc: `raw/` là immutable. Mọi conversion phải chạy lại được bằng script. Không commit dataset hoặc checkpoint lớn vào Git (DVC/Git LFS là should-have). Commit manifest, scripts, configs, metric nhỏ và report.
```text
edge-ai-training/
├── datasets/
│   ├── raw/
│   │   ├── visdrone/
│   │   ├── uavdt/
│   │   └── custom_sources/
│   ├── interim/
│   ├── processed/
│   │   └── uav_vehicle_v1/
│   └── manifests/
│       ├── DATASET_SOURCES.md
│       ├── DATASET_MANIFEST.json
│       ├── CLASS_MAPPING.md
│       ├── ANNOTATION_GUIDELINES.md
│       └── SPLIT_MANIFEST.csv
├── experiments/
│   ├── EXPERIMENT_REGISTRY.csv
│   └── EXPERIMENT_TEMPLATE.md
├── scripts/
│   ├── download_dataset.py
│   ├── extract_video_frames.py
│   ├── convert_annotations.py
│   ├── remap_vehicle_classes.py
│   ├── split_by_sequence.py
│   ├── audit_dataset.py
│   ├── detect_duplicates.py
│   └── visualize_labels.py
├── reports/
└── models/
```

## 5. Chỉ số mục tiêu sau 30 ngày

| Nhóm | Metric | Mục tiêu thực tế trong 30 ngày |
|---|---|---|
| Precision landing / centering | Final error (Pixel-loop) | ≤ 30 px nếu chỉ pixel-loop |
| Precision landing / centering | Final error (Metric Sim) | ≤ 50 cm trong mô phỏng |
| Precision landing / centering | Final error (Real-camera) | Yêu cầu calib thật (nếu có) |
| Control | Overshoot | ≤ 25% |
| Control | Settling time | ≤ 5–8 s |
| Robustness | Target-loss threshold | Khoảng thời gian trước khi hệ thống quyết định target đã mất |
| Robustness | Failsafe reaction latency | Thời gian từ lúc threshold bị vượt đến khi safe state được kích hoạt (≤ 200ms) |
| Robustness | Recovery after 1s occlusion | ≤ 2 s |
| Edge inference | YOLO ONNX CPU FPS | Minimum target: ≥ 10 FPS. Stretch goal: ≥ 15 FPS |
| Edge inference | P95 latency | ≤ 100–150 ms |
| C++ control | Control loop rate | 30–50 Hz ổn định |
| Resource constraint | CPU-limited mode | Perception giảm FPS nhưng control/failsafe không chết |
| Stabilization project | Jitter reduction | ≥ 30% |
| Stabilization project | Tracking lost rate reduction | ≥ 20% |

Ultralytics hỗ trợ export YOLO sang ONNX/OpenVINO/TensorRT và nhiều format khác; tài liệu export cũng nhấn mạnh ONNX/OpenVINO có thể dùng cho CPU deployment và cung cấp Python/CLI export. ONNX Runtime hỗ trợ train bằng framework khác rồi deploy vào C#/C++/Java app, đồng thời áp dụng graph optimization và execution providers để cải thiện inference. OpenVINO là toolkit để deploy high-performance AI trên cloud, AI PC, edge devices và hỗ trợ convert/optimize/run inference trên Intel hardware.

## 6. Phân vai 2 máy

### Laptop — vai trò “System Engineer” & “Deployment Target”

Laptop tập trung vào:
- PX4/Gazebo/SITL
- OpenCV camera/replay pipeline
- ArUco/AprilTag detection
- Camera calibration / pose estimation
- C++ PID controller
- C++ MAVLink bridge
- Python → C++ IPC
- Robustness test
- Docker
- Technical documents
- Final demo video
- **Edge Deployment Benchmark**: Là target chính cho ONNX Runtime CPU, OpenVINO CPU, Thread count, Batch size 1, P50/P95 latency, FPS, Peak RAM, CPU utilization, Startup time, Concurrent perception + control test. Không dùng benchmark CPU trên PC GPU làm bằng chứng duy nhất cho edge deployment trên laptop.

### PC GPU — vai trò “ML Engineer”

PC GPU tập trung vào:
- Dataset UAV / VisDrone / custom subset (Evaluation)
- YOLO training
- Data augmentation
- Accuracy metrics (mAP, precision, recall)
- Export ONNX / OpenVINO
- Batch processing / Sanity-check ONNX
- Generate plots / reports
- Overnight training 24/24

Mọi report ML/Benchmark phải ghi rõ: Machine, CPU, GPU, RAM, OS, Runtime, Precision, Thread count, Input size.

## 7. Quy tắc vận hành mỗi ngày

Mỗi ngày phải có tối thiểu:
1. Một meaningful commit (code, test, dataset manifest, report, documentation, config). Không tạo commit rỗng chỉ để đạt checklist.
2. Một log hoặc bằng chứng mới.
3. Một file note trong `daily_logs/day_xx.md`
4. Quyết định ngày mai dựa trên lỗi/tiến độ hôm nay.

### Template daily_logs/day_XX.md

```md
# Day XX

## Done
- ...

## Metrics
- FPS:
- Latency:
- Error:
- CPU/RAM:
- Test pass/fail:

## Problems
- ...

## Decision
- Keep / cut / replace / fallback:

## Tomorrow
- Laptop:
- PC GPU:
```

Quy tắc rất quan trọng: Không có metric thì xem như chưa chứng minh được.

### 7.1. Quy tắc Agent Bắt buộc (Agent Rules)
1. Agent **KHÔNG ĐƯỢC** dùng `coco8.yaml`, `coco128.yaml` hoặc dataset demo khác làm portfolio baseline. Dataset demo chỉ được dùng cho smoke test và experiment name phải có `SMOKE_`.
2. Trước mọi training task, agent phải chỉ ra: project mission, target classes, dataset source, license/citation, split strategy, expected metrics, và experiment ID.
3. Nếu chưa có dataset phù hợp, agent phải tạo task tìm nguồn, tải, convert, extract, annotate, review, audit và versioning.
4. Agent không được random split các frame từ cùng một video nếu điều đó gây leakage.
5. Agent không được đánh dấu training hoàn thành nếu chưa lưu: command, config, seed, metrics, curves, best.pt và notes. Phải lưu failure cases và viết nguyên nhân.
6. Ưu tiên dữ liệu liên quan đúng UAV viewpoint hơn dataset lớn nhưng sai domain. Mọi claim trong README phải khớp với dữ liệu và test.
7. Agent KHÔNG tự ý chạy toàn bộ quy trình Optimization trong một ngày mà phải phân bổ theo dependency.
8. Ghi log phải phản ánh đúng thực tế, không được viết các claim chưa được xác minh (ví dụ: metric chưa đo). Không ghi latency nếu chưa có phương pháp đo.
9. Không gọi model là optimized nếu chưa có baseline comparison. Không chọn model chỉ dựa vào mAP.
10. Không thay đổi nhiều biến chính trong một ablation mà không giải thích.
11. Không dùng test set để tune threshold, augmentation hoặc hyperparameter. Không đưa failure samples trực tiếp từ test vào train.
12. Không chạy INT8 nếu chưa có representative calibration set. Không xem một seed là bằng chứng final.
13. Không gọi model final trước runtime/system validation.
14. Không commit raw dataset, checkpoint và experiment artifact lớn bằng `git add .`. Luôn chạy `git status` trước commit.
15. Mọi claim phải có metric, protocol, environment, artifact hoặc report.
16. Không để ML optimization làm chậm core UAV/system deliverables. Không claim hardware accuracy từ synthetic calibration. Không claim full PX4 closed-loop nếu chỉ mới có message builder.

## 8. Tuần 1 — Foundation, perception baseline, control offline

### Mục tiêu tuần 1

Đến cuối tuần 1, bạn phải có:

- Repo chính có cấu trúc sản phẩm
- Problem statement + requirements + test plan
- OpenCV camera/video reader
- ArUco/AprilTag detection
- Camera calibration hoặc synthetic calibration
- Pose/center error estimation
- PID controller bản Python ban đầu
- Replay mode
- PX4/Gazebo khởi động được hoặc có fallback rõ
- YOLO training baseline đầu tiên trên PC GPU

AprilTag là visual fiducial system phổ biến trong robotics, có thể tính 3D position, orientation và ID của tag tương đối với camera; thư viện AprilTag được viết bằng C, ít dependency và dễ nhúng vào ứng dụng khác. OpenCV camera calibration cần các cặp điểm 3D thực và điểm ảnh 2D tương ứng, thường dùng nhiều ảnh checkerboard để tìm camera parameters.

### Day 1 — Khóa scope, tạo repo, định nghĩa sản phẩm

#### Laptop

Tạo repo chính:

```bash
mkdir edge-vision-uav-landing
cd edge-vision-uav-landing
git init

mkdir -p src/{perception,estimation,ipc,evaluation,utils}
mkdir -p src/control_cpp src/interface_cpp
mkdir -p configs tests/{python,cpp} scripts reports logs videos models docs daily_logs

touch README.md TECHNICAL_DESIGN.md PROBLEM.md REQUIREMENTS.md TEST_PLAN.md RESULTS.md LIMITATIONS.md
touch MODEL_CARD.md DATASET_MANIFEST.md
```

Tạo PROBLEM.md:

- Problem: Build a laptop-based edge vision system for UAV precision landing and target tracking using simulation/replay validation.
- Industrial risks:
  - Camera noise
  - Motion blur
  - Target occlusion
  - Communication delay
  - Frame drop
  - Wind/disturbance
  - CPU limitation
  - False target
  - Target lost during descent
- Core objective: Demonstrate a measurable perception-control pipeline under resource constraints.
- Success criteria:
  - Detect landing target
  - Estimate target error
  - Run PID visual servoing
  - Generate MAVLink-compatible messages
  - Maintain failsafe under target loss
  - Benchmark AI inference under CPU constraint

Tạo REQUIREMENTS.md:

- Functional requirements:
  - FR-01: Read video/camera frames.
  - FR-02: Detect ArUco/AprilTag landing target.
  - FR-03: Estimate pixel error and metric pose when calibration exists.
  - FR-04: Send target observation to control process.
  - FR-05: C++ control process runs PID and failsafe.
  - FR-06: Generate LANDING_TARGET or SET_POSITION_TARGET_LOCAL_NED compatible data.
  - FR-07: Log target state, command, latency, and vehicle state.
  - FR-08: Run robustness test cases automatically.
  - FR-09: Support YOLO target tracking mode.
  - FR-10: Support ONNX/OpenVINO benchmark.
- Non-functional requirements:
  - NFR-01: Control loop >= 30 Hz.
  - NFR-02: Vision loop >= 15 FPS in marker mode.
  - NFR-03: P95 end-to-end latency <= 150 ms.
  - NFR-04: System must fail safe when target is lost.
  - NFR-05: System must be reproducible with scripts/Docker.

#### PC GPU

Tạo workspace ML:

```bash
mkdir edge-ai-training
cd edge-ai-training
mkdir -p datasets/raw datasets/interim datasets/processed datasets/manifests
mkdir -p experiments scripts reports models
nvidia-smi
python3 -c "import torch; print(torch.cuda.is_available())"
```

Tạo file:

- experiments/EXP_PLAN.md
- datasets/DATASET_SOURCES.md

#### Deliverable cuối ngày

- Repo chính đã có cấu trúc
- Repo ML đã có cấu trúc
- PROBLEM.md, REQUIREMENTS.md, TEST_PLAN.md bản đầu
- Git commit: init product roadmap and requirements

### Day 2 — OpenCV reader + ArUco/AprilTag detection

#### Laptop

Tạo:

- src/perception/video_reader.py
- src/perception/aruco_detector.py
- src/perception/apriltag_detector.py
- src/utils/overlay.py
- configs/perception.yaml

Yêu cầu code:

- Đọc webcam hoặc video file
- Resize frame
- Detect marker
- Vẽ corner, center, ID
- Tính pixel error:
  - $e_x = x_{target} - x_{center}$
  - $e_y = y_{target} - y_{center}$
- Log CSV:
  - timestamp, frame_id, detected, center_x, center_y, error_x, error_y

OpenCV ArUco pose estimation dùng marker coordinate system và camera coordinate system; pose được biểu diễn bằng rotation và translation vector.

#### PC GPU: ML environment và dataset discovery

- Cài/kiểm tra Ultralytics, CUDA. Ghi lại version GPU driver, CUDA, PyTorch, Ultralytics.
- Khảo sát UAV datasets (VisDrone, UAVDT). Ghi rõ nguồn, license, annotation format, class list, split.
- Tạo `datasets/manifests/DATASET_SOURCES.md` và `experiments/EXP_PLAN.md`.
- Chỉ chạy smoke test nếu cần kiểm tra môi trường. KHÔNG train portfolio baseline trước khi xác định được dataset source, split và experiment plan.

#### Deliverable

- Laptop: video marker detection overlay, CSV log detection
- PC GPU: Môi trường ML được xác minh, DATASET_SOURCES.md và EXP_PLAN.md.

### Day 3 — Camera calibration + pose estimation

#### Laptop

Tạo:

- src/estimation/camera_calibration.py
- src/estimation/pose_estimator.py
- configs/camera.yaml
- reports/calibration_report.md

Yêu cầu:

- Lưu camera_matrix
- Lưu dist_coeffs
- Estimate marker pose:
  - translation vector tvec
  - rotation vector rvec
- Viết Unit test cho Coordinate Transform (Camera frame -> Body frame)
- Convert tvec sang relative x/y/z error
- So sánh pixel error vs metric error

Calibration có thể làm theo 2 hướng:

- Option A: Webcam thật + checkerboard/Charuco board
- Option B: Synthetic camera intrinsics nếu chỉ dùng simulation/replay

#### PC GPU

UAV-domain YOLO Baseline v0.1:

- **Task A — GPU verification**: nvidia-smi, yolo checks, version report.
- **Task B — Smoke test**: Chạy `SMOKE_coco8_yolo11n` (1 epoch, imgsz=640).
- **Task C — Dataset manifest & Registry**: Tạo/cập nhật `DATASET_SOURCES.md`, `DATASET_MANIFEST.json`, `CLASS_MAPPING.md`, `EXP_PLAN.md`, `EXPERIMENT_REGISTRY.csv`.
- **Task D — Dataset acquisition và audit**: Tải VisDrone. Kiểm tra image-label pairing, corrupted images, invalid boxes, class stats. Ghi known limitations. (Chưa hoàn thành task này nếu chỉ tải xong).
- **Task E — Baseline train**: (Chỉ chạy khi đủ điều kiện) `TRN_001_visdrone_yolo11n_640`. Có thể carry over nếu không đủ thời gian.

#### Deliverable

- pose_estimator.py chạy được.
- calibration_report.md có thông số camera. (Ghi rõ synthetic calibration chỉ kiểm tra phần mềm, không chứng minh metric accuracy thực tế).
- GPU verification report, Dataset Manifest, Audit draft, và Smoke test pass.

### Day 4 — PID visual servoing offline

#### Laptop

Tạo:

- src/control_cpp/ (chưa cần C++ ngay, chuẩn bị folder)
- src/control_py/pid_controller.py
- src/evaluation/control_metrics.py
- tests/python/test_pid_controller.py

PID bản đầu bằng Python:

- Input: error_x, error_y, dt
- Output: vx_cmd, vy_cmd
- Features:
  - Kp, Ki, Kd
  - deadband
  - saturation
  - anti-windup
  - derivative low-pass

Metrics cần tính:

- overshoot
- settling time
- steady-state error
- command saturation ratio

#### PC GPU

- Đánh giá `TRN_001_visdrone_yolo11n_640` Baseline.
- Thực hiện Resolution ablation. Mỗi resolution là một experiment riêng:
  - `TRN_002_visdrone_yolo11n_960`
  - `TRN_003_visdrone_yolo11n_1280` (nếu có đủ tài nguyên)
- Chỉ đổi image size. Giữ nguyên: Dataset, Split, Model, Seed, Augmentation, Epoch policy.
- Đánh giá: mAP50, mAP50-95, AP small, Vehicle recall, VRAM, Training time.

#### Deliverable

- PID offline simulation plot
- tests/python/test_pid_controller.py pass
- Log của `TRN_001`, `TRN_002`, `TRN_003`.

### Day 5 — Replay mode + fault injection v0.1

#### Laptop

Tạo:

- src/perception/replay_source.py
- src/evaluation/fault_injection.py
- configs/faults.yaml
- scripts/run_replay_test.py

Fault injection ban đầu:

- Gaussian noise
- Motion blur
- Random occlusion rectangle
- Frame drop
- Artificial delay

Log thêm:

- timestamp, frame_id, injected_fault, detection_status, latency_ms

#### PC GPU

Thực hiện Error Analysis và Dataset Audit:
- Tạo `reports/yolo_v0_1_report.md`.
- Tạo thư mục `reports/error_analysis/`. Phân tích: false positive, false negative, tiny object, occlusion, motion blur, crowded scene, domain gap, negative sequences.
- Tạo `reports/dataset_audit_before_cleaning.md`, `dataset_audit_after_cleaning.md`, và `dataset_cleaning_delta.csv`.
- Ghi chú: Không dùng test set để tune model hoặc thêm trực tiếp test failures vào train.

#### Deliverable

- Replay test chạy bằng config
- Fault injection hoạt động
- Error analysis report và Dataset audit delta.

### Day 6 — PX4/Gazebo/SITL setup

#### Laptop

Cài và chạy PX4/Gazebo:

- Goal A: PX4 SITL khởi động được, Gazebo vehicle model chạy được
- Goal B: Có camera stream nếu kịp
- Fallback: Nếu camera bridge mất thời gian, giữ replay pipeline và dùng SITL chỉ để lấy vehicle state / offboard command test

Tài liệu PX4 mô tả Offboard là mode điều khiển movement/attitude bằng position, velocity, acceleration, attitude setpoints từ external controller, và cần stream để chứng minh controller còn hoạt động.

Tạo:

- docs/SITL_SETUP.md
- scripts/run_px4_sitl.sh

#### PC GPU

Lên kế hoạch custom dataset workflow (Tier 2):
- Chọn nguồn dữ liệu (video tự quay hoặc opensource). Ghi nhận license.
- Tạo annotation guideline rõ ràng.
- Extract frame có kiểm soát. Label thử (pilot annotation) 50-100 frame.
- Review pilot annotation.
- Tạo nhóm Hard-negative/hard-example pool.

### Day 7 — Gate 1: Foundation review

#### Laptop

Dọn repo:

- README quick start sơ bộ
- WEEK1_REPORT.md
- Video 30–60s: marker detection + PID overlay
- Git tag: week1-foundation

#### PC GPU

- Sửa annotation guideline sau review.
- Tiếp tục annotation custom dataset.
- Audit pilot set.
- Chọn week-1 provisional model candidate (Chưa gọi model là final, chưa chạy multi-seed).

#### Gate 1 phải đạt

### System
- Marker detection.
- Pixel error.
- Pose estimator functional test.
- PID offline chạy.
- Replay + fault injection hoạt động.
- PX4/Gazebo hoặc fallback rõ ràng.

### ML/Data
- COCO8 chỉ dùng làm smoke test.
- Đã ghi rõ Dataset source/license/citation.
- Class mapping hoàn tất.
- Dataset manifest.
- Audit report bước đầu.
- UAV-domain baseline (`TRN_001`) đã chạy hoặc có trạng thái carry-over rõ.
- Lưu trữ command/config/seed/log. Có Failure samples bước đầu.

## 9. Tuần 2 — Closed-loop, MAVLink concept, YOLO/ONNX baseline

### Mục tiêu tuần 2

Cuối tuần 2 phải có:

- State machine landing
- MAVLink message design
- 2D closed-loop landing/centering simulation
- LANDING_TARGET mode concept
- SET_POSITION_TARGET_LOCAL_NED mode concept
- Robustness test v0.1
- YOLO tracking extension
- ONNX benchmark đầu tiên

### Day 8 — MAVLink interface design + state machine

#### Laptop

Tạo:

- src/interface_cpp/mavlink_message_design.md
- src/control_py/state_machine.py
- docs/MAVLINK_DESIGN.md
- docs/COORDINATE_FRAME_CONTRACT.md (Định nghĩa OpenCV frame, Body frame, Local NED, Dấu X/Y/Z, Transform path. Bắt buộc trước khi tích hợp).

MAVLINK_DESIGN.md phải có 2 mode (angle-only / metric position / velocity setpoint). Không trộn LANDING_TARGET rate với PX4 Offboard proof-of-life rate.

State machine:

```text
SEARCH -> TRACK -> APPROACH -> DESCEND -> LAND -> ABORT/HOVER
```

#### PC GPU

Tiếp tục custom dataset workflow:
- Tiếp tục custom dataset annotation.
- Split theo sequence (đảm bảo không leakage).
- Chạy duplicate/leakage check.
- Freeze dataset version khi quality gate pass.

#### Deliverable

- MAVLINK_DESIGN.md và COORDINATE_FRAME_CONTRACT.md
- state machine chạy được bằng test giả lập
- Custom dataset đã được freeze.

### Day 9 — Closed-loop 2D simulation

#### Laptop

Tạo:

- src/evaluation/landing_2d_sim.py
- scripts/run_2d_landing_sim.py
- reports/closed_loop_2d_v0.md

#### PC GPU

- Hoàn thiện custom dataset.
- Chạy public-to-custom fine-tuning (`FT_001_public_to_custom`).
- So sánh before/after (Baseline `TRN_001` vs `FT_001`).
- Chuẩn bị tracking evaluation protocol.

#### Deliverable

- closed_loop_2d_v0.md có plot error over time
- Fine-tune evidence report.

### Day 10 — Python perception → control observation schema

#### Laptop

Tạo schema chung:

- src/ipc/target_observation_schema.md
- src/ipc/udp_sender.py
- src/ipc/udp_receiver_stub.py

Message format phải tuân theo COORDINATE_FRAME_CONTRACT:

```json
{
  "schema_version": 1,
  "sequence_id": 0,
  "frame_id": 0,
  "capture_timestamp_ns": 0,
  "publish_timestamp_ns": 0,
  "source": "aruco|apriltag|yolo",
  "measurement_type": "pixel|angle|metric_pose",
  "coordinate_frame": "camera_optical",
  "detected": true,
  "target_id": 1,
  "confidence": 0.98,
  "u": 320.0,
  "v": 240.0,
  "error_x_px": 0.0,
  "error_y_px": 0.0,
  "x_m": 0.12,
  "y_m": -0.05,
  "z_m": 1.8,
  "metric_position_valid": true,
  "angle_x_rad": 0.0,
  "angle_y_rad": 0.0,
  "angle_valid": false,
  "stale_after_ms": 200
}
```

Yêu cầu:

- Perception gửi observation qua UDP localhost
- Receiver đọc và in latency. Dropped message tính theo `sequence_id`.
- Không sử dụng metric pose nếu `metric_position_valid=false`.

#### PC GPU

Chuẩn bị Tracking Evaluation Protocol:
- Chọn held-out sequences (không leakage): 3 easy, 3 medium, 3 hard.
- Xác định metric (ID switches, target-lock rate, v.v.).
- (Chưa đánh giá tracker nếu tracker chưa tồn tại).

#### Deliverable

- UDP IPC prototype
- ipc_latency_log.csv

### Day 11 — Precision landing run v0.1

#### Laptop

Chạy landing/centering simulation với nhiều initial conditions:

- Case set:
  - initial offset 0.5 m
  - initial offset 1.0 m
  - initial offset 2.0 m
  - initial offset 3.0 m
  - diagonal offset

Tạo:

- reports/precision_landing_v0_1.md
- logs/landing_runs/

#### PC GPU

Benchmark `BENCH_001_onnx_cpu_threads`:
- Export model sang ONNX (`best.onnx`).
- Test dynamic/static input. Test imgsz 416 vs 640.
- Đo PyTorch FPS vs ONNX Runtime FPS. Đo P50/P95 latency, Peak Memory.
- Chạy benchmark trên Laptop (Deployment target), PC GPU chỉ hỗ trợ export và sanity check.

#### Deliverable

- 20 run landing simulation
- bảng final error / overshoot / settling time
- benchmark_runtime_v0.csv đầu tiên.

### Day 12 — Robustness v0.1 + CPU constraint

#### Laptop

Test cases:

- T01_normal
- T02_noise_low
- T03_noise_high
- T04_blur_low
- T05_blur_high
- T06_occlusion_0_5s
- T07_occlusion_1s
- T08_occlusion_2s
- T09_delay_100ms
- T10_delay_200ms
- T11_frame_drop_10
- T12_frame_drop_20
- T13_cpu_limit_50
- T14_cpu_limit_20

Dùng cpulimit hoặc Docker CPU limit:

```bash
cpulimit -l 20 -- python3 scripts/run_perception.py
```

cpulimit giới hạn CPU usage của process theo phần trăm CPU và dùng SIGSTOP/SIGCONT để kiểm soát CPU thực tế của process.

Điều cần chứng minh:

- Khi Python perception bị nghẽn, C++/control hoặc failsafe vẫn không chết.
- Nếu chưa có C++ node, test này ghi baseline Python-only để so sánh ở tuần 3.

#### PC GPU

- Train model với augmentation mô phỏng robustness: noise, blur, brightness, scale
- So sánh model trước/sau augmentation

#### Deliverable

- robustness_v0_1.csv
- CPU-limited baseline report
- augmentation comparison sơ bộ

### Day 13 — YOLO target tracking extension

#### Laptop

Tích hợp mode:

```bash
python scripts/run_perception.py --mode marker_landing
python scripts/run_perception.py --mode yolo_tracking
```

Tạo:

- src/perception/yolo_detector.py
- src/perception/target_selector.py
- src/perception/simple_tracker.py

Target selection logic:

- Chọn class mong muốn
- Chọn confidence cao nhất
- Chọn target gần tâm nhất
- Giữ target ID nếu tracker còn valid

#### PC GPU

Evaluate Tracker (`TRACK_001_bytetrack_heldout`):
- Chạy evaluation protocol trên PC GPU để đo đạc metrics.
- So sánh các thuật toán ByteTrack vs BoT-SORT offline.

#### Deliverable

- yolo_tracking mode chạy được
- log tracker ban đầu.
- video YOLO target tracking

### Day 14 — Gate 2: Integration review

#### Laptop

Tạo:

- reports/WEEK2_REPORT.md
- videos/week2_precision_landing_v0.mp4
- videos/week2_yolo_tracking_v0.mp4

#### PC GPU

Chạy Tracking Evaluation:
- Tối thiểu 3 easy, 3 medium, 3 hard sequences.
- Tính: ID continuity, ID switches, track fragmentation, target-lock rate, lost-target duration, recovery time, center jitter, FPS, P50/P95 latency.
- Giữ cả success và failure videos.
- Model candidate ở giai đoạn này gọi là "ML candidate v0.1" (Không chạy multi-seed final ở đây).

#### Gate 2 phải đạt

- Closed-loop 2D simulation chạy được.
- State machine có bản đầu.
- IPC prototype chạy được.
- Robustness v0.1 có kết quả.
- UAV-domain detector và Custom adaptation dataset rõ trạng thái.
- Public-only vs fine-tuned comparison.
- Tracking trên held-out sequences (Target-lock/recovery metrics).
- ONNX benchmark bước đầu. Domain-gap report.
- ML Candidate v0.1 (Chưa gọi final).

## 10. Tuần 3 — C++ control, MAVLink bridge, IPC, project phụ CV

### Mục tiêu tuần 3

Đây là tuần “khóa 5% còn lại” để project không bị Python-only.

Cuối tuần 3 phải có:

- C++ PID controller
- C++ failsafe manager
- C++ MAVLink message builder/bridge
- Python perception → C++ control qua IPC
- LANDING_TARGET mode
- SET_POSITION_TARGET_LOCAL_NED mode
- A/B benchmark Python-only vs Python+C++
- CPU-limited stress test với C++ control vẫn sống
- Project phụ video stabilization v0.1

ROS 2 callback groups được dùng để kiểm soát callback khi chạy Multi-Threaded Executor, giúp tránh việc camera/inference/control/logging chặn lẫn nhau trong node đa luồng. Với roadmap này, ROS 2 là optional integration; phần bắt buộc là tách process Python perception và C++ control để chứng minh embedded/real-time mindset.

### Day 15 — Refactor architecture + CMake skeleton

#### Laptop

Refactor project:

```text
src/perception/
  run_perception.py
  aruco_detector.py
  apriltag_detector.py
  yolo_detector.py

src/ipc/
  udp_sender.py
  target_observation_schema.md

src/control_cpp/
  CMakeLists.txt
  include/
  src/
  tests/
```

Tạo C++ skeleton:

- src/control_cpp/include/pid_controller.hpp
- src/control_cpp/src/pid_controller.cpp
- src/control_cpp/tests/test_pid_controller.cpp

CMake:

```cmake
cmake_minimum_required(VERSION 3.16)
project(edge_uav_control)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(control_lib
    src/pid_controller.cpp
)

add_executable(test_pid_controller
    tests/test_pid_controller.cpp
)

target_link_libraries(test_pid_controller control_lib)
```

#### PC GPU

- Chạy training cho candidate v0.1 nếu model chưa ổn
- Nếu model đã ổn, chuyển sang batch evaluation

#### Deliverable

- Project refactor xong
- C++ build được bằng CMake
- PID C++ skeleton compile được

### Day 16 — C++ PID controller + unit tests

#### Laptop

Implement C++ PID:

```cpp
struct PIDConfig {
    double kp;
    double ki;
    double kd;
    double output_min;
    double output_max;
    double integral_min;
    double integral_max;
    double deadband;
};

class PIDController {
public:
    explicit PIDController(const PIDConfig& config);
    double update(double error, double dt);
    void reset();

private:
    PIDConfig config_;
    double integral_;
    double prev_error_;
    bool first_update_;
};
```

Unit tests:

- Test 1: zero error -> zero output
- Test 2: positive error -> positive output
- Test 3: output saturation works
- Test 4: integral anti-windup works
- Test 5: reset clears state

#### PC GPU

Generate YOLO metrics report:

- mAP
- precision
- recall
- model size
- inference speed

#### Deliverable

- C++ PID pass tests
- control_cpp benchmark: update time per call
- YOLO metrics draft v0.1

### Day 17 — C++ failsafe manager + state machine

#### Laptop

Tạo:

- src/control_cpp/include/failsafe_manager.hpp
- src/control_cpp/src/failsafe_manager.cpp
- src/control_cpp/tests/test_failsafe_manager.cpp

State enum:

```cpp
enum class SystemState {
    SEARCH,
    TRACK,
    APPROACH,
    DESCEND,
    LAND,
    HOVER,
    ABORT
};
```

Failsafe rules:

- Nếu target_lost_time > 2.0s -> HOVER hoặc ABORT
- Nếu observation timestamp quá cũ -> HOVER
- Nếu confidence < threshold -> không cập nhật command
- Nếu CPU/perception stalled -> giữ safe mode
- Nếu command vượt limit -> saturate

#### PC GPU

- Export ONNX v0.1
- Export OpenVINO nếu có thể
- Tạo model card bản đầu

#### Deliverable

- C++ failsafe tests pass
- MODEL_CARD.md draft

### Day 18 — C++ MAVLink bridge design + message builder

#### Laptop

Tạo:

- src/interface_cpp/include/mavlink_bridge.hpp
- src/interface_cpp/src/mavlink_bridge.cpp
- src/interface_cpp/tests/test_mavlink_message_builder.cpp

Chức năng:

- Build LANDING_TARGET-like payload
- Build SET_POSITION_TARGET_LOCAL_NED-like payload
- Không nhất thiết phải full autopilot integration ngay
- Bắt buộc log được message fields

- Mode 1: LANDING_TARGET mode
  - Input: target x/y/z hoặc angle_x/angle_y, timestamp, valid flag
  - Output: target observation message
- Mode 2: SET_POSITION_TARGET_LOCAL_NED mode
  - Input: vx_cmd, vy_cmd, vz_cmd, yaw_rate_cmd
  - Output: velocity setpoint message

MAVLink common message set là nơi định nghĩa các message chuẩn nên dùng thay vì tự tạo dialect riêng nếu message đã tồn tại.

#### PC GPU

Export models cho Edge Benchmark (ONNX, OpenVINO). Laptop sẽ chạy script benchmark với cấu hình thực tế (threads=1,2,4, imgsz). PC GPU chuẩn bị test scripts `eval_onnx.py`.

#### Deliverable

- C++ MAVLink bridge compile được
- Message fields log đúng
- benchmark_onnx_threads.csv

### Day 19 — IPC Python → C++ control

#### Laptop

Tạo C++ UDP receiver:

- src/control_cpp/src/control_node.cpp

Luồng xử lý:

- Python perception: frame → detection → target_observation JSON/CSV binary → UDP
- C++ control: receive observation → validate timestamp → update failsafe state → run PID → build MAVLink-compatible command → log command

Metrics:

- IPC latency
- message drop count
- control loop frequency
- control loop jitter
- stale observation count

#### PC GPU

- Tiếp nhận kết quả benchmark CSV từ Laptop.
- Generate plots (FPS vs Latency, Resource constraints).

#### Deliverable

- Python perception gửi được sang C++
- C++ node sinh command từ target error
- ipc_control_log.csv

### Day 20 — CPU-limited stress test với hybrid architecture

#### Laptop

Test A/B:

- A: Python-only control
- B: Python perception + C++ control

Test cases:

- CPU 100%
- CPU 50%
- CPU 20%
- CPU 20% + occlusion 1s
- CPU 20% + delay 200ms
- CPU 20% + frame drop 20%

Metrics:

- control_loop_rate_mean
- control_loop_jitter_p95
- command_latency_p95
- failsafe_reaction_time
- stale_command_count
- unsafe_command_count

Cần chứng minh:

- Python perception có thể giảm FPS khi CPU bị bóp.
- C++ control/failsafe vẫn chạy đều.
- Khi observation cũ, C++ node không gửi command nguy hiểm.

#### PC GPU

- Lựa chọn Release Candidate.
- Chạy Multi-seed validation (3 seeds) trên mô hình Release Candidate. Đóng băng training.
- Chuẩn bị Export ONNX INT8 quantization nếu có tập calibration đại diện.

#### Deliverable

- ab_test_python_vs_cpp_control.md
- cpu_limited_stress_report.md
- Kết quả Multi-seed validation.

### Day 21 — Project phụ CV: video stabilization v0.1 + Gate 3

#### Laptop

Tạo repo phụ hoặc folder riêng:

```bash
mkdir gimbal-video-stabilization-analyzer
cd gimbal-video-stabilization-analyzer
mkdir -p src scripts reports videos
touch README.md METHOD.md RESULTS.md LIMITATIONS.md
```

Pipeline project phụ:

```text
Input shaky video
  -> feature detection / optical flow
  -> estimate transform
  -> smooth camera trajectory
  -> warp stabilized frame
  -> compare before/after tracking quality
```

Tạo:

- src/stabilize.py
- src/motion_estimator.py
- src/trajectory_smoother.py
- src/metrics.py

#### PC GPU

- Batch process video nếu cần
- Generate before/after metrics

#### Gate 3 phải đạt

- [ ] C++ PID chạy được
- [ ] C++ failsafe chạy được
- [ ] C++ MAVLink bridge/message builder có bản đầu
- [ ] Python → C++ IPC chạy được
- [ ] A/B benchmark Python-only vs hybrid có số liệu
- [ ] CPU-limited test có kết quả
- [ ] Project phụ video stabilization có pipeline đầu tiên

## 11. Tuần 4 — Validation, polish, documentation, final product

### Mục tiêu tuần 4

Cuối tuần 4 phải có sản phẩm review được:

- Full test suite
- Robustness report
- Results report
- Docker
- README đẹp
- Technical Design Document
- Demo video
- Project phụ hoàn thiện
- Clean clone test

### Day 22 — Full robustness test suite v1

#### Laptop

Tạo:

- configs/test_cases.yaml
- scripts/run_all_robustness_tests.py
- src/evaluation/test_runner.py
- src/evaluation/report_generator.py

```yaml
cases:
  - name: normal
    noise: 0
    blur: 0
    occlusion_s: 0
    delay_ms: 0
    frame_drop: 0
    cpu_limit: 100

  - name: occlusion_1s
    occlusion_s: 1.0

  - name: delay_200ms
    delay_ms: 200

  - name: cpu_20
    cpu_limit: 20

  - name: cpu_20_occlusion_1s
    cpu_limit: 20
    occlusion_s: 1.0
```

Metrics output:

- pass/fail
- final error
- target lock rate
- recovery time
- control jitter
- P95 latency
- unsafe command count

#### PC GPU

- Export các file model cuối cùng (`best.pt`, `best.onnx`).
- Viết final ML metrics report (trung bình của 3 seeds).
- Generate biểu đồ FPS vs mAP (Pareto front) cho Technical Design.
- Cấm train thêm model mới từ thời điểm này.

#### Deliverable

- robustness_report_v1.md
- final model artifacts và ML metrics.

### Day 23 — Technical Design Document deep write

#### Laptop

Viết TECHNICAL_DESIGN.md theo cấu trúc:

1. Overview
2. Problem Statement
3. Industrial Risks
4. Requirements
5. System Architecture
6. Perception Design
7. IPC Design
8. C++ Control Design
9. MAVLink Design
10. Edge AI Design
11. Robustness Test Design
12. Evaluation Metrics
13. Limitations
14. Future Work

Phải có diagram ASCII:

```text
Camera / Replay / Gazebo
        |
        v
Python Perception
OpenCV / AprilTag / YOLO / ONNX
        |
        | UDP target_observation
        v
C++ Control Node
PID / Failsafe / MAVLink Bridge
        |
        v
PX4 / SITL / Command Log
        |
        v
Evaluation + Reports
```

#### PC GPU

- Sinh biểu đồ: FPS runtime comparison, latency P50/P95, mAP/precision/recall, model size comparison

#### Deliverable

- TECHNICAL_DESIGN.md gần hoàn chỉnh
- figures/benchmark charts

### Day 24 — Results Report

#### Laptop

Viết RESULTS.md:

1. Environment
2. Test protocol
3. Precision landing / centering results
4. Control results
5. Robustness results
6. A/B Python-only vs Python+C++ results
7. Edge inference benchmark
8. Project 2 stabilization results
9. Error analysis
10. Limitations

Bảng bắt buộc:

| Test case | Final error | Overshoot | Recovery | P95 latency | Pass/Fail |
|---|---:|---:|---:|---:|---|
| ... | ... | ... | ... | ... | ... |

| Runtime | Model | FPS | P50 latency | P95 latency | CPU | RAM |
|---|---|---:|---:|---:|---:|---:|
| ... | ... | ... | ... | ... | ... | ... |

| Architecture | Control rate | Jitter P95 | Stale command | Failsafe reaction |
|---|---:|---:|---:|---:|
| ... | ... | ... | ... | ... |

#### PC GPU

- Hoàn thiện Model Card (`MODEL_CARD.md`).
- Hoàn thiện Dataset Manifest (`DATASET_MANIFEST.md`).
- Backup tất cả artifacts liên quan đến Release Candidate.

#### Deliverable

- RESULTS.md có số liệu thật
- MODEL_CARD.md
- DATASET_MANIFEST.md

### Day 25 — Docker + reproducibility

#### Laptop

Tạo:

- Dockerfile
- docker-compose.yml
- scripts/setup.sh
- scripts/run_marker_landing.sh
- scripts/run_yolo_tracking.sh
- scripts/run_cpp_control.sh
- scripts/run_all_tests.sh

Docker Compose services:

```yaml
services:
  perception:
    build: .
    command: python scripts/run_perception.py --mode marker_landing

  control_cpp:
    build: .
    command: ./build/control_node

  evaluator:
    build: .
    command: python scripts/run_all_robustness_tests.py
```

Tạo clean command:

```bash
bash scripts/run_all_tests.sh
```

#### PC GPU

- Kiểm tra model paths
- Tạo release folder: release/models/, release/reports/, release/videos/

#### Deliverable

- Docker chạy được hoặc README local setup chạy được
- run_all_tests.sh

### Day 26 — Project phụ hoàn thiện

#### Laptop

Project phụ cần hoàn thiện:

- stabilize.py
- track_quality.py
- metrics.py
- README.md
- METHOD.md
- RESULTS.md

Metrics:

- frame-to-frame motion variance
- target center variance
- jitter reduction %
- tracking lost rate before/after
- FPS
- crop ratio

#### PC GPU

- Batch process 3–5 videos
- Generate before/after comparison

#### Deliverable

- videos/before_after_stabilization.mp4
- reports/stabilization_results.md

### Day 27 — Final demo script

#### Laptop

Chuẩn bị demo video 3–5 phút:

- Part 1: Problem statement
- Part 2: Architecture
- Part 3: Marker landing / visual servoing
- Part 4: Python perception → C++ control
- Part 5: MAVLink message modes
- Part 6: CPU-limited stress test
- Part 7: YOLO tracking + ONNX/OpenVINO benchmark
- Part 8: Project phụ stabilization before/after
- Part 9: Results + limitations

Tạo:

- docs/DEMO_SCRIPT.md

#### PC GPU

- Render charts final
- Export images cho README

#### Deliverable

- DEMO_SCRIPT.md
- final charts
- final videos draft

### Day 28 — README polish + interview notes

#### Laptop

README chính phải có:

1. One-line project summary
2. Why this project
3. Architecture diagram
4. Features
5. Quick start
6. Run modes
7. Evaluation
8. Results table
9. Robustness tests
10. Limitations
11. Future work
12. Links to reports/videos

Tạo INTERVIEW_NOTES.md:

- Vì sao chọn AprilTag/ArUco làm core?
- Vì sao YOLO chỉ là extension?
- Vì sao tách Python perception và C++ control?
- Vì sao dùng LANDING_TARGET?
- Khi nào dùng SET_POSITION_TARGET_LOCAL_NED?
- CPU 20% thì hệ thống phản ứng thế nào?
- Nếu bay thật cần thêm gì?

#### PC GPU

- Hỗ trợ Review System metrics trên Laptop.
- Không train nữa.
- Chỉ sửa chart/report/model card.

#### Deliverable

- README.md Release Candidate 1
- INTERVIEW_NOTES.md

### Day 29 — Clean clone test

#### Laptop

Test như người lạ:

```bash
cd /tmp
git clone <your_repo>
cd edge-vision-uav-landing
bash scripts/setup.sh
bash scripts/run_all_tests.sh
```

Checklist:

- [ ] Không thiếu file
- [ ] Không hard-code absolute path
- [ ] README chạy được
- [ ] Model path đúng
- [ ] Config path đúng
- [ ] Docker hoặc local setup chạy được
- [ ] Reports generate được

#### PC GPU

- Verify final artifacts
- Backup release folder

#### Deliverable

- CLEAN_CLONE_TEST.md
- Fix toàn bộ lỗi setup

### Day 30 — Final release

#### Laptop

Final release:

- Git tag: v1.0-portfolio
- README final
- TECHNICAL_DESIGN final
- RESULTS final
- LIMITATIONS final
- Demo video final
- Project phụ final

Tạo PORTFOLIO_SUMMARY.md:

- Project 1: Edge Vision Precision Landing & AI Target Tracking for UAV SITL
  - Core proof:
    - Perception-control loop
    - C++ control path
    - MAVLink message design
    - Edge inference benchmark
    - Robustness under CPU constraint
    - Reproducible tests
- Project 2: Gimbal-Aware Video Stabilization & Tracking Quality Analyzer
  - Core proof:
    - Classical CV
    - Camera motion estimation
    - Stabilization
    - Tracking quality metric

#### PC GPU

- Archive final models
- Archive training logs
- Archive benchmark CSVs

#### Deliverable cuối cùng

- [ ] Repo chính public/private ready
- [ ] Repo phụ ready
- [ ] Demo video 3–5 phút
- [ ] Technical Design Document
- [ ] Results Report
- [ ] Robustness Report
- [ ] Model Card
- [ ] Dataset Manifest
- [ ] Clean clone test pass

## 12. Quality Gates tổng hợp

### Gate 1 — Day 7
Goal: Có perception + PID + replay baseline.
Pass:
- Detect marker và tính error.
- PID offline chạy.
- Replay + noise/blur/occlusion hoạt động.
- PX4/Gazebo hoặc fallback rõ ràng.
- ML: COCO8 smoke test, manifest draft, VisDrone baseline train (`TRN_001`) bắt đầu/xong. Dataset license/nguồn được verify.

### Gate 2 — Day 14
Goal: Có closed-loop simulation + Tracking v0.1.
Pass:
- Landing/centering simulation chạy.
- State machine + IPC prototype chạy.
- Robustness v0.1 có kết quả.
- ML: Domain-gap report, Public vs Finetuned, ONNX benchmark bước đầu, Tracking metrics trên held-out set. Có ML Candidate v0.1.

### Gate 3 — Day 21
Goal: Không còn là Python-only demo. Có C++ control path.
Pass:
- C++ PID, C++ failsafe, C++ MAVLink bridge (chưa cần send thực).
- Python → C++ IPC chạy được.
- CPU-limited stress test (Python vs Hybrid C++).
- ML: Hoàn tất Release Candidate. Chuẩn bị Multi-seed validation.
- CV Project 2: Có pipeline đầu tiên.

### Gate 4 — Day 30
Goal: Portfolio product release-ready.
Pass:
- Chạy được từ clean clone (cả system test và evaluation).
- Có report (RESULTS, TECH DESIGN), metrics, video demo.
- Có limitation chân thực.
- Có Docker/scripts.
- Cả 2 project liên quan UAV/CV/Edge hoàn tất artifacts.
- Minh chứng đủ 5 core competencies (AI/CV, Edge AI, UAV/Robotics, Embedded/C++, Product engineering).

## 13. Fallback plan để không vỡ tiến độ

### Nếu PX4/Gazebo camera stream quá khó

Không dừng project. Chuyển sang:

- Hybrid SITL:
  - PX4/Gazebo dùng để chứng minh environment/offboard concept
  - Vision dùng replay video/frame
  - C++ control sinh MAVLink-compatible command log
  - Report ghi rõ: full camera bridge là future work

### Nếu MAVLink integration thật không xong

Giữ:

- C++ MAVLink message builder
- LANDING_TARGET / SET_POSITION_TARGET_LOCAL_NED field mapping
- Command log
- Offboard design document

Không claim “đã bay closed-loop PX4 thật”.

### Nếu YOLO train không đạt mAP tốt

Giữ:

- pretrained YOLO tracking
- custom small fine-tune
- benchmark ONNX/OpenVINO
- ghi limitation về dataset

Project vẫn mạnh vì core là precision landing + edge deployment.

### Nếu OpenVINO lỗi

Giữ:

- PyTorch vs ONNX Runtime benchmark
- OpenVINO section là attempted/future

Không để OpenVINO làm block chính.

### Nếu C++ MAVLink quá tốn thời gian

Ưu tiên:

1. C++ PID
2. C++ failsafe
3. C++ control loop timing
4. MAVLink message field mapping/log

C++ control/failsafe quan trọng hơn full MAVLink send thật trong 30 ngày.

## 14. Lịch chạy PC GPU qua đêm

- Mỗi tối 22:00
  - Chọn experiment
  - Ghi EXP_ID
  - Start training/benchmark
- Qua đêm: Train hoặc benchmark
- Sáng hôm sau:
  - Kiểm tra logs
  - Lưu metrics
  - Quyết định keep/drop

### Naming & Lưu trữ

- Các thử nghiệm sử dụng prefix như `SMOKE_`, `TRN_`, `FT_`, `BENCH_`, `TRACK_`, `SYS_`.

### File cần lưu mỗi experiment

```text
experiments/EXP_XXX/
├── config.yaml
├── command.txt
├── results.csv
├── metrics.json
├── model.pt
├── model.onnx
└── notes.md
```

## 15. Phân loại ưu tiên kiến thức cho portfolio

### Must-have — bắt buộc xong

1. PX4/Gazebo hoặc workflow SITL dựa trên replay/video
2. AprilTag/ArUco detection
3. PID visual servoing logic
4. Precision landing simulation hoặc landing-target centering simulation
5. Robustness tests: noise, blur, occlusion, delay
6. YOLO target tracking extension
7. ONNX/OpenVINO benchmark
8. Technical Design Document + Results Report
9. GitHub repo sạch + Docker + video demo

### Should-have — nên có

1. ROS 2 node architecture (đủ cho architecture, không nhất thiết full launch system)
2. MAVLink LANDING_TARGET message
3. Replay-based testing
4. Gimbal-aware video stabilization project
5. DVC dataset versioning (nếu muốn tăng tính chuyên nghiệp)
6. MLflow experiment tracking và model lifecycle management
7. GitHub Actions CI cho build/test

### Could-have — chỉ làm nếu còn thời gian

1. LQR controller
2. ROS 2 full launch system hoàn chỉnh
3. Multi-object tracking nâng cao
4. OpenVINO INT8 quantization
5. Web dashboard
6. Synthetic data generation nâng cao

> Các mục DVC, MLflow và GitHub Actions không phải blocker của roadmap 30 ngày; chúng là nâng cấp để tăng tính chuyên nghiệp của portfolio, nhưng không nên làm chậm core delivery.

## 16. Roadmap rút gọn theo dòng thời gian

- Day 01: Scope, repo, requirements
- Day 02: OpenCV reader + marker detection
- Day 03: Camera calibration + pose estimation
- Day 04: PID offline
- Day 05: Replay + fault injection
- Day 06: PX4/Gazebo setup
- Day 07: Gate 1
- Day 08: MAVLink design + state machine
- Day 09: Closed-loop 2D simulation
- Day 10: IPC schema
- Day 11: Landing simulation v0.1
- Day 12: Robustness + CPU limit baseline
- Day 13: YOLO tracking + ONNX
- Day 14: Gate 2
- Day 15: Refactor + CMake skeleton
- Day 16: C++ PID
- Day 17: C++ failsafe
- Day 18: C++ MAVLink bridge
- Day 19: Python → C++ IPC
- Day 20: CPU-limited hybrid stress test
- Day 21: Project phụ stabilization + Gate 3
- Day 22: Robustness test suite v1
- Day 23: Technical Design Document
- Day 24: Results Report
- Day 25: Docker/reproducibility
- Day 26: Project phụ finalize
- Day 27: Demo script
- Day 28: README + interview notes
- Day 29: Clean clone test
- Day 30: Final release

## 17. Trọng tâm cần giữ trong suốt 30 ngày

Roadmap này không nhằm tạo “một app chạy được một lần”. Nó nhằm chứng minh 5 năng lực:

1. AI/CV:
   - YOLO, OpenCV, ArUco/AprilTag, tracking, metrics
2. Edge AI:
   - ONNX, OpenVINO, latency, FPS, CPU/RAM, constrained runtime
3. UAV/Robotics:
   - PX4/Gazebo/SITL, MAVLink LANDING_TARGET, SET_POSITION_TARGET_LOCAL_NED
4. Embedded/Firmware awareness:
   - C++ PID, C++ failsafe, C++ MAVLink bridge, CMake, timing/jitter
5. Product engineering:
   - Requirements, risk register, test plan, robustness tests, reports, reproducibility

### Đích cuối cùng của 30 ngày

Một sản phẩm mô phỏng chạy trên laptop, có kiến trúc rõ, có C++ control path, có AI inference benchmark, có robustness test, có report định lượng, có video demo, và có limitation trung thực.