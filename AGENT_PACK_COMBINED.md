# Edge UAV Agent Pack — Combined Markdown



---

# File: AGENTS.md

# AGENTS.md — IDE Agent Operating Manual

## Mission

You are the implementation agent for the 30-day portfolio product:

**Project 1:** Edge Vision Precision Landing & AI Target Tracking for UAV SITL  
**Project 2:** Gimbal-Aware Video Stabilization & Tracking Quality Analyzer

The goal is not to create a shallow demo. The goal is to build a measurable, reproducible, engineering-grade portfolio system that proves capability in:

1. AI / Computer Vision
2. Edge AI deployment
3. UAV / robotics simulation
4. C++ control and embedded-style software
5. Product engineering: requirements, tests, reports, reproducibility

## Primary Roadmap Source

Follow `roadmap.md` as the master schedule. Do not skip Quality Gates. Do not optimize one topic so much that another roadmap block is neglected.

When in doubt, preserve the project balance:

- Precision landing / ArUco / AprilTag / PID / SITL: 45%
- YOLO / Edge AI / ONNX / OpenVINO benchmark: 25%
- Robustness / testing / reports: 20%
- Docker / CI / polish: 10%

## Ubuntu Execution Target

Prefer this environment for new setup:

- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- Gazebo Harmonic
- PX4 v1.16+ or current stable
- Python virtual environment
- C++17 with CMake
- Docker / Docker Compose
- Optional: OpenVINO on Intel CPU/iGPU/NPU
- Optional PC GPU training environment with CUDA/PyTorch

If the host is Ubuntu 22.04 LTS, use:

- ROS 2 Humble
- PX4 v1.16-compatible setup
- Gazebo Harmonic or Gazebo Classic fallback where applicable

Do not mix ROS 2 Humble with Ubuntu 24.04 or ROS 2 Jazzy with Ubuntu 22.04 unless explicitly using a container.

## Architecture to Preserve

```text
Camera / Replay / Gazebo
        |
        v
Python Perception Process
OpenCV / ArUco / AprilTag / YOLO / ONNX
        |
        | UDP/TCP/Unix Socket target_observation
        v
C++ Control Process
PID / Failsafe / MAVLink-compatible message builder
        |
        v
PX4 / SITL / Command Log
        |
        v
Evaluation + Reports
```

## Non-Negotiable Rules

1. Every feature must produce logs or measurable metrics.
2. Every module must have a clear input/output.
3. Python perception and C++ control must remain decoupled after Week 3.
4. The C++ control node must never trust stale observations.
5. If full PX4 camera integration fails, switch to Hybrid SITL but document the limitation.
6. Do not claim real-world flight readiness.
7. Never hard-code absolute paths.
8. All scripts must run from the repository root.
9. Prefer reproducible scripts over manual steps.
10. Update `daily_logs/day_XX.md` at the end of each day.

## Daily Work Protocol

For each day:

1. Read the relevant Day section in `roadmap.md`.
2. Read `TASK_BOARD_DAY1.md` or the current day's task file.
3. Implement only the current day tasks unless a dependency requires earlier cleanup.
4. Run tests or at least a smoke test.
5. Record metrics.
6. Commit with a clear message.
7. Update daily log.

## Commit Style

```text
day01: initialize repo and requirements
day02: add aruco marker detection pipeline
day04: implement pid controller baseline
day16: port pid controller to c++
day20: add cpu-limited hybrid stress tests
```

## Definition of Done

A task is done only when:

- Code exists
- It runs
- Output is logged
- Failure mode is handled
- Documentation is updated
- Result is reproducible



---

# File: RULES.md

# RULES.md — Hard Rules for the 30-Day Roadmap

## 1. Scope Rules

The project must remain aligned with the roadmap:

- Project 1 is the main project.
- Project 2 is a supporting CV project.
- Do not replace precision landing with a random YOLO demo.
- Do not spend excessive time on ROS 2 if MAVLink/IPC/control proof is not done.
- Do not spend excessive time on model training if the system pipeline is not integrated.

## 2. Technical Priority Rules

Priority order for Project 1:

1. Reproducible repo structure
2. OpenCV marker detection
3. Target error estimation
4. PID visual servoing
5. Replay/fault injection
6. C++ PID and failsafe
7. Python perception → C++ control IPC
8. MAVLink message mapping
9. YOLO/ONNX/OpenVINO edge benchmark
10. Robustness tests and reports
11. Docker/clean clone/test release

## 3. Ubuntu Rules

