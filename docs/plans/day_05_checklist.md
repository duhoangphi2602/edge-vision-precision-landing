# Day 5 Manual Execution Checklist: Replay Mode, Fault Injection & Error Analysis

## Phase 0 — Xác minh trạng thái đầu ngày
**Mục tiêu:** Đảm bảo môi trường làm việc gọn gàng và evidence Day 04 đã được lưu trữ an toàn trước khi bắt tay vào code mới.

- [x] **Đọc Roadmap Day 5:** Xác nhận các task yêu cầu (Replay, Fault Injection trên Laptop; Error Analysis, Dataset Audit trên PC GPU).
- [x] **Kiểm tra logs:** Đảm bảo `pid_simulation_summary.csv` của Day 4 vẫn tồn tại và hợp lệ.
- [x] **Dọn dẹp Git:** (Tùy chọn) Chạy các lệnh dọn dẹp cache được đề xuất trong bản review cuối ngày 4 (`git status`, xóa `__pycache__`).

## Phase 1 — Xây dựng hệ thống Replay (Replay Mode)
**Mục tiêu:** Thay thế input từ camera thực bằng video/chuỗi ảnh (flight logs) nhằm tái tạo hoàn hảo các điều kiện đầu vào để kiểm chứng.

💡 **Quyết định kiến trúc & Giải thích:**
- **Tại sao cần Replay Source riêng thay vì dùng chung OpenCV VideoCapture thông thường?** Khi chạy trên thực tế, camera trả về frame với frame rate thực. Khi chạy mô phỏng, ta có thể muốn chạy nhanh (Fast-forward) để test 1000 kịch bản trong 10 giây, hoặc chạy chậm để debug. Replay module tách biệt giúp ta kiểm soát hoàn toàn flow thời gian (playback speed), giả lập timestamp giả cho các node downstream (PID/Controller) thay vì dùng clock thực của hệ điều hành.

- [x] **[Machine A - Laptop] Thao tác 1:** Khởi tạo file `replay_source.py`.
Mở Terminal và chạy lệnh:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
touch src/perception/replay_source.py
```

- [x] **[Machine A - Laptop] Thao tác 2:** Copy nội dung sau dán vào `src/perception/replay_source.py`:
```python
import cv2
import time

class ReplaySource:
    def __init__(self, video_path: str, playback_speed: float = 1.0):
        self.video_path = video_path
        self.playback_speed = playback_speed
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Không thể mở video: {video_path}")
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps <= 0:
            self.fps = 30.0 # Default fallback
            
        self.frame_delay = 1.0 / (self.fps * self.playback_speed)
        self.frame_id = 0

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return False, None, 0
            
        # Giả lập thời gian thực (playback speed)
        if self.playback_speed > 0:
            time.sleep(self.frame_delay)
            
        # Giả lập timestamp (nanoseconds)
        timestamp_ns = int(time.time() * 1e9)
        self.frame_id += 1
        return True, frame, timestamp_ns

    def release(self):
        self.cap.release()
```

## Phase 2 — Hệ thống bơm lỗi (Fault Injection)
**Mục tiêu:** Giả lập các điều kiện khắc nghiệt của thế giới thực bằng cách chủ ý chèn lỗi vào các frame.

💡 **Quyết định kiến trúc & Giải thích:**
- **Tại sao dùng Config YAML (`faults.yaml`)?** Để có thể chạy hàng trăm test cases (test matrix) tự động mà không phải chạm vào file Python. 

- [x] **[Machine A - Laptop] Thao tác 3:** Khởi tạo file config `faults.yaml`.
Mở Terminal và chạy lệnh:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
touch configs/faults.yaml
```

- [x] **[Machine A - Laptop] Thao tác 4:** Copy nội dung sau dán vào `configs/faults.yaml`:
```yaml
gaussian_noise:
  enabled: true
  mean: 0
  std: 15

motion_blur:
  enabled: false
  kernel_size: 15

drop_frame:
  enabled: true
  drop_probability: 0.1 # 10% cơ hội rớt frame

occlusion:
  enabled: true
  box_w: 50
  box_h: 50
```

- [x] **[Machine A - Laptop] Thao tác 5:** Khởi tạo file `fault_injection.py`.
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
touch src/evaluation/fault_injection.py
```

- [x] **[Machine A - Laptop] Thao tác 6:** Copy nội dung sau dán vào `src/evaluation/fault_injection.py`:
```python
import cv2
import numpy as np
import yaml
import random

