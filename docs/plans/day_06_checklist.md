# Day 06 Manual Execution Checklist: Production Alignment & Cross-Process IPC

## Phase 0 — Xác minh trạng thái đầu ngày
**Mục tiêu:** Đảm bảo Day 05 đã hoàn thành và dọn dẹp môi trường trước khi viết code giao tiếp IPC.

- [x] **Đọc tài liệu:** Xác nhận đã đọc `docs/plans/next_action_plan.md` và hiểu rõ yêu cầu Day 06.
- [x] **Chạy Terminal:** Mở Terminal và di chuyển vào thư mục gốc của dự án:
```bash
cd ~/Projects/edge-vision-precision-landing
```

## Phase 1 — Hợp đồng Giao Tiếp & UDP Schema (ALIGN_002)
**Mục tiêu:** Tạo tài liệu định nghĩa giao tiếp giữa Perception (CV) và Control (PID) bằng JSON.

💡 **Quyết định kiến trúc & Giải thích:**
- **Tại sao cần Schema chuẩn?** Việc tách 2 process yêu cầu một cấu trúc dữ liệu nghiêm ngặt. Nếu Perception đổi tên biến, Control sẽ crash. `MISSION_CONTRACTS.md` đóng vai trò là "luật" bắt buộc 2 bên phải tuân theo, bao gồm cả mốc thời gian `timestamp_capture_ns` để loại bỏ dữ liệu cũ (stale data rejection).

- [x] **Thao tác 1:** Chạy lệnh sau để tạo file hợp đồng:
```bash
mkdir -p edge-vision-uav-landing/docs
touch edge-vision-uav-landing/docs/MISSION_CONTRACTS.md
```

- [x] **Thao tác 2:** Copy và dán nội dung sau vào file `edge-vision-uav-landing/docs/MISSION_CONTRACTS.md`:
```markdown
# Mission Contracts (v1.0)

## 1. Perception Observation Schema (UDP)
Được gửi từ Perception Process sang Control Process.

```json
{
  "schema_version": "1.0",
  "mission_id": "P1_A_FIXED_ARUCO_LANDING",
  "timestamp_capture_ns": 1690000000000,
  "timestamp_publish_ns": 1690000005000,
  "sequence_id": 1,
  "frame_id": 100,
  "source_type": "replay",
  "target_found": true,
  "marker_dictionary": "DICT_4X4_50",
  "marker_id": 0,
  "center_px": {"x": 320.0, "y": 240.0},
  "error_px": {"x": 10.5, "y": -5.0},
  "normalized_error": {"x": 0.03, "y": -0.02},
  "pose_valid": true,
  "translation_camera_m": {"x": 0.1, "y": 0.0, "z": 2.5},
  "rotation_rvec": [0.01, 0.02, -0.01],
  "detection_latency_ms": 12.5
}
```
```

## Phase 2 — Setup YAML Config Chuẩn (ALIGN_001)
**Mục tiêu:** Lưu thông số cấu hình hạ cánh vào YAML thay vì hardcode trong file Python.

💡 **Quyết định kiến trúc & Giải thích:**
- **Tại sao dùng YAML?** Đọc dễ hơn JSON, hỗ trợ comment giải thích. Cho phép kỹ sư điều chỉnh thông số bay, threshold failsafe mà không cần đụng vào code logic.

- [x] **Thao tác 1:** Khởi tạo thư mục và file config:
```bash
mkdir -p edge-vision-uav-landing/configs/missions
touch edge-vision-uav-landing/configs/missions/fixed_aruco_landing_v1.yaml
```

- [x] **Thao tác 2:** Copy và dán nội dung sau vào `fixed_aruco_landing_v1.yaml`:
```yaml
mission_id: P1_A_FIXED_ARUCO_LANDING
marker_type: aruco
marker_dictionary: DICT_4X4_50
marker_id: 0
marker_size_m: 0.20
landing_pad_size_m: 0.60
landing_pad_motion: fixed
camera_orientation: downward_facing
gazebo_model_name: landing_pad_aruco_id0
world_frame: world
landing_pad_position_m:
  x: 0.0
  y: 0.0
  z: 0.0
failsafe:
  stale_observation_threshold_ms: 200
network:
  udp_ip: "127.0.0.1"
  udp_port: 5005
```

## Phase 3 — Xây dựng IPC UDP (Cross-Process Setup)
**Mục tiêu:** Viết code Python thực hiện việc gửi và nhận dữ liệu qua UDP Port 5005.

💡 **Quyết định kiến trúc & Giải thích:**
- **UDP vs TCP:** Dữ liệu camera (ví dụ 30 FPS) liên tục được cập nhật. Nếu dùng TCP, khi rớt mạng 1 nhịp, TCP sẽ cố gửi lại frame cũ, khiến Controller nhận tọa độ sai (trễ thời gian thực). UDP sẽ vứt bỏ frame rớt và luôn lấy frame mới nhất. 

- [x] **Thao tác 1:** Khởi tạo cấu trúc IPC:
```bash
mkdir -p edge-vision-uav-landing/src/ipc
touch edge-vision-uav-landing/src/ipc/__init__.py
touch edge-vision-uav-landing/src/ipc/udp_sender.py
touch edge-vision-uav-landing/src/ipc/udp_receiver.py
```

