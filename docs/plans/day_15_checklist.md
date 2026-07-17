# Day 15 Manual Execution Checklist: Architecture refactor, CMake skeleton, and model handoff

## Cảnh báo lộ trình (Roadmap Alignment)
*Day 15 bắt đầu Phase C++ cho Gate 3 và thực hiện handoff model (đóng băng từ Day 14). Mục tiêu của Machine A là tạo bộ khung C++ (skeletons) và hệ thống build (CMake) mà không phá vỡ logic Python cũ. Mục tiêu của Machine B là di chuyển model đã freeze vào package của Project 1 và cập nhật registry.*

---

## Phase 0 — Preflight và status verification

### Task 0.1: Kiểm tra trạng thái hệ thống
- [x] **Các file đã đọc:** `ROADMAP.md`, `docs/plans/day_14_checklist.md`, `edge-vision-uav-landing/daily_logs/day_14.md`.
- [x] **Trạng thái Day trước (Day 14):** Hoàn thành (PASS_WITH_DOCUMENTED_LIMITATION).
- [x] **Gate hiện tại:** Bước vào Phase C++ (chuẩn bị cho Gate 3).
- [x] **Git status:** Sạch sẽ, không có uncommitted changes.
- [x] **Dependency:** Freeze model `yolo26s_640_v1` từ Day 14.
- [x] **Blocker:** Không có.

---

## Machine A — Các phase thực thi

### Phase 1: Tạo CMake Project Structure

#### Task 1.1: Tạo root CMakeLists.txt
- **Mục tiêu:** Định nghĩa project C++17 và kết nối các module `control_cpp` và `interface_cpp`.
- **Mission phục vụ:** P1-A, INFRA
- **File liên quan:** `edge-vision-uav-landing/CMakeLists.txt`
- **Các bước thao tác:**
  - [x] Chạy lệnh tạo root `CMakeLists.txt`:
```bash
cat << 'EOF' > edge-vision-uav-landing/CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(EdgeVisionUAVLanding VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Sẽ liên kết OpenCV, ONNXRuntime và MAVSDK ở các module sau
add_subdirectory(src/interface_cpp)
add_subdirectory(src/control_cpp)
EOF
```
  - [x] **Lệnh kiểm tra:** `cat edge-vision-uav-landing/CMakeLists.txt`
  - [x] **Acceptance criteria:** File tồn tại với cấu hình C++17.

#### Task 1.2: Tạo module CMakeLists.txt
- **Mục tiêu:** Định nghĩa các thư viện tĩnh/chia sẻ cho `interface_cpp` và `control_cpp`.
- **Các bước thao tác:**
  - [x] Chạy lệnh tạo file:
```bash
cat << 'EOF' > edge-vision-uav-landing/src/interface_cpp/CMakeLists.txt
add_library(interface_cpp STATIC
    src/mavlink_builder.cpp
    src/udp_receiver.cpp
)
target_include_directories(interface_cpp PUBLIC include)
EOF

cat << 'EOF' > edge-vision-uav-landing/src/control_cpp/CMakeLists.txt
add_library(control_cpp STATIC
    src/pid_controller.cpp
    src/failsafe.cpp
    src/control_loop.cpp
)
target_include_directories(control_cpp PUBLIC include)
EOF
```
  - [x] **Acceptance criteria:** Các file CMakeLists.txt cục bộ được tạo.

### Phase 2: Thêm Skeletons cho C++ PID, Failsafe, IPC

#### Task 2.1: Skeleton cho PID Controller & Failsafe
- **Mục tiêu:** Định nghĩa cấu trúc header (.hpp) và implementation (.cpp) tĩnh (skeleton) không phá vỡ logic cũ.
- **Mission phục vụ:** P1-A
- **File liên quan:** `pid_controller.hpp`, `pid_controller.cpp`, v.v.
- **Các bước thao tác:**
  - [x] Chạy lệnh sinh header và source:
```bash
cat << 'EOF' > edge-vision-uav-landing/src/control_cpp/include/pid_controller.hpp
#pragma once

namespace control {
class PIDController {
public:
    PIDController(double kp, double ki, double kd);
    double compute(double setpoint, double current_value, double dt);
private:
    double kp_, ki_, kd_;
    double integral_, prev_error_;
};
} // namespace control
EOF

cat << 'EOF' > edge-vision-uav-landing/src/control_cpp/src/pid_controller.cpp
#include "pid_controller.hpp"

namespace control {
PIDController::PIDController(double kp, double ki, double kd) 
    : kp_(kp), ki_(ki), kd_(kd), integral_(0), prev_error_(0) {}

double PIDController::compute(double setpoint, double current_value, double dt) {
    // TODO: Implement PID logic (matching Python behavior)
    return 0.0;
}
} // namespace control
EOF

cat << 'EOF' > edge-vision-uav-landing/src/control_cpp/include/failsafe.hpp
#pragma once

namespace control {
class Failsafe {
public:
    static bool check_timeout(double last_msg_time, double current_time, double timeout_limit);
};
} // namespace control
EOF

cat << 'EOF' > edge-vision-uav-landing/src/control_cpp/src/failsafe.cpp
#include "failsafe.hpp"

namespace control {
bool Failsafe::check_timeout(double last_msg_time, double current_time, double timeout_limit) {
    return (current_time - last_msg_time) > timeout_limit;
}
} // namespace control
EOF

cat << 'EOF' > edge-vision-uav-landing/src/control_cpp/include/control_loop.hpp
#pragma once

namespace control {
class ControlLoop {
public:
    void run();
};
} // namespace control
EOF

cat << 'EOF' > edge-vision-uav-landing/src/control_cpp/src/control_loop.cpp
#include "control_loop.hpp"

namespace control {
void ControlLoop::run() {
    // TODO: Implement main loop
}
} // namespace control
EOF
```
  - [x] **Acceptance criteria:** Header và cpp files cho Control Module tồn tại và sẵn sàng biên dịch (compilable).

#### Task 2.2: Skeleton cho Interface (Receiver, MAVLink)
- **Các bước thao tác:**
  - [x] Chạy lệnh sinh skeleton:
```bash
cat << 'EOF' > edge-vision-uav-landing/src/interface_cpp/include/udp_receiver.hpp
#pragma once

namespace interface {
class UDPReceiver {
public:
    UDPReceiver(int port);
    bool receive();
private:
    int port_;
};
} // namespace interface
EOF

cat << 'EOF' > edge-vision-uav-landing/src/interface_cpp/src/udp_receiver.cpp
#include "udp_receiver.hpp"

namespace interface {
UDPReceiver::UDPReceiver(int port) : port_(port) {}
bool UDPReceiver::receive() {
    // TODO: Bind and recvfrom
    return false;
}
} // namespace interface
EOF

cat << 'EOF' > edge-vision-uav-landing/src/interface_cpp/include/mavlink_builder.hpp
#pragma once

namespace interface {
class MAVLinkBuilder {
public:
    static void build_velocity_command();
};
} // namespace interface
EOF

cat << 'EOF' > edge-vision-uav-landing/src/interface_cpp/src/mavlink_builder.cpp
#include "mavlink_builder.hpp"

namespace interface {
void MAVLinkBuilder::build_velocity_command() {
    // TODO: Pack MAVLink msg
}
} // namespace interface
EOF
```
  - [x] **Acceptance criteria:** Header và cpp files cho Interface Module tồn tại.

#### Task 2.3: Compile Dummy Build (Kiểm tra Skeleton)
- **Mục tiêu:** Đảm bảo toàn bộ project CMake không có lỗi cú pháp và skeleton biên dịch tốt.
- **Các bước thao tác:**
  - [x] Chạy lệnh build:
```bash
cd edge-vision-uav-landing
mkdir -p build && cd build
cmake ..
make
cd ../..
```
  - [x] **Lệnh kiểm tra:** Check log `make` không sinh lỗi (sẽ tạo các file lib .a).
  - [x] **Acceptance criteria:** Lệnh make hoàn tất mà không có Error. Build log thành công.

---

## Machine B — Các phase thực thi

### Phase 3: Model Handoff

#### Task 3.1: Integrity Check & Install Model Package
- **Mục tiêu:** Đọc checksum từ metadata và copy model vào thư mục deploy cuối cùng của Edge module.
- **Mission phục vụ:** ML, P1-B
- **File liên quan:** `edge-vision-uav-landing/models/`
- **Các bước thao tác:**
  - [x] Chạy lệnh copy model và kiểm tra checksum:
```bash
# Đảm bảo target directory tồn tại
mkdir -p edge-vision-uav-landing/models/yolo26s_640_v1

# Copy package được chọn từ Phase trước (bên thư mục training)
cp -r edge-ai-training/models/deployment_candidates/yolo26s_640_v1/* edge-vision-uav-landing/models/yolo26s_640_v1/

# Kiểm tra Integrity
cd edge-vision-uav-landing/models/yolo26s_640_v1/
CHECKSUM_EXPECTED=$(grep checksum_sha256 metadata.yaml | awk '{print $2}')
CHECKSUM_ACTUAL=$(sha256sum model.onnx | awk '{print $1}')

if [ "$CHECKSUM_EXPECTED" = "$CHECKSUM_ACTUAL" ]; then
    echo "Integrity check PASSED. Checksum match: $CHECKSUM_ACTUAL"
else
    echo "Integrity check FAILED. Checksums DO NOT match."
    exit 1
fi
cd ../../../
```
  - [x] **Expected output:** Script in ra "Integrity check PASSED".
  - [x] **Acceptance criteria:** Model nằm trong `edge-vision-uav-landing/models/yolo26s_640_v1/` và checksum hợp lệ.

#### Task 3.2: Cập nhật Config Model & Model-load Smoke Test
- **Mục tiêu:** Chỉnh sửa file yaml `p1_b_tracking_v1.yaml` để chỉ định chính xác phiên bản model và chạy script mock load qua Python.
- **Các bước thao tác:**
  - [x] Chạy lệnh cập nhật config:
```bash
# Thêm cấu hình model path vào p1_b_tracking_v1.yaml
echo "model_path: models/yolo26s_640_v1/model.onnx" >> edge-vision-uav-landing/configs/missions/p1_b_tracking_v1.yaml
```
  - [x] Sinh script Smoke Test để mô phỏng tải mô hình bằng ONNX Runtime:
```bash
cat << 'EOF' > edge-vision-uav-landing/scripts/smoke_test_model_load.py
import onnxruntime as ort
import sys
import yaml

config_path = "configs/missions/p1_b_tracking_v1.yaml"
try:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    model_path = config.get("model_path")
    if not model_path:
        raise ValueError("model_path missing in config")
    
    print(f"Loading ONNX model from: {model_path}")
    session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    print("Model load SUCCESS.")
    sys.exit(0)
except Exception as e:
    print(f"Model load FAILED: {e}")
    sys.exit(1)
EOF
```
  - [x] Chạy smoke test (phải có `onnxruntime` cài sẵn):
```bash
cd edge-vision-uav-landing
python3 scripts/smoke_test_model_load.py
cd ..
```
  - [x] **Acceptance criteria:** In ra `Model load SUCCESS.`.

---

## Integration / Evidence Phase

- **Test:** Smoke test cho model load pass. C++ code skeletons pass dummy compile.
- **Benchmark:** Không yêu cầu benchmark mới trong ngày hôm nay.
- **Report:** C++ compilation logs (std out/err).
- **Run Artifact:** Lib tĩnh C++ `libcontrol_cpp.a` và `libinterface_cpp.a` trong folder `build`.
- **Manifest:** Config `p1_b_tracking_v1.yaml` trỏ tới `yolo26s_640_v1` ONNX model.

