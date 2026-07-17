# Day 3 Manual Execution Checklist: Camera Calibration + Pose Estimation

## 1. Laptop (Machine A): Thiết lập Camera Calibration (Hiệu chuẩn Camera)
**Mục tiêu:** Tạo file cấu hình và script để tính toán (hoặc giả lập) các thông số nội tại của camera (intrinsic parameters) - bao gồm `camera_matrix` và `dist_coeffs`. Đây là bước bắt buộc để chuyển đổi từ pixel (2D) sang hệ mét (3D).

💡 **Quyết định kiến trúc & Giải thích:**
- **Tại sao cần Calibration?** Camera bị biến dạng hình học (distortion) do thấu kính lồi. Hơn nữa, để biết một khoảng cách trên màn hình (pixel) tương đương với bao nhiêu mét ngoài đời thực, ta cần biết tiêu cự (focal length) của camera. `camera_matrix` sẽ cung cấp điều đó.
- **Dùng ảnh thật hay Synthetic (giả lập)?** Vì ta đang phát triển SITL (mô phỏng) và có thể không có điều kiện in checkerboard để calibrate webcam vật lý liền lúc này, ta sẽ viết một đoạn code hỗ trợ cả 2 chế độ: load thông số có sẵn (synthetic/webcam default) hoặc chạy thuật toán calibrate thực tế bằng ảnh checkerboard. Ở bài lab này, ta sẽ dùng bộ tham số nội suy giả định (synthetic) của một webcam HD tiêu chuẩn.

- [x] **Mở terminal trên Laptop (Machine A)** và tạo các file cần thiết:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
mkdir -p src/estimation                 # (Tạo thư mục estimation chứa các module liên quan đến tính toán, ước lượng toán học như góc, vị trí, khoảng cách)
touch src/estimation/__init__.py        # (Biến thư mục estimation thành một Python package để có thể import các file bên trong)
touch src/estimation/camera_calibration.py # (Tạo file code Python chịu trách nhiệm đọc/tính toán thông số nội tại của camera)
touch configs/camera.yaml               # (Tạo file cấu hình lưu các con số matrix và distortion để không phải hard-code vào mã nguồn)
touch reports/calibration_report.md     # (Tạo file báo cáo Markdown để lưu lại bằng chứng/chỉ số sau khi calibration thành công)
```

- [x] Chèn nội dung sau vào `configs/camera.yaml` (Thông số giả lập cho webcam HD 640x480 thông dụng):
```yaml
camera_name: "webcam_default"
image_width: 640
image_height: 480
# Camera matrix: [fx, 0, cx; 0, fy, cy; 0, 0, 1]
# Giả sử góc nhìn (FOV) ~60 độ cho webcam tiêu chuẩn
camera_matrix:
  - [554.25, 0.0, 320.0]
  - [0.0, 554.25, 240.0]
  - [0.0, 0.0, 1.0]
# Distortion coefficients (k1, k2, p1, p2, k3)
dist_coeffs: [0.0, 0.0, 0.0, 0.0, 0.0]
```

- [x] Chèn nội dung sau vào `src/estimation/camera_calibration.py`:
```python
import yaml
import numpy as np
import os

class CameraCalibration:
    def __init__(self, config_path="configs/camera.yaml"):
        self.config_path = config_path
        self.camera_matrix = None
        self.dist_coeffs = None
        self.width = 640
        self.height = 480
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Cannot find camera config at {self.config_path}")
        
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)
            self.camera_matrix = np.array(data.get("camera_matrix", []), dtype=np.float32)
            self.dist_coeffs = np.array(data.get("dist_coeffs", []), dtype=np.float32)
            self.width = data.get("image_width", 640)
            self.height = data.get("image_height", 480)
            
    def get_parameters(self):
        return self.camera_matrix, self.dist_coeffs