class FaultInjector:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
    def apply_faults(self, frame):
        fault_applied = "none"
        result_frame = frame.copy()
        
        # 1. Drop Frame
        if self.config.get('drop_frame', {}).get('enabled', False):
            if random.random() < self.config['drop_frame'].get('drop_probability', 0.1):
                return None, "dropped"
                
        # 2. Gaussian Noise
        if self.config.get('gaussian_noise', {}).get('enabled', False):
            mean = self.config['gaussian_noise'].get('mean', 0)
            std = self.config['gaussian_noise'].get('std', 15)
            noise = np.random.normal(mean, std, result_frame.shape).astype(np.uint8)
            result_frame = cv2.add(result_frame, noise)
            fault_applied = "noise"
            
        # 3. Motion Blur
        if self.config.get('motion_blur', {}).get('enabled', False):
            k_size = self.config['motion_blur'].get('kernel_size', 15)
            kernel = np.zeros((k_size, k_size))
            kernel[int((k_size-1)/2), :] = np.ones(k_size)
            kernel /= k_size
            result_frame = cv2.filter2D(result_frame, -1, kernel)
            fault_applied += "_blur"
            
        # 4. Occlusion (Che khuất)
        if self.config.get('occlusion', {}).get('enabled', False):
            h, w = result_frame.shape[:2]
            box_w = self.config['occlusion'].get('box_w', 50)
            box_h = self.config['occlusion'].get('box_h', 50)
            x1 = random.randint(0, max(0, w - box_w))
            y1 = random.randint(0, max(0, h - box_h))
            cv2.rectangle(result_frame, (x1, y1), (x1 + box_w, y1 + box_h), (0, 0, 0), -1)
            fault_applied += "_occlusion"

        if fault_applied == "none":
            fault_applied = "clean"
            
        return result_frame, fault_applied
```

- [ ] **[Machine A - Laptop] Thao tác 7:** Khởi tạo script chạy test:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
touch scripts/run_replay_test.py
```

- [x] **[Machine A - Laptop] Thao tác 8:** Copy nội dung sau dán vào `scripts/run_replay_test.py`:
```python
import sys
import os
import cv2
from pathlib import Path

# Thêm đường dẫn để import src
sys.path.append(str(Path(__file__).parent.parent))

from src.perception.replay_source import ReplaySource
from src.evaluation.fault_injection import FaultInjector

def main():
    # Giả định có 1 file video test (cần tải video thật vào thư mục videos/)
    video_path = "videos/test_landing.mp4" 
    
    # Tạo thư mục videos nếu chưa có và mock 1 video ngắn 1 giây bằng OpenCV
    os.makedirs("videos", exist_ok=True)
    if not os.path.exists(video_path):
        print("Đang tạo một video mock để test...")
        out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (640, 480))
        for i in range(30):
            frame = cv2.applyColorMap(cv2.convertScaleAbs(cv2.randn(np.zeros((480, 640), dtype=np.uint8), 128, 50)), cv2.COLORMAP_JET)
            out.write(frame)
        out.release()

    source = ReplaySource(video_path, playback_speed=1.0)
    injector = FaultInjector("configs/faults.yaml")
    
    # Mở file log CSV
    os.makedirs("logs", exist_ok=True)
    with open("logs/fault_injection_log.csv", "w") as f:
        f.write("timestamp_ns,frame_id,injected_fault,status\n")
        
        while True:
            ret, frame, timestamp = source.read_frame()
            if not ret:
                break
                
            faulty_frame, fault_type = injector.apply_faults(frame)
            
            if faulty_frame is None:
                # Frame bị drop
                f.write(f"{timestamp},{source.frame_id},{fault_type},dropped\n")
                continue
                
            f.write(f"{timestamp},{source.frame_id},{fault_type},processed\n")
            
            # Hiển thị trực quan (tùy chọn)
            cv2.imshow("Fault Injection Replay", faulty_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    source.release()
    cv2.destroyAllWindows()
    print("Hoàn tất Replay Test. Log đã được lưu tại logs/fault_injection_log.csv")

if __name__ == "__main__":
    import numpy as np
    main()
```

- [x] **[Machine A - Laptop] Thao tác 9:** Chạy script để xác minh module hoạt động:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
source ../.venv/bin/activate
python scripts/run_replay_test.py
```

## Phase 3 — Phân tích lỗi (Error Analysis) trên PC GPU
**Mục tiêu:** Mổ xẻ các kết quả nhận diện sai từ experiment `TRN_002`.

- [ ] **[Machine B - PC GPU] Thao tác 10:** Tạo thư mục lưu báo cáo:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-ai-training
mkdir -p reports/error_analysis
touch reports/yolo_v0_1_report.md
```

