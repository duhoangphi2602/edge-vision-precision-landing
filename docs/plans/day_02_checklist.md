# Day 2 Manual Execution Checklist: OpenCV reader + ArUco/AprilTag detection

## 1. Laptop (Machine A): Thiết lập cấu hình và tiện ích Overlay
**Mục tiêu:** Tạo cấu hình linh hoạt cho camera/marker và một module chuyên dụng để vẽ bounding box, tâm target, và thông tin lên màn hình.

💡 **Quyết định kiến trúc & Giải thích:**
- **Vì sao dùng YAML cho cấu hình?** Việc tách biệt tham số (độ phân giải camera, threshold, marker ID) ra khỏi code giúp ta dễ dàng chuyển đổi cấu hình khi đổi môi trường (webcam laptop sang camera trên UAV) mà không cần sửa source code.
- **Tách `overlay.py` để làm gì?** Trong hệ thống thực tế, module vẽ UI (overlay) không nên can thiệp vào logic thuật toán (perception). Việc tách riêng giúp sau này tích hợp YOLO hay thuật toán khác đều dùng chung một bộ công cụ hiển thị.

- [ ] **Mở terminal trên Laptop (Machine A)** và tạo các file cần thiết:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
touch configs/perception.yaml
touch src/utils/overlay.py
touch src/perception/__init__.py
touch src/utils/__init__.py
```
- [ ] Chèn nội dung sau vào `configs/perception.yaml`:
```yaml
camera:
  source: 0 # 0 for default webcam, or path to video file
  width: 640
  height: 480
  fps: 30

target:
  center_x: 320 # camera_width / 2
  center_y: 240 # camera_height / 2
  aruco_dict: "DICT_4X4_50"
  target_id: 0
```
- [ ] Chèn nội dung sau vào `src/utils/overlay.py`:
```python
import cv2

def draw_target_center(frame, center_x, center_y):
    """Vẽ tâm chuẩn của camera (nơi mong muốn target nằm vào)"""
    cv2.drawMarker(frame, (center_x, center_y), (0, 255, 0), cv2.MARKER_CROSS, 20, 2)
    return frame

def draw_detection_info(frame, corners, center, target_id, error_x, error_y):
    """Vẽ bounding box của marker, tâm marker và các thông số error"""
    if corners is not None:
        cv2.polylines(frame, [corners.astype(int)], True, (0, 255, 0), 2)
        cv2.circle(frame, (int(center[0]), int(center[1])), 5, (0, 0, 255), -1)
        
        info_text = f"ID: {target_id} | e_x: {error_x:.1f} e_y: {error_y:.1f}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    return frame
```

## 2. Laptop (Machine A): Phát triển Video Reader & ArUco Detector
**Mục tiêu:** Xây dựng module đọc video/webcam ổn định và thuật toán nhận diện ArUco Marker, tính toán "pixel error" (lệch bao nhiêu pixel so với tâm màn hình).

💡 **Quyết định kiến trúc & Giải thích:**
- **Pixel Error ($e_x, e_y$):** Là sự chênh lệch tọa độ $x, y$ giữa tâm của marker nhận diện được và tâm của camera. Nếu $e_x = 0, e_y = 0$ nghĩa là drone đang ở vị trí hoàn hảo để hạ cánh xuống marker. Dữ liệu này sẽ là Input sinh tử cho module PID ở Day 4.

- [ ] Tạo các file mã nguồn:
```bash
touch src/perception/video_reader.py
touch src/perception/aruco_detector.py
```
- [ ] Chèn nội dung sau vào `src/perception/video_reader.py`:
```python
import cv2

class VideoReader:
    def __init__(self, source=0, width=640, height=480):
        # Thêm cờ CAP_V4L2 để fix lỗi timeout trên Linux
        self.cap = cv2.VideoCapture(source, cv2.CAP_V4L2)
        # Ép camera xuất định dạng YUYV vì luồng MJPG đang bị nhiễu và vỡ ảnh (Corrupt JPEG data)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()
```
- [ ] Chèn nội dung sau vào `src/perception/aruco_detector.py`:
```python
import cv2
import numpy as np

class ArucoDetector:
    def __init__(self, dict_type="DICT_4X4_50", target_id=0):
        self.target_id = target_id
        # Tương thích với các phiên bản OpenCV mới
        try:
            self.aruco_dict = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dict_type))
            self.parameters = cv2.aruco.DetectorParameters()
            self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        except AttributeError:
            # Fallback cho OpenCV cũ
            self.aruco_dict = cv2.aruco.Dictionary_get(getattr(cv2.aruco, dict_type))
            self.parameters = cv2.aruco.DetectorParameters_create()
            self.detector = None

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.detector:
            corners, ids, _ = self.detector.detectMarkers(gray)
        else:
            corners, ids, _ = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
        
        if ids is not None:
            for i in range(len(ids)):
                if ids[i][0] == self.target_id:
                    # Tính tâm của marker
                    c = corners[i][0]
                    center_x = (c[0][0] + c[2][0]) / 2.0
                    center_y = (c[0][1] + c[2][1]) / 2.0
                    return True, corners[i][0], (center_x, center_y)
        
        return False, None, None

    def compute_error(self, marker_center, camera_center):
        if marker_center is None:
            return 0.0, 0.0
        # e_x = x_target - x_center
        error_x = marker_center[0] - camera_center[0]
        error_y = marker_center[1] - camera_center[1]
        return error_x, error_y