```

## 2. Laptop (Machine A): Xây dựng thuật toán Pose Estimation (Ước lượng tư thế 3D)
**Mục tiêu:** Sử dụng `cv2.solvePnP` để tính toán khoảng cách vật lý $X, Y, Z$ (theo đơn vị mét) của ArUco marker đối với hệ tọa độ của camera.

💡 **Quyết định kiến trúc & Giải thích:**
- `solvePnP` giải bài toán Perspective-n-Point. Nó cần 3 thứ: (1) Tọa độ 3D của marker trong không gian (ta quy định marker phẳng, nên Z=0, kích thước là L), (2) Tọa độ 2D của marker trên hình (có từ `ArucoDetector`), (3) Thông số camera (`camera_matrix`). Kết quả trả về là `tvec` (translation vector - khoảng cách X, Y, Z tính bằng mét) và `rvec` (rotation vector - góc nghiêng).
- **Hệ tọa độ OpenCV:** Trục Z đâm thẳng từ camera tới vật, trục X nằm ngang sang phải, trục Y hướng xuống dưới. Để hạ cánh, khoảng cách $X, Y$ của `tvec` chính là sai số metric (thay cho pixel error) cần đưa cho bộ điều khiển PID.

- [x] Tạo file `src/estimation/pose_estimator.py`:
```bash
touch src/estimation/pose_estimator.py  # (Tạo file code Python chứa class PoseEstimator, chịu trách nhiệm gọi hàm solvePnP để dịch từ pixel 2D sang tọa độ mét 3D)
```

- [x] Chèn nội dung mã nguồn vào `src/estimation/pose_estimator.py`:
```python
import cv2
import numpy as np

class PoseEstimator:
    def __init__(self, camera_matrix, dist_coeffs, marker_size=0.15):
        """
        marker_size: Kích thước cạnh của ArUco marker tính bằng mét (m). Mặc định 0.15m (15cm).
        """
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.marker_size = marker_size
        
        # Định nghĩa 4 góc của marker trong không gian 3D (Z=0 vì marker phẳng)
        # Thứ tự các góc: top-left, top-right, bottom-right, bottom-left
        half_size = self.marker_size / 2.0
        self.obj_points = np.array([
            [-half_size,  half_size, 0],
            [ half_size,  half_size, 0],
            [ half_size, -half_size, 0],
            [-half_size, -half_size, 0]
        ], dtype=np.float32)

    def estimate_pose(self, corners):
        """
        Dự đoán tvec (vị trí) và rvec (góc xoay) của marker.
        corners: Tọa độ 4 góc 2D nhận diện được từ ảnh (của 1 marker).
        """
        # solvePnP yêu cầu corner format phải đúng chuẩn
        img_points = np.array(corners, dtype=np.float32)
        success, rvec, tvec = cv2.solvePnP(
            self.obj_points, 
            img_points, 
            self.camera_matrix, 
            self.dist_coeffs,
            flags=cv2.SOLVEPNP_IPPE_SQUARE # Thuật toán tối ưu cho điểm phẳng hình vuông
        )
        return success, rvec, tvec
        
    def get_error_metric(self, tvec):
        """
        Lấy lỗi theo hệ tọa độ metric (mét) từ tvec.
        Trong hệ OpenCV: X là qua phải, Y là xuống dưới, Z là khoảng cách phía trước.
        """
        if tvec is None:
            return 0.0, 0.0, 0.0
        x_m = float(tvec[0][0])
        y_m = float(tvec[1][0])
        z_m = float(tvec[2][0])
        return x_m, y_m, z_m
```

## 3. Laptop (Machine A): Viết script kiểm tra Calibration & Pose
**Mục tiêu:** Xác minh rằng `PoseEstimator` hoạt động tốt.

- [x] Tạo thư mục chứa ảnh giả lập và script test:
```bash
touch scripts/test_pose_estimation.py   # (Tạo script thực thi để test độc lập logic của PoseEstimator mà không cần mở camera, giúp debug dễ dàng)
```

- [x] Chèn đoạn mã giả lập test vào `scripts/test_pose_estimation.py`:
```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import numpy as np
from src.estimation.camera_calibration import CameraCalibration
from src.estimation.pose_estimator import PoseEstimator