- Use Ubuntu LTS only.
- Prefer Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic for new installations.
- Use Ubuntu 22.04 + ROS 2 Humble if the laptop is already on 22.04.
- Do not install large robotics stacks blindly into a dirty host OS.
- Use venv for Python.
- Keep PX4 source outside the project repo, for example `~/PX4-Autopilot`.
- Keep datasets outside the repo, for example `~/Datasets`.
- Never commit datasets, model weights, logs, or videos unless intentionally small placeholders.

## 4. Python Rules

- Python is for perception, training, evaluation, plotting, and scripts.
- Use type hints when practical.
- Keep functions small and testable.
- All scripts must support CLI arguments.
- Use config YAML for thresholds and paths.
- Log CSV/JSON outputs for metrics.

## 5. C++ Rules

- C++ is for PID, failsafe, control loop timing, MAVLink-compatible message building, and IPC receiver.
- Use C++17.
- Build with CMake.
- Keep headers in `include/`.
- Keep implementation in `src/`.
- Keep tests in `tests/`.
- Do not over-engineer templates/classes early.
- First prove correctness and timing.

## 6. MAVLink Rules

Study and map these messages:

- `LANDING_TARGET`
- `SET_POSITION_TARGET_LOCAL_NED`

Implement at least:

- Field mapping
- Message builder or payload builder
- Log output
- Documentation explaining when each mode is used

Full autopilot communication is valuable but not required if it blocks the 30-day roadmap.

## 7. Robustness Rules

Robustness tests must include:

- Noise
- Blur
- Occlusion
- Delay
- Frame drop
- CPU limit
- Stale observation
- False target if possible

Every robustness test must produce:

- Pass/fail
- Latency
- Target lock rate
- Recovery time
- Unsafe command count

## 8. Reporting Rules

Every final claim must be backed by a number.

Bad:

```text
The system runs well.
```

Good:

```text
The marker pipeline achieved 28 FPS and P95 latency of 42 ms on Ubuntu 24.04 laptop CPU.
```

## 9. Honesty Rules

Do not claim:

- Real drone flight validated
- Production safety
- Industrial readiness
- Hardware-in-the-loop validation

Unless those tests are actually performed.

Use:

```text
Validated in SITL/replay under controlled robustness tests.
```



---

# File: PROJECT_CONTEXT.md

# PROJECT_CONTEXT.md — Product Context for Agent

## Product Name

**Edge Vision Precision Landing & AI Target Tracking for UAV SITL**

## Secondary Product

**Gimbal-Aware Video Stabilization & Tracking Quality Analyzer**

## Why This Product Exists

The project demonstrates that the developer can build more than a YOLO demo. It proves a measurable perception-control system under resource constraints, using simulation and replay when real drone hardware is unavailable.

## Real-World Problem

UAV precision landing and target tracking are difficult because of:

- Camera noise
- Motion blur
- Partial occlusion
- Communication delay
- Frame drop
- Wind/disturbance
- CPU limitation
- False target detection
- Target loss during descent
- Camera calibration error

## Product Hypothesis

A system using:

- ArUco/AprilTag for reliable precision landing target detection
- YOLO for AI target tracking extension
- ONNX/OpenVINO for edge inference
- C++ PID/failsafe for control
- MAVLink-compatible message mapping
- Robustness tests under simulated hardware constraints

can demonstrate practical UAV perception and edge-AI engineering capability on laptop-only hardware.

## Core Architecture

```text
Camera / Replay / Gazebo
        |
        v
Python Perception
  - OpenCV
  - ArUco / AprilTag
  - YOLO / ONNX
        |
        v
IPC target_observation
        |
        v
C++ Control
  - PID
  - Failsafe
  - MAVLink-compatible message builder
        |
        v
SITL / Command Log / Evaluation
```

## Main Repositories

Recommended workspace:

```text
~/Projects/
├── edge-vision-uav-landing/
├── edge-ai-training/
└── gimbal-video-stabilization-analyzer/

~/PX4-Autopilot/
~/Datasets/
```

## What Must Be Proved

1. Detection works.
2. Target error is computed.
3. Control command is generated.
4. Stale target does not create unsafe command.
5. Edge inference is benchmarked.
6. CPU limitation does not collapse failsafe.
7. Results are reproducible.
8. Limitations are documented.

## Final Deliverables

- README
- Technical Design Document
- Problem Statement
- Requirements
- Test Plan
- Results Report
- Limitations
- Model Card
- Dataset Manifest
- Dockerfile / docker-compose
- Test scripts
- Demo video
- Clean clone test