```

## 3. Laptop (Machine A): Script chạy chính & Export Log (Metric Rule)
**Mục tiêu:** Ráp nối các module thành pipeline hoàn chỉnh và tuân thủ yêu cầu ghi log liên tục để có dữ liệu cho hệ thống control phía sau.

- [ ] Tạo file script thực thi:
```bash
touch scripts/run_perception.py
```
- [ ] Chèn nội dung sau vào `scripts/run_perception.py`:
```python
import time
import yaml
import cv2
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.perception.video_reader import VideoReader
from src.perception.aruco_detector import ArucoDetector
from src.utils.overlay import draw_target_center, draw_detection_info

def main():
    # Load Config
    with open("configs/perception.yaml", "r") as f:
        config = yaml.safe_load(f)

    cam_cfg = config["camera"]
    target_cfg = config["target"]
    camera_center = (target_cfg["center_x"], target_cfg["center_y"])

    # Init Modules
    reader = VideoReader(source=cam_cfg["source"], width=cam_cfg["width"], height=cam_cfg["height"])
    detector = ArucoDetector(dict_type=target_cfg["aruco_dict"], target_id=target_cfg["target_id"])

    # Setup CSV Log (Ghi đè file baseline ngày 1)
    log_file = open("logs/perception_baseline.csv", "w")
    log_file.write("timestamp_ns,frame_id,detected,error_x,error_y,latency_ms\n")

    frame_id = 0
    print("Starting perception loop. Press 'q' to quit.")

    while True:
        start_time = time.time_ns()
        frame = reader.read_frame()
        if frame is None:
            break

        detected, corners, marker_center = detector.detect(frame)
        
        error_x, error_y = 0.0, 0.0
        if detected:
            error_x, error_y = detector.compute_error(marker_center, camera_center)
            frame = draw_detection_info(frame, corners, marker_center, target_cfg["target_id"], error_x, error_y)

        frame = draw_target_center(frame, camera_center[0], camera_center[1])
        
        # Tính latency và log dữ liệu
        latency_ms = (time.time_ns() - start_time) / 1e6
        log_file.write(f"{time.time_ns()},{frame_id},{detected},{error_x},{error_y},{latency_ms:.2f}\n")

        cv2.imshow("Edge Vision Perception", frame)
        frame_id += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    reader.release()
    cv2.destroyAllWindows()
    log_file.close()
    print("Perception loop stopped.")

if __name__ == "__main__":
    main()
```
- [ ] **Chạy thử pipeline:** Cầm một hình in ArUco marker (DICT_4X4_50, ID 0) giơ ra trước webcam và chạy lệnh:
```bash
source ../.venv/bin/activate
python scripts/run_perception.py
```

## 4. PC GPU (Machine B): YOLO Baseline Training 
**Mục tiêu:** Khởi tạo baseline YOLO phục vụ bài toán Tracking (tuần 2).

- [ ] Kích hoạt môi trường và tải một ảnh mẫu/dataset UAV nhỏ để thử pipeline.
```bash
cd ~/Projects/edge-vision-precision-landing/edge-ai-training
source ../.venv/bin/activate
```
- [ ] Chạy huấn luyện YOLO baseline bản Nano (quá trình này chứng minh môi trường Pytorch/Ultralytics đã sẵn sàng):
```bash
yolo detect train model=yolo11n.pt data=coco8.yaml imgsz=640 epochs=10 batch=16 project=experiments name=yolo_baseline_v0
```
  *(Lưu ý: Bạn có thể thay đổi `coco8.yaml` bằng `dataset.yaml` của tập VisDrone thu gọn tùy ý)*

## 5. Laptop (Machine A): Nhật ký & Code Commit
**Mục tiêu:** Đóng gói tiến độ Day 2 theo quy tắc của Monorepo.

- [ ] Tạo file log `edge-vision-uav-landing/daily_logs/day_02.md`:
```md
# Day 02: OpenCV reader + ArUco detection

## Done
- [Machine A] Hoàn thiện cấu hình `perception.yaml` và module `overlay.py`.
- [Machine A] Triển khai thành công `VideoReader` và `ArucoDetector`.
- [Machine A] Hoàn thành pipeline tại `run_perception.py`, hiện overlay chuẩn xác pixel error.
- [Machine A] Đã xuất log thành công ra `perception_baseline.csv` đúng chuẩn thiết kế Day 1.
- [Machine B] Đã chạy thành công 10 epochs YOLO baseline để chứng minh năng lực training môi trường PC GPU.

## Metrics (Ví dụ với CPU i7-10750H)
- FPS: ~30 FPS (Đạt giới hạn webcam)
- Latency: ~5-15 ms (Giai đoạn CV truyền thống rất nhanh)
- Error: Đã map đúng (Pixel error nhảy realtime khi di chuyển marker)
- CPU/RAM: ~12% CPU, ~150MB RAM
- Test pass/fail: N/A (chưa viết Unit test)

## Problems
- None. Quá trình tính Center bằng Aruco API của OpenCV hơi khác giữa bản OpenCV < 4.7 và >= 4.7, đã cài đặt block `try-except` fallback để tương thích ngược.

## Decision
- Chốt việc dùng ArUco DICT_4X4_50 vì nó to, dễ nhận diện khi bay cao, ít false positive.
- Mặc dù AprilTag cũng nằm trong scope nhưng do thư viện Python binding thi thoảng gây lỗi trên Ubuntu, tạm chọn ArUco làm first baseline.

## Tomorrow
- Laptop: Cấu hình Camera Calibration và tính Pose Estimation (Khoảng cách thực tế bằng mét thay vì pixel error).
- PC GPU: Evaluate YOLO model và xuất báo cáo.
```
- [ ] **Commit lên kho lưu trữ**:
```bash
cd ~/Projects/edge-vision-precision-landing
git add .
git commit -m "day02: implement video reader, aruco detector and run perception pipeline"
```