def test_pose():
    print("--- Test Pose Estimation ---")
    calib = CameraCalibration("configs/camera.yaml")
    cam_mat, dist = calib.get_parameters()
    print("Loaded Camera Matrix:\n", cam_mat)
    
    # Kích thước thật 0.15m (15cm)
    estimator = PoseEstimator(cam_mat, dist, marker_size=0.15)
    
    # Giả lập tọa độ 2D corners của marker khi nó nằm chính diện, cách camera tầm 1 mét
    # Giả sử kích thước trên pixel khoảng 80x80 px nằm ở trung tâm ảnh
    mock_corners = [[
        [280., 200.], # Top-left
        [360., 200.], # Top-right
        [360., 280.], # Bottom-right
        [280., 280.]  # Bottom-left
    ]]
    
    success, rvec, tvec = estimator.estimate_pose(mock_corners[0])
    
    if success:
        x_m, y_m, z_m = estimator.get_error_metric(tvec)
        print("\nPose Estimation Success!")
        print(f"X Offset (Lệch trái/phải) = {x_m:.3f} m")
        print(f"Y Offset (Lệch trên/dưới) = {y_m:.3f} m")
        print(f"Z Distance (Khoảng cách)  = {z_m:.3f} m")
    else:
        print("Pose Estimation Failed.")

if __name__ == "__main__":
    test_pose()
```

- [x] Kích hoạt môi trường và chạy thử:
```bash
source ../.venv/bin/activate
python scripts/test_pose_estimation.py
```
*(Yêu cầu: Kết quả Z Distance phải hiện ra một con số dương tính bằng mét hợp lý)*

## 4. Laptop (Machine A): Viết Báo cáo Calibration
- [x] Chèn nội dung sau vào `reports/calibration_report.md`:
```md
# Camera Calibration Report
- **Tình trạng:** Chạy bằng thông số giả lập (Synthetic intrinsics).
- **Độ phân giải:** 640x480
- **Camera Matrix (K):**
  [554.25, 0.0, 320.0]
  [0.0, 554.25, 240.0]
  [0.0, 0.0, 1.0]
- **Distortion:** Không sử dụng.
- **Pose Estimation Algorithm:** `cv2.SOLVEPNP_IPPE_SQUARE` 
- **Kết quả nghiệm thu:** Script Pose Estimator có khả năng phân giải thành công tọa độ X, Y, Z ra mét từ pixel 2D.
```

## 5. PC GPU (Machine B): UAV-Domain YOLO Baseline v0.1
**Mục tiêu:** Tạo baseline detector đầu tiên trên dữ liệu UAV thật, đồng thời chứng minh đầy đủ quy trình dataset engineering và experiment tracking.

💡 **Quyết định kiến trúc & Giải thích:**
- `coco8.yaml` chỉ dùng để smoke test môi trường, KHÔNG dùng làm baseline portfolio.
- Baseline portfolio bắt buộc dùng `VisDrone.yaml` (dữ liệu UAV thật từ trên không).
- Mô hình ban đầu dùng `yolo26n.pt` (Nano) để phù hợp mục tiêu edge deployment.

### Task 5A — Environment verification
- [x] **Kiểm tra GPU và môi trường**
```bash
cd ~/Projects/edge-vision-precision-landing/edge-ai-training
source ../.venv/bin/activate
nvidia-smi
python3 -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE')"
yolo checks
```
*(Đã kiểm tra thành công. GPU: NVIDIA GeForce RTX 3060 12GB. Ultralytics: 8.4.92, PyTorch: 2.13.0+cu130, CUDA: 13.0).*

### Task 5B — Pipeline smoke test
- [x] **Smoke test (Không phải baseline)**
```bash
yolo detect train data=coco8.yaml model=yolo26n.pt epochs=1 imgsz=640 batch=4 device=0 project=experiments name=SMOKE_coco8_yolo26n
```
*(Lưu ý: Không dùng metric vào portfolio, không gọi weight này là baseline).*

### Task 5C — Dataset source và experiment plan
- [x] **Khởi tạo thư mục Dataset Manifest & Audit**
```bash
mkdir -p datasets/manifests experiments
touch datasets/manifests/DATASET_SOURCES.md
touch datasets/manifests/DATASET_MANIFEST.json
touch experiments/EXP_PLAN.md
touch experiments/EXPERIMENT_REGISTRY.csv
```
*(Yêu cầu tối thiểu: Dataset name, source, license, mission target, classes, split strategy, expected metrics).*

### Task 5D — Dataset acquisition và audit
- [x] **Tạo báo cáo audit (Chờ tải xong VisDrone)**
```bash
mkdir -p reports/label_samples
touch reports/dataset_audit_visdrone_v1.md
```
*(Yêu cầu check: image-label pairing, corrupted images, invalid boxes, class distribution. Không đánh dấu hoàn thành nếu chỉ mới tải xong bộ dataset).*

### Task 5E — Train baseline thật
- [x] **Train baseline UAV-domain v0.1**
```bash
yolo detect train data=VisDrone.yaml model=yolo26n.pt epochs=30 patience=10 imgsz=640 batch=-1 device=0 seed=42 deterministic=True cache=disk project=experiments name=TRN_001_visdrone_yolo26n_640
```
*(Lưu ý fallback: Nếu thiếu VRAM dùng batch nhỏ hơn, thiếu RAM tắt cache. Đây là baseline, chưa phải final optimized model).*

### Task 5F — Evidence và quality gate
- [x] Xác nhận đã lưu đủ Artifacts của EXP_001 (`args.yaml`, `results.csv`, `best.pt`, `COMMAND.txt`, `NOTES.md`, failure cases). Mới được tính là hoàn thành Task 5.

## 6. Laptop (Machine A): Nhật ký & Code Commit
**Mục tiêu:** Ghi log ngày làm việc thứ 3 và commit code (Đảm bảo phản ánh ĐÚNG thực tế).

- [x] Tạo và chèn nội dung vào file `edge-vision-uav-landing/daily_logs/day_03.md`:
```md
# Day 03: Camera calibration + Pose estimation

