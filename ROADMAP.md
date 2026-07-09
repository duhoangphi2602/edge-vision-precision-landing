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

- Precision Landing core: AprilTag/ArUco + camera pose/target error.
- AI extension: YOLO target tracking + ONNX/OpenVINO edge benchmark.
- Control layer: C++ PID + failsafe + MAVLink.
- Perception layer: Python OpenCV/YOLO/ONNX.
- Communication: Python perception → C++ control qua UDP/TCP/Unix socket.
- MAVLink messages: LANDING_TARGET và SET_POSITION_TARGET_LOCAL_NED.
- Simulation: PX4/Gazebo SITL hoặc hybrid replay-SITL nếu camera bridge mất thời gian.
- Hardware constraint: cpulimit, Docker CPU/memory limit, stress test.

LANDING_TARGET là MAVLink message dùng để gửi vị trí target từ vision/positioning system tới autopilot, với broadcast rate khuyến nghị ban đầu khoảng 10–50 Hz tùy tốc độ landing và độ chính xác mong muốn. SET_POSITION_TARGET_LOCAL_NED dùng để gửi setpoint vị trí/vận tốc/gia tốc trong local NED frame, phù hợp khi bạn tự tính velocity command bằng PID. PX4 Offboard cần stream setpoint liên tục; tài liệu PX4 v1.12 ghi setpoints phải được stream >2 Hz trước và trong khi dùng Offboard mode.

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

## 5. Chỉ số mục tiêu sau 30 ngày

| Nhóm | Metric | Mục tiêu thực tế trong 30 ngày |
|---|---|---|
| Precision landing / centering | Final error | ≤ 50 cm trong mô phỏng hoặc ≤ 30 px nếu chỉ pixel-loop |
| Control | Overshoot | ≤ 25% |
| Control | Settling time | ≤ 5–8 s |
| Robustness | Recovery after 1s occlusion | ≤ 2 s |
| Edge inference | YOLO ONNX CPU FPS | ≥ 10–15 FPS |
| Edge inference | P95 latency | ≤ 100–150 ms |
| C++ control | Control loop rate | 30–50 Hz ổn định |
| C++ control | Failsafe reaction | ≤ 200 ms sau timeout |
| Resource constraint | CPU-limited mode | Perception giảm FPS nhưng control/failsafe không chết |
| Stabilization project | Jitter reduction | ≥ 30% |
| Stabilization project | Tracking lost rate reduction | ≥ 20% |

Ultralytics hỗ trợ export YOLO sang ONNX/OpenVINO/TensorRT và nhiều format khác; tài liệu export cũng nhấn mạnh ONNX/OpenVINO có thể dùng cho CPU deployment và cung cấp Python/CLI export. ONNX Runtime hỗ trợ train bằng framework khác rồi deploy vào C#/C++/Java app, đồng thời áp dụng graph optimization và execution providers để cải thiện inference. OpenVINO là toolkit để deploy high-performance AI trên cloud, AI PC, edge devices và hỗ trợ convert/optimize/run inference trên Intel hardware.

## 6. Phân vai 2 máy

### Laptop — vai trò “System Engineer”

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

### PC GPU — vai trò “ML Engineer”

PC GPU tập trung vào:

- Dataset UAV / VisDrone / custom subset
- YOLO training
- Data augmentation
- Evaluation: mAP, precision, recall
- Export ONNX
- Benchmark PyTorch vs ONNX Runtime vs OpenVINO
- Batch evaluation
- Generate plots / reports
- Overnight training 24/24

## 7. Quy tắc vận hành mỗi ngày

Mỗi ngày phải có 4 output nhỏ:

1. Code commit
2. Log hoặc metric mới
3. Một file note trong daily_logs/day_xx.md
4. Quyết định ngày mai dựa trên lỗi hôm nay

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
mkdir -p datasets models experiments logs scripts reports
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

#### PC GPU

Chuẩn bị YOLO baseline:

- Cài Ultralytics
- Tải một subset nhỏ dataset UAV hoặc chuẩn bị video tự quay
- Tạo dataset.yaml
- Train thử YOLO nano/small trên subset nhỏ

Lệnh mẫu:

```bash
yolo detect train model=yolo11n.pt data=dataset.yaml imgsz=640 epochs=10 batch=16
```

#### Deliverable

- Laptop: video marker detection overlay, CSV log detection
- PC GPU: YOLO baseline training chạy được, metrics sơ bộ

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
- Convert tvec sang relative x/y/z error
- So sánh pixel error vs metric error