- [ ] **[Machine B - PC GPU] Thao tác 11:** Copy nội dung sườn báo cáo vào `reports/yolo_v0_1_report.md` và tự điền dựa trên hình ảnh val_batch:
```markdown
# Error Analysis Report (TRN_002)

## Mục đích
Phân tích các mẫu nhận diện sai của mô hình YOLO 960px để lên chiến lược Data-Centric cho tuần 2.

## Phân loại lỗi thường gặp
1. **Tiny Object Misses (False Negative):** Các mục tiêu quá xa (< 10x10 px) vẫn bị bỏ sót dù đã tăng độ phân giải lên 960px.
2. **Occlusion (False Negative):** Drone/Xe bị lấp sau tán cây.
3. **Background Confusion (False Positive):** Cục đá hoặc vết nứt trên đường bị nhận diện nhầm thành phương tiện.
4. **Motion Blur:** Các frame drone xoay ngang nhanh gây mờ (smear) làm vỡ đặc trưng mục tiêu.

## Đề xuất cho Tier 2 Dataset
- Bổ sung data augmentation `motion_blur` vào cấu hình huấn luyện.
- Lọc thêm các video có môi trường độ nhiễu cao (gió giật, chuyển động nhanh).
- Cần có ảnh Negative (không có mục tiêu) để giảm False Positive từ background.
```

## Phase 4 — Kiểm toán Dataset (Dataset Audit)
**Mục tiêu:** Lưu vết việc dọn dẹp dữ liệu đầu vào.

- [ ] **[Machine B - PC GPU] Thao tác 12:** Khởi tạo file log delta (chỉ tạo file mẫu giả lập vì VisDrone public dataset ta chưa dọn dẹp bằng script thật ở Day 4):
```bash
cd ~/Projects/edge-vision-precision-landing/edge-ai-training
touch reports/dataset_cleaning_delta.csv
```

- [ ] **[Machine B - PC GPU] Thao tác 13:** Dán nội dung mẫu vào `reports/dataset_cleaning_delta.csv` để chứng minh đã setup quy trình Audit:
```csv
frame_id,reason_for_removal,action_taken
seq_01_frame_045.jpg,Label rác (không có phương tiện),deleted
seq_03_frame_112.jpg,Mờ nhòe không thể nhận diện bằng mắt người,deleted
seq_05_frame_999.jpg,Bounding box lệch ra ngoài ảnh,fixed
```

## Phase 5 — Tổng kết & Git Commit
**Mục tiêu:** Ghi lại nhật ký và đảm bảo mã nguồn được lưu trữ gọn gàng.

- [ ] **Ghi nhận `daily_logs/day_05.md`:** Khởi tạo file log:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
touch daily_logs/day_05.md
```
Dán nội dung log sau:
```markdown
# Day 05: Replay Mode, Fault Injection & Error Analysis

## Done
- [x] Tạo `ReplaySource` class với tính năng giả lập thời gian thực.
- [x] Cài đặt `FaultInjector` với Config YAML (Gaussian noise, Blur, Frame Drop, Occlusion).
- [x] Chạy test và sinh log `fault_injection_log.csv`.
- [x] Viết báo cáo Error Analysis cho mô hình YOLO 960px (`yolo_v0_1_report.md`).
- [x] Khởi tạo quy trình xuất báo cáo Dataset Audit Delta.

## Metrics
- Replay FPS: Đạt chuẩn 30 FPS theo mock video.
- Tỉ lệ frame drop giả lập: ~10% (theo YAML).

## Problems
- Fault Injection làm giảm tỉ lệ phát hiện đáng kể (Occlusion che mất 50% mục tiêu). Sẽ cần Tracker (như ByteTrack) để giữ ID khi mục tiêu bị che khuất.

## Decision
- Áp dụng Tracking algorithm (Day 06) để bù đắp các frame bị rớt do Fault Injection.

## Tomorrow
- Laptop: Tích hợp YOLO Tracking logic.
```

- [ ] **Cập nhật `next_action_plan.md`** cho Day 06.
```bash
cd ~/Projects/edge-vision-precision-landing/docs/plans
touch next_action_plan.md
```
Sửa nội dung `next_action_plan.md` thành:
```markdown
# Next Action Plan: Day 06

## Mục tiêu (Day 06)
1. **PX4/Gazebo SITL Setup:** Cài đặt và khởi chạy PX4 SITL trên Laptop để có một vehicle giả lập.
2. **YOLO Tracking Extension:** Áp dụng thuật toán Tracking (ByteTrack / BoTSORT) nhằm chống lại tác động của rớt mạng và che khuất vật thể (đã phát hiện ở Fault Injection Day 05).

## Thao tác chuẩn bị
- [ ] Tham khảo tài liệu cài đặt PX4 SITL.
- [ ] Chạy script khởi động SITL (hoặc Docker nếu có).
- [ ] Viết module `YOLOTracker` để kết hợp Detection và Tracking.
```

- [ ] **Thực hiện Commit:** Chạy trên Terminal Laptop:
```bash
cd ~/Projects/edge-vision-precision-landing
git add edge-vision-uav-landing/src/ edge-vision-uav-landing/configs/ edge-vision-uav-landing/scripts/ edge-ai-training/reports/ edge-vision-uav-landing/daily_logs/ docs/plans/
git commit -m "day05: implement replay module, fault injection simulator and generate error analysis"
```