---

# File: UBUNTU_ENVIRONMENT.md

# UBUNTU_ENVIRONMENT.md — Ubuntu Setup and Execution Layer

## Recommended OS Matrix

### Recommended for a clean new setup

```text
Ubuntu 24.04 LTS
ROS 2 Jazzy
Gazebo Harmonic
PX4 v1.16+ or current stable
Python 3.12 venv
C++17 / CMake / Ninja
Docker / Docker Compose
```

### Alternative if the machine already uses Ubuntu 22.04

```text
Ubuntu 22.04 LTS
ROS 2 Humble
Gazebo Harmonic or Gazebo Classic fallback
PX4 v1.16-compatible setup
Python 3.10 venv
C++17 / CMake / Ninja
Docker / Docker Compose
```

## Do Not Mix

Avoid:

```text
Ubuntu 24.04 + ROS 2 Humble directly on host
Ubuntu 22.04 + ROS 2 Jazzy directly on host
PX4 installed into random dirty environment
System Python pip install for project packages
```

Use Docker if a mismatched stack is required.

## Directory Layout

```text
~/Projects/
├── edge-vision-uav-landing/
├── edge-ai-training/
└── gimbal-video-stabilization-analyzer/

~/PX4-Autopilot/
~/Datasets/
~/Models/
```

## Base Packages

```bash
sudo apt update
sudo apt install -y   git git-lfs curl wget unzip zip   build-essential cmake ninja-build pkg-config   gcc g++ gdb clang-format cppcheck   python3 python3-pip python3-venv python3-dev   ffmpeg v4l-utils   libopencv-dev   cpulimit htop tree jq   docker.io docker-compose-v2
```

Add current user to Docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

## Python Virtual Environment