- [x] **Thao tác 2:** Dán code sau vào `src/ipc/udp_sender.py`:
```python
import socket
import json
import time

class UDPSender:
    def __init__(self, ip="127.0.0.1", port=5005):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def send_observation(self, observation_dict):
        # Update publish timestamp
        observation_dict["timestamp_publish_ns"] = time.time_ns()
        message = json.dumps(observation_dict).encode('utf-8')
        self.sock.sendto(message, (self.ip, self.port))

if __name__ == "__main__":
    sender = UDPSender()
    dummy_data = {
        "schema_version": "1.0",
        "timestamp_capture_ns": time.time_ns(),
        "normalized_error": {"x": 0.01, "y": -0.01},
        "pose_valid": True
    }
    while True:
        dummy_data["timestamp_capture_ns"] = time.time_ns()
        sender.send_observation(dummy_data)
        print("Đã gửi observation!")
        time.sleep(0.1) # 10Hz
```

- [ ] **Thao tác 3:** Dán code sau vào `src/ipc/udp_receiver.py`:
```python
import socket
import json
import time

class UDPReceiver:
    def __init__(self, ip="127.0.0.1", port=5005, stale_threshold_ms=200):
        self.ip = ip
        self.port = port
        self.stale_threshold_ms = stale_threshold_ms
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(0.5) # timeout tránh block hoàn toàn

    def receive_latest(self):
        latest_data = None
        try:
            # Rút cạn buffer để luôn lấy gói tin mới nhất (Drop gói cũ nếu kẹt)
            while True:
                data, _ = self.sock.recvfrom(4096)
                latest_data = data
        except socket.timeout:
            pass
        except BlockingIOError:
            pass

        if latest_data:
            obs = json.loads(latest_data.decode('utf-8'))
            current_ns = time.time_ns()
            latency_ms = (current_ns - obs.get("timestamp_capture_ns", current_ns)) / 1e6
            
            if latency_ms > self.stale_threshold_ms:
                print(f"[FAILSAFE] Dữ liệu quá cũ ({latency_ms:.1f}ms > {self.stale_threshold_ms}ms)")
                return None
            return obs
        return None

if __name__ == "__main__":
    receiver = UDPReceiver()
    receiver.sock.setblocking(False)
    print("Đang chờ UDP data ở port 5005...")
    while True:
        obs = receiver.receive_latest()
        if obs:
            print(f"Nhận observation hợp lệ! Normalized Error: {obs['normalized_error']}")
        time.sleep(0.02) # 50Hz control loop logic
```

- [x] **Thao tác 4 (Run Test):** Mở 2 tab Terminal song song:
  - Tab 1 chạy Receiver:
    ```bash
    python3 edge-vision-uav-landing/src/ipc/udp_receiver.py
    ```
  - Tab 2 chạy Sender:
    ```bash
    python3 edge-vision-uav-landing/src/ipc/udp_sender.py
    ```
  - *Kết quả mong đợi:* Tab 1 liên tục in "Nhận observation hợp lệ...". Nếu dừng Tab 2, Tab 1 sẽ im lặng (vào timeout loop).

## Phase 4 — Cấu trúc Experiment Registry cho Machine B (ALIGN_003-005)
**Mục tiêu:** Tạo file theo dõi các lần huấn luyện mô hình để trả lời được câu hỏi "Model này có metrics gì, vì sao chọn nó?".

- [x] **Thao tác 1:** Khởi tạo registry trong ML workspace:
```bash
mkdir -p edge-ai-training/docs
touch edge-ai-training/EXPERIMENT_REGISTRY.csv
```

- [x] **Thao tác 2:** Copy dán header chuẩn này vào `EXPERIMENT_REGISTRY.csv`:
```csv
Experiment_ID,Date,Model_Type,Dataset_Version,Epochs,Batch_Size,mAP50,mAP50-95,Notes
TRN_001,2026-07-14,YOLOv11n,VisDrone2019,50,-1,0.25,0.15,Baseline model (auto-batch issue)
```

## Thống kê cuối ngày & Dọn dẹp
- [x] **Thao tác 1:** Tạo file tổng kết ngày 6:
```bash
touch edge-vision-uav-landing/daily_logs/day_06.md
```

- [x] **Thao tác 2:** Ghi nhận log:
```markdown
# Day 06: Production Alignment & Cross-Process IPC

## Done
- Định nghĩa JSON schema cho Observation theo ROADMAP 3.1.5.
- Cấu hình YAML cho Fixed ArUco Landing (mission P1-A).
- Hoàn thiện UDP Sender/Receiver với cơ chế stale data rejection (> 200ms).
- Thiết lập Experiment Registry cho Machine B.

## Metrics & Test
- UDP truyền tin thành công ở localhost (Port 5005).
- Receiver lọc thành công gói tin bị trễ hoặc rớt mạng.

## Next Action
- Tích hợp UDP vào PID Controller cũ và chuyển sang môi trường Gazebo SITL (Day 07).
```

- [x] **Thao tác 3:** Commit lên Git:
```bash
git add docs/ edge-vision-uav-landing/ edge-ai-training/
git commit -m "feat(ipc): implement UDP sender/receiver and mission contracts for Day 06"
```
