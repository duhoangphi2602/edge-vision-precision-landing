# Day 19 Execution Checklist: Python to C++ IPC Integration

## Phase 0 — Preflight and status verification
- [x] **Verify Day 18 is COMPLETE:** 
  - Đã đọc `docs/reviews/day_18_completion_review.md` (Gate Status: `PASS`).
  - Source code Machine A hiện có MAVLink structs và builder tại `edge-vision-uav-landing/src/control_cpp`.
  - Machine B đã tạo `ARTIFACT_CHECKSUMS.txt`.
- [x] **Xác nhận không có blocker:** Sẵn sàng kết nối Python perception (sender) và C++ control (receiver).

---

## Machine A — Các phase thực thi

### Phase 1: Implement C++ UDP Receiver & JSON Parsing
**Mục tiêu:** Nhận packet từ Python (UDP) và extract các field cơ bản theo Observation Schema.
**File:** `include/udp_receiver.hpp`, `src/udp_receiver.cpp`
- [x] Tạo file header `include/udp_receiver.hpp`:
```bash
cat << 'EOF' > edge-vision-uav-landing/src/control_cpp/include/udp_receiver.hpp
#ifndef UDP_RECEIVER_HPP
#define UDP_RECEIVER_HPP

#include <string>
#include <netinet/in.h>

struct PerceptionObservation {
    bool valid = false;
    std::string mission_id;
    long long timestamp_publish_ns = 0;
    bool target_found = false;
    double error_x = 0.0;
    double error_y = 0.0;
    double latency_ms = 0.0;
};

class UdpReceiver {
public:
    UdpReceiver(int port);
    ~UdpReceiver();
    bool get_latest_observation(PerceptionObservation& obs);
private:
    int sockfd_;
    struct sockaddr_in servaddr_;
    PerceptionObservation parse_json(const std::string& json_str);
};

#endif
EOF
```

- [x] Tạo file source `src/udp_receiver.cpp` (với logic parse chuỗi cơ bản, do chưa add thư viện JSON rời):
```bash
cat << 'EOF' > edge-vision-uav-landing/src/control_cpp/src/udp_receiver.cpp
#include "udp_receiver.hpp"
#include <iostream>
#include <sys/socket.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>

UdpReceiver::UdpReceiver(int port) {
    sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
    memset(&servaddr_, 0, sizeof(servaddr_));
    servaddr_.sin_family = AF_INET;
    servaddr_.sin_addr.s_addr = INADDR_ANY;
    servaddr_.sin_port = htons(port);
    
    bind(sockfd_, (const struct sockaddr *)&servaddr_, sizeof(servaddr_));
    
    // Set non-blocking
    int flags = fcntl(sockfd_, F_GETFL, 0);
    fcntl(sockfd_, F_SETFL, flags | O_NONBLOCK);
}

UdpReceiver::~UdpReceiver() {
    close(sockfd_);
}

PerceptionObservation UdpReceiver::parse_json(const std::string& json_str) {
    PerceptionObservation obs;
    // Basic string search for demonstration to avoid external deps.
    // In production, use nlohmann/json or rapidjson.
    if (json_str.find("\"target_found\": true") != std::string::npos) {
        obs.target_found = true;
    }
    
    auto ts_pos = json_str.find("\"timestamp_publish_ns\": ");
    if (ts_pos != std::string::npos) {
        obs.timestamp_publish_ns = std::stoll(json_str.substr(ts_pos + 24, 15)); // rough parse
    }

    auto norm_pos = json_str.find("\"normalized_error\":");
    if (norm_pos != std::string::npos) {
        auto x_pos = json_str.find("\"x\":", norm_pos);
        if (x_pos != std::string::npos) obs.error_x = std::stod(json_str.substr(x_pos + 4, 8));
        auto y_pos = json_str.find("\"y\":", norm_pos);
        if (y_pos != std::string::npos) obs.error_y = std::stod(json_str.substr(y_pos + 4, 8));
    }
    obs.valid = true;
    return obs;
}

bool UdpReceiver::get_latest_observation(PerceptionObservation& obs) {
    char buffer[1024];
    struct sockaddr_in cliaddr;
    socklen_t len = sizeof(cliaddr);
    
    int n = recvfrom(sockfd_, (char *)buffer, 1024, MSG_DONTWAIT, (struct sockaddr *) &cliaddr, &len);
    if (n > 0) {
        buffer[n] = '\0';
        std::string json_str(buffer);
        obs = parse_json(json_str);
        return true;
    }
    return false;
}
EOF
```