## Done
- [Machine A] Khởi tạo thư mục `src/estimation` và tạo schema `camera.yaml` cho thông số camera matrix.
- [Machine A] Hoàn thiện class `CameraCalibration` để load thông số intrinsics.
- [Machine A] Hoàn thiện class `PoseEstimator` áp dụng `solvePnP` chuyển từ 2D pixels qua tọa độ 3D mét (tvec, rvec). Đã test giả lập chạy mượt mà.
- [Machine A] Xuất báo cáo Calibration giả lập.
- [Machine B] Đã xác minh CUDA và môi trường YOLO.
- [Machine B] Đã hoàn thành COCO8 smoke test.
- [Machine B] Đã tạo dataset manifest.
- [Machine B] (Tùy chọn ghi nếu xong) Đã tải/audit VisDrone và chạy xong EXP_001.

## Metrics
- Pose estimation functional test: PASS
- (Chỉ ghi metric training từ `results.csv` nếu EXP_001 đã hoàn thành).

## Problems
- Synthetic intrinsics chỉ phù hợp để kiểm tra luồng phần mềm và SITL. Sai số intrinsic tạo systematic scale/pose error. PID không thể đảm bảo sửa được một measurement model sai. Trước khi đưa ra claim về khoảng cách metric trên camera thật, cần calibration thật hoặc camera model chính xác.

## Decision
- Tạm sử dụng synthetic intrinsics cho software/SITL validation.
- Không dùng kết quả này làm bằng chứng độ chính xác metric trên camera thật.
- Real-camera calibration là task bắt buộc trước hardware validation.

## Tomorrow
- Laptop (Machine A): Thiết kế PID Controller Offline bằng Python cho 2 trục X, Y (Dựa trên metric error tính bằng mét lấy từ tvec).
- PC GPU (Machine B): Tiếp tục dataset audit/baseline (nếu EXP_001 chưa xong) HOẶC bắt đầu baseline evaluation/error analysis (nếu EXP_001 đã xong).
```

- [x] **Commit lên Git (Kiểm tra kĩ trước khi đẩy)**:
```bash
cd ~/Projects/edge-vision-precision-landing
git status
# (Kiểm tra .gitignore đã chặn các thư mục: datasets/raw, experiments, runs, *.pt, *.cache chưa)
git add src configs scripts reports docs daily_logs .gitignore
git commit -m "day03: add pose estimation and UAV dataset training plan"
```

## 7. Nghiệm thu Day 3 (Acceptance)
- [x] Pose functional test pass.
- [x] Camera/pose report không đưa claim chưa được đo.
- [x] CUDA/environment verification pass.
- [x] COCO8 smoke test pass.
- [x] Dataset source/license được ghi.
- [x] Dataset audit artifact tồn tại.
- [x] Nếu EXP_001 đã chạy: tồn tại `best.pt`, `results.csv`, curves, notes.
- [x] Daily log phản ánh đúng kết quả thực tế.
- [x] Git status không chứa dataset/checkpoint lớn ngoài ý muốn.