Calibration có thể làm theo 2 hướng:

- Option A: Webcam thật + checkerboard/Charuco board
- Option B: Synthetic camera intrinsics nếu chỉ dùng simulation/replay

#### PC GPU

Training baseline v0.1:

- Train YOLO model v0.1
- Lưu best.pt
- Lưu results.csv
- Lưu confusion matrix nếu có

#### Deliverable

- pose_estimator.py chạy được
- calibration_report.md có thông số camera
- YOLO baseline v0.1

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

Chạy 2 experiment:

- EXP-001: YOLO nano, imgsz=416
- EXP-002: YOLO nano, imgsz=640

Mục tiêu:

- So sánh accuracy vs speed
- Ghi lại model size

#### Deliverable

- PID offline simulation plot
- tests/python/test_pid_controller.py pass
- EXP-001/EXP-002 log

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

Tạo evaluation script:

- scripts/eval_yolo.py
- reports/yolo_v0_1_report.md

Output:

- precision
- recall
- mAP@50
- mAP@50:95 nếu có
- confusion matrix

#### Deliverable

- Replay test chạy bằng config
- Fault injection hoạt động
- YOLO report v0.1

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

Chạy overnight training:

- YOLO v0.2 với augmentation nhẹ
- Lưu logs

#### Deliverable

- PX4/Gazebo chạy được hoặc có lỗi được ghi rõ
- SITL_SETUP.md
- YOLO v0.2 training job đang chạy

### Day 7 — Gate 1: Foundation review

#### Laptop

Dọn repo:

- README quick start sơ bộ
- WEEK1_REPORT.md
- Video 30–60s: marker detection + PID overlay
- Git tag: week1-foundation

#### PC GPU

- Chọn model YOLO tốt nhất hiện tại
- Export ONNX thử

Ultralytics export hỗ trợ Python API như model.export(format="onnx") và nhiều option như imgsz, dynamic, simplify, opset.

#### Gate 1 phải đạt

- [ ] ArUco/AprilTag detection chạy được
- [ ] Pixel error tính đúng
- [ ] Pose estimation có bản đầu
- [ ] PID offline chạy được
- [ ] Replay + fault injection chạy được
- [ ] PX4/Gazebo ít nhất khởi động được
- [ ] YOLO baseline có model + log

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

MAVLINK_DESIGN.md phải có 2 mode:

- Mode 1: LANDING_TARGET
  - Purpose: Vision system acts like external landing target sensor.
  - Sends target position to autopilot.
  - Fields to study:
    - time_usec
    - target_num
    - frame
    - angle_x / angle_y
    - distance
    - x, y, z
    - q
    - type
    - position_valid
- Mode 2: SET_POSITION_TARGET_LOCAL_NED
  - Purpose: External controller computes velocity setpoint.
  - Sends vx/vy/vz/yaw_rate command to autopilot.

State machine:

```text
SEARCH -> TRACK -> APPROACH -> DESCEND -> LAND -> ABORT/HOVER
```

#### PC GPU

- Train YOLO v0.3 với augmentation: blur, brightness, scale, mosaic nếu phù hợp
- Lưu config experiment

#### Deliverable

- MAVLINK_DESIGN.md
- state machine chạy được bằng test giả lập
- YOLO v0.3 training job

### Day 9 — Closed-loop 2D simulation

#### Laptop

Tạo:

- src/evaluation/landing_2d_sim.py
- scripts/run_2d_landing_sim.py
- reports/closed_loop_2d_v0.md

Simulation đơn giản:

- State: drone_x, drone_y, target_x, target_y, velocity_x, velocity_y
- Controller: PID(error_x, error_y)
- Disturbance: wind_x, wind_y, delay_ms
- Metrics:
  - final_error
  - max_error
  - overshoot
  - settling_time
  - time_to_center
  - command_saturation_ratio

#### PC GPU

Benchmark ban đầu:

- PyTorch inference FPS
- ONNX Runtime inference FPS
- Latency P50/P95

ONNX Runtime có thể cải thiện inference nhờ graph optimizations và hardware-specific execution providers.

#### Deliverable

- closed_loop_2d_v0.md có plot error over time
- benchmark_pytorch_vs_onnx_v0.csv

### Day 10 — Python perception → control observation schema

#### Laptop

Tạo schema chung:

- src/ipc/target_observation_schema.md
- src/ipc/udp_sender.py
- src/ipc/udp_receiver_stub.py