### Phase 2: Main C++ Control Node & Graceful Shutdown
**Mục tiêu:** Tạo main executable kết nối UDP Receiver và `ControlLoop`, có bắt tín hiệu (SIGINT) để dừng an toàn.
- [x] Tạo file `src/main_control_node.cpp`:
```bash
cat << 'EOF' > edge-vision-uav-landing/src/control_cpp/src/main_control_node.cpp
#include "udp_receiver.hpp"
#include "control_loop.hpp"
#include "mavlink_builder.hpp"
#include <iostream>
#include <chrono>
#include <thread>
#include <csignal>

bool running = true;

void signal_handler(int signum) {
    std::cout << "\n[CTRL-C] Interrupt signal (" << signum << ") received. Graceful shutdown...\n";
    running = false;
}

int main() {
    signal(SIGINT, signal_handler);
    
    UdpReceiver receiver(5005);
    control::ControlLoop loop(30.0);
    control::MavlinkBuilder mav_builder;
    
    std::cout << "[INFO] Control node started. Listening on UDP 5005...\n";
    
    while(running) {
        PerceptionObservation obs;
        bool has_data = receiver.get_latest_observation(obs);
        
        long long current_time_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
            
        loop.update(obs.target_found, obs.error_x, obs.error_y, current_time_ns);
        
        float vx, vy, vz, yaw_rate;
        loop.get_velocity_commands(vx, vy, vz, yaw_rate);
        
        if (has_data) {
            std::cout << "[IPC-LOG] Data Rcvd -> ErrorX: " << obs.error_x << " ErrorY: " << obs.error_y 
                      << " | Cmd -> Vx: " << vx << " Vy: " << vy << " Vz: " << vz << "\n";
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(33)); // ~30Hz
    }
    std::cout << "[INFO] Control node stopped cleanly.\n";
    return 0;
}
EOF
```

- [x] Cập nhật `CMakeLists.txt`:
```bash
cat << 'EOF' >> edge-vision-uav-landing/src/control_cpp/CMakeLists.txt

add_executable(control_node src/main_control_node.cpp src/udp_receiver.cpp src/control_loop.cpp src/pid_controller.cpp src/state_machine.cpp src/failsafe.cpp src/mavlink_builder.cpp)
target_include_directories(control_node PUBLIC include)
EOF
```

- [x] Build dự án:
```bash
cd edge-vision-uav-landing/src/control_cpp
mkdir -p build && cd build
cmake ..
make
```

### Phase 3: Python IPC Mock Sender
**Mục tiêu:** Mô phỏng perception gửi data qua UDP.
- [x] Tạo `scripts/mock_perception_sender.py`:
```bash
mkdir -p edge-vision-uav-landing/scripts
cat << 'EOF' > edge-vision-uav-landing/scripts/mock_perception_sender.py
import socket
import time
import json

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Sending Mock Perception JSON to {UDP_IP}:{UDP_PORT}")

try:
    for i in range(100):
        # Simulate moving towards center
        err_x = 0.5 - (i * 0.005)
        
        payload = {
            "schema_version": "1.0",
            "mission_id": "P1_A_FIXED_ARUCO_LANDING",
            "timestamp_publish_ns": int(time.time() * 1e9),
            "target_found": True,
            "normalized_error": {"x": err_x, "y": 0.1},
            "detection_latency_ms": 12.5
        }
        
        sock.sendto(json.dumps(payload).encode('utf-8'), (UDP_IP, UDP_PORT))
        time.sleep(0.1) # 10Hz
        
except KeyboardInterrupt:
    print("Stopped sender.")
EOF
```

---

## Machine B — Các phase thực thi