Inside project repo:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
```

Recommended `requirements.txt` initial content:

```text
numpy
opencv-python
opencv-contrib-python
pyyaml
pytest
pytest-cov
matplotlib
pandas
onnx
onnxruntime
ultralytics
psutil
rich
```

If OpenVINO is needed:

```bash
pip install openvino
```

## C++ Build

```bash
cmake -S src/control_cpp -B build/control_cpp -G Ninja
cmake --build build/control_cpp
./build/control_cpp/test_pid_controller
```

## PX4 Setup Rule

Keep PX4 outside the repo:

```bash
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
bash ./Tools/setup/ubuntu.sh
```

Restart after PX4 setup if the installer requests it.

## Gazebo GUI Notes

If Gazebo GUI has display issues:

- Try logging into an X11 session.
- Try headless or replay mode first.
- Do not block the roadmap on GUI rendering.
- Record the limitation in `LIMITATIONS.md`.

## Resource Constraint Testing

Use `cpulimit`:

```bash
cpulimit -l 20 -- python3 scripts/run_perception.py --mode marker_landing
```

Use Docker CPU/memory limits:

```bash
docker run --cpus="0.5" --memory="1g" edge-uav-vision
```

## PC GPU Notes

On the PC GPU machine:

- Keep training workspace separate from the laptop system repo.
- Run overnight training jobs.
- Store experiment configs and logs.
- Export final models to `models/` in the main repo only after freezing.

Check GPU:

```bash
nvidia-smi
python3 -c "import torch; print(torch.cuda.is_available())"
```



---

# File: SKILLS_DEEP_DIVE.md

# SKILLS_DEEP_DIVE.md — Knowledge Blocks to Master During Implementation

## 1. Ubuntu / Linux Engineering

Must understand:

- Filesystem layout
- Permissions
- Process monitoring
- Environment variables
- Virtual environments
- Device access
- CPU/memory limits
- X11/Wayland display issues
- Shell scripts
- Logs

Practice:

```bash
htop
ps aux
tree
du -sh *
df -h
chmod +x scripts/*.sh
cpulimit -l 20 -- <command>
```

## 2. Git / Reproducibility

Must understand:

- Commit discipline
- Experiment logs
- Clean clone test
- No absolute paths
- No large datasets in Git
- Model artifacts versioning

Required files:

- `DATASET_MANIFEST.md`
- `MODEL_CARD.md`
- `CLEAN_CLONE_TEST.md`

## 3. Python Perception

Must understand:

- Video capture
- Frame timestamp
- Image resize
- BGR/RGB/HSV
- ArUco/AprilTag detection
- YOLO inference
- ONNX Runtime inference
- Logging CSV/JSON

Required modules:

- `video_reader.py`
- `aruco_detector.py`
- `apriltag_detector.py`
- `yolo_detector.py`
- `target_selector.py`
- `run_perception.py`

## 4. Camera Geometry

Must understand:

- Pixel coordinate
- Camera coordinate
- Intrinsic matrix
- Distortion coefficients
- Marker size
- Pose estimation
- Pixel error vs metric error

Minimum output:

```text
timestamp, detected, u, v, error_x, error_y, x_m, y_m, z_m
```

## 5. C++ Control

Must understand:

- PID
- Saturation
- Deadband
- Anti-windup
- Derivative filtering
- Loop timing
- Jitter
- Failsafe
- Stale observation rejection

Required modules:

- `pid_controller.hpp/.cpp`
- `failsafe_manager.hpp/.cpp`
- `control_node.cpp`

## 6. IPC

Must understand:

- UDP localhost
- Timestamp
- Message schema
- Dropped message
- Stale data
- Latency measurement

Required schema:

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

## 7. MAVLink Concepts

Must understand:

- MAVLink as lightweight UAV communication protocol
- `LANDING_TARGET`
- `SET_POSITION_TARGET_LOCAL_NED`
- Position frame vs velocity frame
- Timestamp
- Coordinate conventions
- Offboard setpoint streaming
- Failsafe behavior when setpoints stop

Minimum proof:

- Field mapping
- Message builder or payload builder
- Command log
- Documentation explaining which mode is used when

## 8. Edge AI

Must understand:

- PyTorch model
- YOLO export
- ONNX
- ONNX Runtime
- OpenVINO
- FPS
- P50/P95 latency
- Model size
- CPU/RAM usage
- Thread count benchmark
- Input size trade-off

Required benchmark table:

```text
Runtime, Model, Input size, FPS, P50 latency, P95 latency, CPU%, RAM MB
```

## 9. Robustness Testing

Must understand:

- Noise
- Blur
- Occlusion
- Delay
- Frame drop
- CPU limit
- False target
- Stale observation

Required output:

```text
Test case, pass/fail, recovery time, P95 latency, target lock rate, unsafe command count
```

## 10. Product Documentation

Must understand:

- Problem statement
- Requirements
- Design document
- Test plan
- Results
- Limitations
- Future work
- Honest claims



---

# File: IMPLEMENTATION_PLAN.md

# IMPLEMENTATION_PLAN.md — Agent Implementation Plan

## Principle

Implement the roadmap one day at a time. Do not jump ahead unless it is required to unblock today's tasks.

## Day 1 Implementation

### Laptop

1. Create repository structure.
2. Create all core documentation files.
3. Add initial README.
4. Add `requirements.txt`.
5. Add `.gitignore`.
6. Add `daily_logs/day_01.md`.
7. Commit.

### PC GPU

1. Create `edge-ai-training`.
2. Verify GPU.
3. Create experiment folder structure.
4. Create `EXP_PLAN.md`.
5. Create `DATASET_SOURCES.md`.

## Day 2 Implementation

1. Implement video reader.
2. Implement ArUco detection.
3. Add overlay.
4. Add CSV logging.
5. Add sample command in README.

## Day 3 Implementation

1. Implement calibration loader.
2. Implement pose estimator.
3. Add `camera.yaml`.
4. Generate calibration report.

## Day 4 Implementation

1. Implement Python PID.
2. Implement control metrics.
3. Add pytest.
4. Plot offline response.

## Day 5 Implementation

1. Implement replay source.
2. Implement fault injection.
3. Add config-driven test runner.

## Day 6 Implementation

1. Install/run PX4/Gazebo or document issue.
2. Create SITL setup guide.
3. Add fallback path.

## Day 7 Gate

1. Produce Week 1 report.
2. Record video.
3. Tag repository.

## Week 2 Implementation Summary

- State machine
- MAVLink design document
- Closed-loop 2D simulation
- IPC schema
- YOLO tracking mode
- ONNX benchmark
- Robustness v0.1

## Week 3 Implementation Summary

- CMake skeleton
- C++ PID
- C++ failsafe
- C++ MAVLink message builder
- Python → C++ UDP IPC
- CPU-limited hybrid stress test
- Project 2 stabilization v0.1

## Week 4 Implementation Summary

- Full robustness suite
- Technical Design Document
- Results Report
- Docker / reproducibility
- Project 2 finalization
- Demo script
- README polish
- Clean clone test
- Final release

## Implementation Rule

Each code module must have:

- Purpose comment
- Input/output description
- CLI or test command
- Failure handling
- Log output



---

# File: TASK_BOARD_DAY1.md

# TASK_BOARD_DAY1.md — Start Immediately

## Goal

Initialize the project so every following day has a stable base.

## Laptop Tasks

### 1. Create project

```bash
mkdir -p ~/Projects
cd ~/Projects
mkdir edge-vision-uav-landing
cd edge-vision-uav-landing
git init
```

### 2. Create folder structure

```bash
mkdir -p src/{perception,estimation,ipc,evaluation,utils}
mkdir -p src/control_cpp/{include,src,tests}
mkdir -p src/interface_cpp/{include,src,tests}
mkdir -p configs tests/{python,cpp} scripts reports logs videos models docs daily_logs
```

### 3. Create documentation files

```bash
touch README.md TECHNICAL_DESIGN.md PROBLEM.md REQUIREMENTS.md TEST_PLAN.md RESULTS.md LIMITATIONS.md
touch MODEL_CARD.md DATASET_MANIFEST.md CLEAN_CLONE_TEST.md PORTFOLIO_SUMMARY.md
touch daily_logs/day_01.md
```

### 4. Create development files

```bash
touch requirements.txt .gitignore
```

### 5. Initial `.gitignore`

```gitignore
.venv/
__pycache__/
*.pyc
build/
dist/
*.egg-info/
logs/
videos/
models/*.pt
models/*.onnx
models/*.engine
models/openvino_model/
datasets/
*.avi
*.mp4
*.bag
*.ulg
.DS_Store
.vscode/
```

### 6. Initial `requirements.txt`

```text
numpy
opencv-python
opencv-contrib-python
pyyaml
pytest
pytest-cov
matplotlib
pandas
onnx
onnxruntime
ultralytics
psutil
rich
```

### 7. Write `daily_logs/day_01.md`

```md
# Day 01

## Done
- Initialized repository.
- Created project structure.
- Created documentation files.

## Metrics
- FPS: N/A
- Latency: N/A
- Error: N/A
- CPU/RAM: N/A
- Test pass/fail: N/A

## Problems
- None yet.

## Decision
- Start with marker landing core before YOLO integration.

## Tomorrow
- Laptop: implement OpenCV video reader and ArUco detector.
- PC GPU: prepare YOLO training environment.
```

### 8. Commit

```bash
git add .
git commit -m "day01: initialize product repository and roadmap files"
```

## PC GPU Tasks

```bash
mkdir -p ~/Projects/edge-ai-training
cd ~/Projects/edge-ai-training
mkdir -p datasets models experiments logs scripts reports
nvidia-smi
python3 -c "import torch; print(torch.cuda.is_available())"
```

Create:

```bash
touch experiments/EXP_PLAN.md
touch datasets/DATASET_SOURCES.md
```

## Day 1 Done Criteria

- Main repo exists.
- Training workspace exists.
- Git commit exists.
- Daily log exists.
- Next day is unblocked.



---

# File: PROMPTS.md

# PROMPTS.md — Prompts for IDE Agent

## Prompt 1 — Start Day 1

```text
You are implementing the 30-day Edge Vision UAV roadmap. Read these files first: roadmap.md, AGENTS.md, RULES.md, PROJECT_CONTEXT.md, UBUNTU_ENVIRONMENT.md, TASK_BOARD_DAY1.md.

Today is Day 1. Do not jump ahead. Create the repository structure, documentation skeleton, requirements.txt, .gitignore, and daily log exactly as specified. Make no large design changes. After creating files, summarize what was created and list the next Day 2 tasks.
```

## Prompt 2 — Daily Execution

```text
Read roadmap.md and AGENTS.md. Implement only Day [XX]. Preserve the architecture: Python perception, C++ control, IPC boundary, MAVLink-compatible message design, metrics, and reproducibility. Do not optimize one area at the expense of the roadmap balance. For every file you create, explain its purpose and how to run or test it. Update daily_logs/day_[XX].md.
```

## Prompt 3 — Code Review

```text
Review the current implementation against RULES.md and roadmap.md. Check for: hard-coded paths, missing metrics, missing tests, unsafe stale target behavior, lack of logging, overuse of Python in control path, and missing documentation. Return a prioritized fix list.
```

## Prompt 4 — Ubuntu Setup

```text
Read UBUNTU_ENVIRONMENT.md. Generate the exact setup commands for this machine. First detect or ask for Ubuntu version. If Ubuntu 24.04, use ROS 2 Jazzy assumptions. If Ubuntu 22.04, use ROS 2 Humble assumptions. Do not mix ROS distributions across Ubuntu versions. Prefer venv and reproducible scripts.
```

## Prompt 5 — C++ PID Implementation

```text
Implement the C++ PID controller in src/control_cpp using C++17 and CMake. Include saturation, deadband, anti-windup, reset, and unit tests. Add a simple benchmark measuring update time over 100000 iterations. Do not implement MAVLink yet.
```

## Prompt 6 — C++ Failsafe Implementation

```text
Implement the C++ failsafe manager. It must reject stale observations, low-confidence observations, target loss longer than timeout, and commands outside limits. Add tests for each state transition.
```

## Prompt 7 — IPC Implementation

```text
Implement Python-to-C++ UDP IPC. Python perception sends target_observation JSON with timestamp_ns. C++ control_node receives, validates timestamp, computes PID command, and logs command output. Measure IPC latency, stale observation count, and control loop jitter.
```

## Prompt 8 — Robustness Test Runner

```text
Implement config-driven robustness tests from configs/test_cases.yaml. Support noise, blur, occlusion, delay, frame drop, and CPU-limit notes. Generate CSV and Markdown reports with pass/fail, P95 latency, target lock rate, recovery time, and unsafe command count.
```

## Prompt 9 — Documentation Fill

```text
Fill TECHNICAL_DESIGN.md, TEST_PLAN.md, RESULTS.md, and LIMITATIONS.md based only on implemented features and measured metrics. Do not claim real drone flight or production readiness. Clearly mark SITL/replay validation and known limitations.
```

## Prompt 10 — Final Audit

```text
Perform final audit for Day 30. Verify clean clone setup, scripts, README, metrics, reports, Docker, model paths, and limitations. Create CLEAN_CLONE_TEST.md and PORTFOLIO_SUMMARY.md. List any remaining gaps honestly.
```



---

# File: CODING_STANDARDS.md

# CODING_STANDARDS.md — Coding Standards

## Python

### Style

- Use Python 3.10+.
- Use type hints for public functions.
- Avoid global mutable state.
- Use `argparse` for scripts.
- Use YAML config files.
- Use CSV/JSON logs.

### Function Standard

Every major function should have a short docstring that explains:

- Purpose
- Inputs
- Outputs
- Failure behavior

### Logging

Use structured logs:

```text
timestamp_ns, frame_id, detected, confidence, error_x, error_y, latency_ms
```

### CLI Pattern

```bash
python scripts/run_perception.py --mode marker_landing --config configs/perception.yaml
```

## C++

### Standard

- C++17
- CMake
- No complex framework unless necessary
- Keep deterministic control code small
- Prefer explicit structs for data passing

### Folder Standard

```text
src/control_cpp/
├── CMakeLists.txt
├── include/
│   ├── pid_controller.hpp
│   └── failsafe_manager.hpp
├── src/
│   ├── pid_controller.cpp
│   ├── failsafe_manager.cpp
│   └── control_node.cpp
└── tests/
    ├── test_pid_controller.cpp
    └── test_failsafe_manager.cpp
```

### Control Code Rules

- Reject stale observations.
- Clamp commands.
- Separate perception confidence from control decision.
- Never send unsafe command when target is lost.
- Always log state transition.

## Config Naming

```text
configs/perception.yaml
configs/control.yaml
configs/faults.yaml
configs/test_cases.yaml
configs/edge_benchmark.yaml
```

## Script Naming

```text
scripts/run_perception.py
scripts/run_cpp_control.sh
scripts/run_replay_test.py
scripts/run_all_robustness_tests.py
scripts/generate_report.py
scripts/run_all_tests.sh
```

## Data Output Naming

```text
logs/YYYYMMDD_HHMMSS_<test_name>.csv
reports/<topic>_<version>.md
videos/<demo_name>.mp4
```

## Error Handling

Every script must fail with readable messages:

- Missing config
- Missing model
- Camera unavailable
- Invalid mode
- Output directory not writable

## Do Not Commit

- Large datasets
- Large model weights
- Long videos
- Virtual environments
- Build folders
- Temporary logs



---

# File: TESTING_VALIDATION.md

# TESTING_VALIDATION.md — Testing and Validation Plan

## Test Levels

### Level 1 — Unit Tests

Python:

- PID Python baseline
- Control metrics
- Fault injection
- Target selector
- Evaluation metrics

C++:

- PID
- Failsafe
- MAVLink-compatible payload builder
- Stale observation rejection

### Level 2 — Component Tests

- Video reader → detector
- Detector → target observation
- Python sender → C++ receiver
- C++ receiver → PID command
- PID command → message builder
- Fault injection → robustness report

### Level 3 — Integration Tests

- Marker detection replay
- Closed-loop 2D landing simulation
- Python perception + C++ control
- YOLO tracking mode
- ONNX benchmark mode

### Level 4 — Robustness Tests

Required cases:

```text
normal
noise_low
noise_high
blur_low
blur_high
occlusion_0_5s
occlusion_1s
occlusion_2s
delay_100ms
delay_200ms
frame_drop_10
frame_drop_20
cpu_limit_50
cpu_limit_20
cpu_20_occlusion_1s
false_target_optional
```

## Metrics

### Perception Metrics

- FPS
- P50 latency
- P95 latency
- Detection rate
- Target lock rate
- False positive count
- Lost target duration

### Control Metrics

- Final error
- Overshoot
- Settling time
- Steady-state error
- Control loop rate
- Control jitter P95
- Command saturation ratio
- Unsafe command count

### Edge Metrics

- Model size
- Runtime
- Input size
- FPS
- P50 latency
- P95 latency
- CPU usage
- RAM usage

## Pass/Fail Rules

A test passes when:

- It completes without crash.
- It produces logs.
- No unsafe command is generated.
- Required metrics are computed.
- Result is within threshold or explicitly marked as limitation.

## Example Test Case Format

```yaml
cases:
  - name: normal
    noise: 0
    blur: 0
    occlusion_s: 0
    delay_ms: 0
    frame_drop: 0
    cpu_limit: 100
    expected:
      unsafe_command_count: 0
      target_lock_rate_min: 0.85

  - name: occlusion_1s
    occlusion_s: 1.0
    expected:
      recovery_time_max_s: 2.0
      unsafe_command_count: 0
```

## Reports to Generate

- `reports/robustness_report_v1.md`
- `reports/edge_benchmark.md`
- `reports/control_ab_test.md`
- `reports/stabilization_results.md`



---

# File: METRICS_AND_REPORTS.md

# METRICS_AND_REPORTS.md — Metrics, Logs, and Report Schemas

## Perception Log Schema

```csv
timestamp_ns,frame_id,source,detected,target_id,confidence,u,v,error_x,error_y,x_m,y_m,z_m,latency_ms
```

## Control Log Schema

```csv
timestamp_ns,state,error_x,error_y,vx_cmd,vy_cmd,vz_cmd,yaw_rate_cmd,observation_age_ms,stale,unsafe_command
```

## IPC Log Schema

```csv
timestamp_ns,sent_ns,received_ns,ipc_latency_ms,message_size_bytes,dropped_count,stale_count
```

## Edge Benchmark Schema

```csv
runtime,model,input_size,device,threads,fps,p50_latency_ms,p95_latency_ms,cpu_percent,ram_mb,model_size_mb
```

## Robustness Report Schema

```csv
case_name,pass,final_error,overshoot,settling_time_s,target_lock_rate,recovery_time_s,p95_latency_ms,unsafe_command_count,notes
```

## Stabilization Report Schema

```csv
video_name,jitter_before,jitter_after,jitter_reduction_percent,tracking_lost_before,tracking_lost_after,fps,crop_ratio
```

## Required Markdown Reports

### `RESULTS.md`

Must contain:

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

### `LIMITATIONS.md`

Must contain:

1. Not tested on real drone
2. SITL/replay only
3. Camera calibration limitations
4. Simulation limits
5. Dataset limitations
6. Edge hardware limitations
7. Next validation steps

### `MODEL_CARD.md`

Must contain:

1. Model name
2. Dataset
3. Classes
4. Training command
5. Metrics
6. Runtime benchmark
7. Known failure cases
8. Intended use
9. Not intended use

### `DATASET_MANIFEST.md`

Must contain:

1. Dataset source
2. Version/date
3. Classes
4. Split
5. Preprocessing
6. Augmentation
7. Known bias/limitations



---

# File: FALLBACKS.md

# FALLBACKS.md — Fallback Rules

## Principle

Fallback is allowed only to preserve the roadmap. Fallback is not failure if documented honestly.

## PX4/Gazebo Camera Stream Fails

Use Hybrid SITL:

```text
PX4/Gazebo:
- proves simulator setup
- proves offboard/MAVLink concept where possible

Replay/video:
- drives perception
- drives control simulation
- drives robustness tests
```

Document:

```text
Full Gazebo camera bridge is future work.
```

## MAVLink Full Send Fails

Keep:

- C++ message builder
- Field mapping
- Command logs
- MAVLink design document
- Optional pymavlink smoke test

Do not claim full closed-loop autopilot integration.

## YOLO Training Is Weak

Keep:

- Pretrained YOLO tracking
- Small custom fine-tune
- ONNX benchmark
- Error analysis
- Dataset limitation

Do not spend days chasing mAP if the system pipeline is not done.

## OpenVINO Fails

Keep:

- PyTorch benchmark
- ONNX Runtime benchmark
- OpenVINO attempted section
- Future work note

## C++ MAVLink Is Too Slow

Prioritize:

1. C++ PID
2. C++ failsafe
3. C++ control loop timing
4. MAVLink-compatible payload logging

## ROS 2 Takes Too Long

Use:

- Python + C++ processes
- UDP IPC
- MAVLink-compatible message logs

Treat ROS 2 as optional extension.

## Laptop Performance Is Poor

Use:

- Smaller image size
- Marker mode first
- YOLO nano
- ONNX Runtime
- Lower frame rate
- CPU limit test as explicit evidence

## Documentation Is Falling Behind

Stop adding features and write:

- TECHNICAL_DESIGN.md
- TEST_PLAN.md
- RESULTS.md
- LIMITATIONS.md

A measured partial product is better than an undocumented pile of code.



---

# File: REPO_TEMPLATES.md

# REPO_TEMPLATES.md — Initial Content Templates

## README.md Template

```md
# Edge Vision Precision Landing & AI Target Tracking for UAV SITL

A laptop-based UAV edge-vision portfolio project that combines OpenCV marker detection, YOLO target tracking, ONNX/OpenVINO edge inference, C++ PID control, MAVLink-compatible message design, and robustness testing.

## Why This Project

This project demonstrates a measurable perception-control system for UAV precision landing and target tracking without requiring real drone hardware.

## Architecture

Camera / Replay / Gazebo
        |
        v
Python Perception
        |
        v
IPC target_observation
        |
        v
C++ Control Node
        |
        v
MAVLink-compatible Command Log / SITL

## Features

- ArUco/AprilTag landing target detection
- Pixel and metric target error estimation
- C++ PID controller
- C++ failsafe manager
- Python → C++ IPC
- LANDING_TARGET / SET_POSITION_TARGET_LOCAL_NED mapping
- YOLO target tracking
- ONNX/OpenVINO benchmark
- Robustness tests
- Docker/reproducible scripts

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/run_all_tests.sh
```

## Status

See `RESULTS.md` and `LIMITATIONS.md`.
```

## PROBLEM.md Template

```md
# Problem Statement

## Problem

Build a laptop-based edge vision system for UAV precision landing and target tracking using simulation/replay validation.

## Industrial Risks

- Camera noise
- Motion blur
- Target occlusion
- Communication delay
- Frame drop
- Wind/disturbance
- CPU limitation
- False target
- Target lost during descent

## Core Objective

Demonstrate a measurable perception-control pipeline under resource constraints.

## Success Criteria

- Detect landing target
- Estimate target error
- Run PID visual servoing
- Generate MAVLink-compatible messages
- Maintain failsafe under target loss
- Benchmark AI inference under CPU constraint
```

## REQUIREMENTS.md Template

```md
# Requirements

## Functional Requirements

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

## Non-Functional Requirements

- NFR-01: Control loop >= 30 Hz.
- NFR-02: Vision loop >= 15 FPS in marker mode.
- NFR-03: P95 end-to-end latency <= 150 ms.
- NFR-04: System must fail safe when target is lost.
- NFR-05: System must be reproducible with scripts/Docker.
```

## TEST_PLAN.md Template

```md
# Test Plan

## Test Levels

1. Unit tests
2. Component tests
3. Integration tests
4. Robustness tests
5. Clean clone test

## Required Robustness Cases

- Normal
- Noise low/high
- Blur low/high
- Occlusion 0.5s/1s/2s
- Delay 100ms/200ms
- Frame drop 10%/20%
- CPU limit 50%/20%
- False target optional

## Metrics

- FPS
- P50/P95 latency
- Final error
- Overshoot
- Settling time
- Target lock rate
- Recovery time
- Unsafe command count
```

## LIMITATIONS.md Template

```md
# Limitations

- The system has not been tested on a real UAV.
- Validation is limited to SITL/replay and controlled robustness tests.
- Camera vibration, rolling shutter, and real wind are approximated only.
- Full hardware-in-the-loop validation is future work.
- Model performance depends on dataset quality and coverage.
- OpenVINO/TensorRT results depend on available hardware.
```