---

## End-of-Day Gate Review

### Deliverables
- `edge-vision-uav-landing/CMakeLists.txt` và các thư mục/skeleton C++.
- Thư mục copy `edge-vision-uav-landing/models/yolo26s_640_v1/`.
- Updated `configs/missions/p1_b_tracking_v1.yaml`.
- Log biên dịch C++.

### Verification Matrix
| Hạng mục | Evidence yêu cầu | Trạng thái đầu ngày | Điều kiện hoàn thành |
|---|---|---|---|
| CMake build | Build output libs | MISSING | CMake configure & make chạy thành công không có error |
| Model Integrity | Checksum pass script output | MISSING | `CHECKSUM_ACTUAL == CHECKSUM_EXPECTED` |
| Handoff Config | `p1_b_tracking_v1.yaml` updated | MISSING | Có đường dẫn model và Python smoke test pass |

### Gate Decision Template
- **Gate:** Daily Progression
- **Status:** PASS
- **Passed criteria:** C++ skeleton compiles; Python testing logic preserved; Model version explicit and integrity-checked.
- **Missing criteria:** None
- **Blocked criteria:** None
- **Deferred criteria:** C++ PID implementation thực tế (Day 16).
- **Evidence paths:** `edge-vision-uav-landing/build/`, `edge-vision-uav-landing/models/yolo26s_640_v1/`
- **Decision:** Chuyển model thành công. Bộ khung kiến trúc C++ sẵn sàng. Tiến tới Day 16: C++ PID controller and parity tests.

### End-of-Day Log Template
Theo mẫu trong ROADMAP.md, bạn hãy lưu file log `edge-vision-uav-landing/daily_logs/day_15.md` sau khi hoàn thành:
```bash
mkdir -p edge-vision-uav-landing/daily_logs/
cat << 'EOF' > edge-vision-uav-landing/daily_logs/day_15.md
# Day 15: Architecture refactor, CMake skeleton, and model handoff

## Mission served
P1-A, P1-B, INFRA, ML

## Done
- **Machine A:** Tạo dự án CMake cho modules C++ (`interface_cpp`, `control_cpp`). Viết skeletons cho PID, Failsafe, ControlLoop và Receiver (MAVLink builder). Dummy build CMake thành công.
- **Machine B:** Handoff ONNX model từ ML sang Edge (`models/yolo26s_640_v1`). Đo checksum SHA256 để xác nhận toàn vẹn, cập nhật config và test load Python thành công.

## Evidence
- `edge-vision-uav-landing/build/`
- `edge-vision-uav-landing/models/yolo26s_640_v1/model.onnx`
- `edge-vision-uav-landing/scripts/smoke_test_model_load.py`

## Metrics
- C++ Compile: SUCCESS (0 errors).
- Integrity Check: MATCHED.

## Problems
- Không có lỗi blocker trong ngày.

## Decision
- PASS. Sẵn sàng viết logic toán học C++ (Day 16).

## Tomorrow
- Day 16: C++ PID controller and parity tests.
EOF
```

### Git Commit Guidance
- [ ] Chạy lệnh commit các file code của Day 15 (Không commit output build hay file model ONNX lớn):
```bash
# Ignore build artifacts & model weights
echo "edge-vision-uav-landing/build/" >> .gitignore
echo "edge-vision-uav-landing/models/*/*.onnx" >> .gitignore

git add .gitignore
git add edge-vision-uav-landing/CMakeLists.txt
git add edge-vision-uav-landing/src/interface_cpp/
git add edge-vision-uav-landing/src/control_cpp/
git add edge-vision-uav-landing/configs/missions/p1_b_tracking_v1.yaml
git add edge-vision-uav-landing/scripts/smoke_test_model_load.py
git add edge-vision-uav-landing/daily_logs/day_15.md
git add docs/plans/day_15_checklist.md

git commit -m "feat: setup C++ CMake skeletons and handoff ONNX model for Day 15"
```