### Phase 4: Integration Versioning
- [x] Đảm bảo input json schemas được snapshot rõ ràng. Checksum file script để làm evidence.
```bash
cd edge-vision-uav-landing/scripts
md5sum mock_perception_sender.py > IPC_INTEGRATION_CHECKSUM.txt
```

---

## Integration / Evidence Phase

- [x] Chạy test tích hợp (Terminal 1 - C++ Node):
```bash
cd edge-vision-uav-landing/src/control_cpp/build
./control_node > ../../../logs/day19_ipc_cpp_log.txt 2>&1 &
PID_CPP=$!
```

- [x] Chạy Python Sender (Terminal 2):
```bash
cd edge-vision-uav-landing/scripts
python3 mock_perception_sender.py > ../logs/day19_ipc_python_log.txt 2>&1
```

- [x] Kill C++ node an toàn:
```bash
kill -SIGINT $PID_CPP
```

- [x] Kiểm tra nội dung log, chứng minh C++ node đã nhận JSON, parse lỗi và xuất ra command `[IPC-LOG]`:
```bash
cat edge-vision-uav-landing/logs/day19_ipc_cpp_log.txt
```

---

## Deliverables
1. `include/udp_receiver.hpp` & `src/udp_receiver.cpp`
2. `src/main_control_node.cpp`
3. `scripts/mock_perception_sender.py`
4. Logs: `day19_ipc_cpp_log.txt`, `day19_ipc_python_log.txt`, `IPC_INTEGRATION_CHECKSUM.txt`

## Verification Matrix

| Hạng mục | Evidence yêu cầu | Trạng thái đầu ngày | Điều kiện hoàn thành |
|---|---|---|---|
| C++ UDP Receiver | `udp_receiver.cpp` | Missing | Nhận và parse đúng JSON |
| Graceful shutdown | Log ghi `Control node stopped cleanly.` | Missing | `SIGINT` hoạt động |
| Python Sender | `mock_perception_sender.py` | Missing | Gửi JSON liên tục |
| End-to-end Test | `day19_ipc_cpp_log.txt` | Missing | Có data flow từ UDP -> PID -> Vx/Vy |

---

## End-of-Day Log Template
Tạo file `edge-vision-uav-landing/daily_logs/day_19.md`

```markdown
# Day 19 Log

**Mission served:** `P1-A, INFRA`

**Done:**
- Machine A: Implemented C++ UDP Receiver with basic JSON extraction.
- Machine A: Integrated Receiver into main Control loop. Added graceful SIGINT shutdown.
- Machine A: Created Python mock sender to simulate perception.
- Machine B: Checksummed integration scripts.

**Evidence:**
- `logs/day19_ipc_cpp_log.txt` showing successful packet reception and control calculation.
- `logs/day19_ipc_python_log.txt`
- `scripts/IPC_INTEGRATION_CHECKSUM.txt`

**Metrics:**
- IPC frequency: Receiver loops at 30Hz, Sender at 10Hz. Stale state triggers appropriately between packets if loop is fast.
- Latency (Target): < 1ms localhost UDP overhead.

**Problems:**
- `parse_json` is currently a naive string implementation to reduce C++ dependencies. Sufficient for Phase 1 demo but should upgrade to rapidjson/nlohmann if schema gets complex.

**Decision:**
- Proceed with naive parser. Passed IPC integration test.

**Tomorrow:**
- Day 20 — CPU-limited hybrid stress test and A/B architecture benchmark.
```

## Gate Decision Template
**Gate:** Python-to-C++ IPC Integration
**Status:** 
**Passed criteria:** Data flows from Python process to C++ process via UDP. JSON is parsed and fed into the control loop. C++ node shuts down gracefully.
**Missing criteria:** None.
**Blocked criteria:** None.
**Deferred criteria:** Full proper JSON library integration (deferred to when external deps are added).
**Evidence paths:** `logs/day19_ipc_cpp_log.txt`
**Decision:** 

## Git Commit Guidance
- Stage: `edge-vision-uav-landing/src/control_cpp/`, `edge-vision-uav-landing/scripts/`, `edge-vision-uav-landing/logs/`
- Thông điệp: `feat(P1-A): day 19 python to c++ udp ipc integration and mock sender`
- Chỉ commit code và txt log, không commit build binaries.