Message format:

```json
{
  "timestamp_ns": 0,
  "source": "aruco|apriltag|yolo",
  "detected": true,
  "target_id": 1,
  "confidence": 0.98,
  "u": 320.0,
  "v": 240.0,
  "error_x": 0.0,
  "error_y": 0.0,
  "x_m": 0.12,
  "y_m": -0.05,
  "z_m": 1.8,
  "latency_ms": 18.5
}
```

Yêu cầu:

- Perception gửi observation qua UDP localhost
- Receiver đọc và in latency
- Log dropped message count

#### PC GPU

- Chạy YOLO tracking trên video UAV hoặc video test
- Log target ID, center, confidence

#### Deliverable

- UDP IPC prototype
- ipc_latency_log.csv
- YOLO tracking overlay video

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

- Export best model sang ONNX
- Test dynamic/static input
- Test imgsz 416 vs 640

#### Deliverable

- 20 run landing simulation
- bảng final error / overshoot / settling time
- best.onnx đầu tiên

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

Benchmark:

- PyTorch
- ONNX Runtime
- OpenVINO nếu máy/laptop hỗ trợ

OpenVINO phù hợp để benchmark hướng CPU/AI PC/edge device vì tài liệu chính thức mô tả nó như toolkit deploy high-performance AI trên AI PCs, edge devices và Physical AI.

#### Deliverable

- yolo_tracking mode chạy được
- benchmark_runtime_v0.csv
- video YOLO target tracking

### Day 14 — Gate 2: Integration review

#### Laptop

Tạo:

- reports/WEEK2_REPORT.md
- videos/week2_precision_landing_v0.mp4
- videos/week2_yolo_tracking_v0.mp4

#### PC GPU

- Đóng băng model candidate v0.3
- Lưu best.pt, best.onnx
- Lưu training config

#### Gate 2 phải đạt

- [ ] Landing/centering closed-loop simulation chạy được
- [ ] State machine có bản đầu
- [ ] MAVLink message design rõ
- [ ] IPC Python → receiver chạy được
- [ ] Robustness test v0.1 có kết quả
- [ ] CPU-limited baseline có số liệu
- [ ] YOLO tracking mode chạy được
- [ ] ONNX benchmark có số liệu

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

- Chạy final training candidate nếu model chưa ổn
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
- YOLO final metrics draft

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

- Export ONNX final
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

Benchmark ONNX Runtime:

- threads=1
- threads=2
- threads=4
- imgsz=416
- imgsz=640

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

- Batch chạy benchmark PyTorch/ONNX/OpenVINO
- Generate plots

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

- Không train thêm nếu không cần
- Tập trung export charts và finalize ML report

#### Deliverable

- ab_test_python_vs_cpp_control.md
- cpu_limited_stress_report.md

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

- Xuất final ML metrics
- Đóng băng model: best.pt, best.onnx, openvino_model/

#### Deliverable

- robustness_report_v1.md
- final model artifacts

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

- Cập nhật MODEL_CARD.md
- Cập nhật DATASET_MANIFEST.md

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

- Không train nữa
- Chỉ sửa chart/report/model card

#### Deliverable

- README.md gần final
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

- Detect marker
- Tính target error
- PID offline chạy
- Replay + noise/blur/occlusion hoạt động
- YOLO baseline có model

### Gate 2 — Day 14

Goal: Có closed-loop simulation + YOLO/ONNX baseline.

Pass:

- Landing/centering simulation chạy
- State machine có bản đầu
- Robustness v0.1 có kết quả
- YOLO tracking chạy
- ONNX benchmark có số liệu

### Gate 3 — Day 21

Goal: Không còn là Python-only demo.

Pass:

- C++ PID
- C++ failsafe
- C++ MAVLink bridge/message builder
- Python → C++ IPC
- CPU-limited stress test
- A/B Python-only vs hybrid
- Project phụ stabilization v0.1

### Gate 4 — Day 30

Goal: Portfolio product.

Pass:

- Chạy được từ clean clone
- Có report
- Có metrics
- Có video
- Có limitations
- Có Docker/scripts
- Có 2 project liên quan UAV/CV/Edge

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

### Experiment naming

- EXP_001_yolo_n_416_baseline
- EXP_002_yolo_n_640_baseline
- EXP_003_yolo_n_640_aug_blur_noise
- EXP_004_yolo_s_640_aug
- EXP_005_onnx_cpu_threads
- EXP_006_openvino_cpu

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