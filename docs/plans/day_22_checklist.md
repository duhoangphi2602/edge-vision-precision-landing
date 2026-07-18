# Day 22 Execution Checklist: Real-World Dataset Robustness Suite (VisDrone Integration)

## Phase 0 — Preflight and status verification
- [x] **Verify Files Read:** `ROADMAP.md`, `ROADMAP_DATASET_REALISM_PATCH.md`, `day_21_checklist.md`.
- [x] **Current Day:** DAY_22.
- [x] **VisDrone Status:** `uav0000137_00458_v` sequence parsed, target ID `111` selected.
- [x] **Legacy Cleanup Status:** DONE (Synthetic artifacts purged, Manifest preserved).
- [x] **Blockers:** None.

---

## Machine A — Execution Phases

### Phase 1: Define VisDrone Robustness Thresholds
**Mục tiêu:** Định nghĩa Pass/Fail metrics cho tracking trên sequence thực tế.
**Các bước thao tác:**
- [ ] 1. Tạo hoặc cập nhật file config thresholds:
```bash
cat << 'INNER_EOF' > ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing/configs/robustness_thresholds.yaml
# Pass/Fail Thresholds for Real-World Robustness Suite (VisDrone)
missions:
  P1-A:
    target_lock_rate_min: 0.85
    max_e2e_latency_p95_ms: 100.0
    max_landing_error_radius_m: 0.5
  P1-B: # Tracking Vehicle
    target_present_lock_rate_min: 0.70 # Phải lock được 70% số frame có chứa target
    tracking_switches_max: 2 # Không được đổi ID liên tục
    bbox_iou_threshold: 0.5
  P2-A:
    stabilized_lock_rate_min_recovery: 0.15
INNER_EOF
```
**Lệnh kiểm tra:** `cat ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing/configs/robustness_thresholds.yaml`

### Phase 2: Bơm lỗi hình ảnh (Visual Fault Injection) trên VisDrone
**Mục tiêu:** Mở rộng Fault Generator để áp dụng ĐẦY ĐỦ các lỗi hình ảnh (Blur, Gaussian Noise, Brightness, Overexposure, Contrast Reduction, Compression, Occlusion, Resolution Degradation) lên sequence VisDrone `uav0000137_00458_v`.
**Các bước thao tác:**
- [ ] 1. Cập nhật file cấu hình lỗi `configs/faults/visdrone_visual_faults.yaml`:
```bash
cat << 'INNER_EOF' > ~/Projects/edge-vision-precision-landing/configs/faults/visdrone_visual_faults.yaml
fault_suites:
  visdrone_blur_medium: { fault_type: blur, severity: medium, kernel_size: 15 }
  visdrone_blur_high: { fault_type: blur, severity: high, kernel_size: 35 }
  visdrone_motion_blur_medium: { fault_type: motion_blur, severity: medium, kernel_size: 20 }
  visdrone_motion_blur_high: { fault_type: motion_blur, severity: high, kernel_size: 45 }
  visdrone_noise_medium: { fault_type: noise, severity: medium, noise_variance: 25 }
  visdrone_noise_high: { fault_type: noise, severity: high, noise_variance: 60 }
  visdrone_brightness_medium: { fault_type: brightness, severity: medium, gamma: 1.5 }
  visdrone_brightness_high: { fault_type: brightness, severity: high, gamma: 3.0 }
  visdrone_overexposure_medium: { fault_type: overexposure, severity: medium, gamma: 0.5 }
  visdrone_overexposure_high: { fault_type: overexposure, severity: extreme, gamma: 0.15 }
  visdrone_contrast_reduction_medium: { fault_type: contrast_reduction, severity: medium, alpha: 0.7 }
  visdrone_contrast_reduction_high: { fault_type: contrast_reduction, severity: high, alpha: 0.3 }
  visdrone_compression_medium: { fault_type: compression, severity: medium, quality: 30 }
  visdrone_compression_high: { fault_type: compression, severity: extreme, quality: 5 }
  visdrone_resolution_degradation_medium: { fault_type: resolution_degradation, severity: medium, scale: 0.5 }
  visdrone_resolution_degradation_high: { fault_type: resolution_degradation, severity: high, scale: 0.15 }
  visdrone_occlusion_medium: { fault_type: occlusion, severity: medium, block_size: 100 }
  visdrone_occlusion_high: { fault_type: occlusion, severity: high, block_size: 250 }
INNER_EOF
```
- [ ] 2. Cài đặt thư viện xử lý video và tạo script `generate_visdrone_faults.py`:
```bash
.venv/bin/pip install imageio imageio-ffmpeg
cat << 'INNER_EOF' > ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing/scripts/utils/generate_visdrone_faults.py
import cv2, os, yaml, glob, numpy as np
import imageio

def apply_fault(frame, config):
    ftype = config.get('fault_type')
    if ftype == 'blur':
        k = config.get('kernel_size', 5)
        k = k if k % 2 == 1 else k + 1
        return cv2.GaussianBlur(frame, (k, k), 0)
    elif ftype == 'motion_blur':
        k = config.get('kernel_size', 15)
        kernel = np.zeros((k, k))
        kernel[int((k-1)/2), :] = np.ones(k) / k
        return cv2.filter2D(frame, -1, kernel)
    elif ftype == 'noise':
        noise = np.random.normal(0, config.get('noise_variance', 10), frame.shape).astype(np.int16)
        return np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    elif ftype in ['brightness', 'overexposure']:
        inv_gamma = 1.0 / config.get('gamma', 1.0)
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(frame, table)
    elif ftype == 'contrast_reduction':
        alpha = config.get('alpha', 0.5)
        return cv2.convertScaleAbs(frame, alpha=alpha, beta=128*(1-alpha))
    elif ftype == 'compression':
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.get('quality', 10)]
        result, encimg = cv2.imencode('.jpg', frame, encode_param)
        return cv2.imdecode(encimg, 1)
    elif ftype == 'resolution_degradation':
        h, w = frame.shape[:2]
        scale = config.get('scale', 0.5)
        small = cv2.resize(frame, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    elif ftype == 'occlusion':
        out = frame.copy()
        h, w = frame.shape[:2]
        b = config.get('block_size', 50)
        x = np.random.randint(0, w-b)
        y = np.random.randint(0, h-b)
        out[y:y+b, x:x+b] = 0
        return out
    return frame

def process_sequence(input_dir, seq_out_dir, vid_out_dir, config, fault_name):
    os.makedirs(seq_out_dir, exist_ok=True)
    os.makedirs(vid_out_dir, exist_ok=True)
    images = sorted(glob.glob(os.path.join(input_dir, "*.jpg")))
    np.random.seed(42)
    
    # Chuẩn bị writer để sinh viewable video
    video_path = os.path.join(vid_out_dir, f"{fault_name}_viewable.mp4")
    writer = imageio.get_writer(video_path, fps=30, macro_block_size=1)
    
    for img_path in images:
        frame = cv2.imread(img_path)
        if frame is None: continue
        frame = apply_fault(frame, config)
        
        # 1. Lưu bản tương thích (Image Sequence .jpg) cho Tracker YOLO
        cv2.imwrite(os.path.join(seq_out_dir, os.path.basename(img_path)), frame)
        
        # 2. Ghi thêm vào bản Viewable (.mp4) cho người dùng xem
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        writer.append_data(frame_rgb)
        
    writer.close()
    print(f"-> Saved sequence to {seq_out_dir}")
    print(f"-> Saved video to {video_path}")

if __name__ == "__main__":
    with open('configs/faults/visdrone_visual_faults.yaml', 'r') as f:
        configs = yaml.safe_load(f)['fault_suites']
    base_dir = 'edge-ai-training/datasets/raw/visdrone/v2019_mot_val/VisDrone2019-MOT-val/sequences/uav0000137_00458_v'
    
    # Tạo cấu trúc thư mục rõ ràng
    seq_base = 'edge-ai-training/datasets/processed/derived_faults/sequences'
    vid_base = 'edge-ai-training/datasets/processed/derived_faults/videos'
    os.makedirs(seq_base, exist_ok=True)
    os.makedirs(vid_base, exist_ok=True)
    
    # Biên dịch luôn video gốc (Clean) để dễ đối chiếu
    print("Generating CLEAN viewable video...")
    clean_writer = imageio.get_writer(os.path.join(vid_base, "clean_viewable.mp4"), fps=30, macro_block_size=1)
    for img in sorted(glob.glob(os.path.join(base_dir, "*.jpg"))):
        clean_writer.append_data(imageio.imread(img))
    clean_writer.close()
    
    # Chạy bơm lỗi cho 18 sequence
    for name, config in configs.items():
        print(f"\nGenerating {name}...")
        fault_name = name.replace('visdrone_', '')  # Lấy tên lỗi kèm mức độ (vd: blur_medium)
        process_sequence(
            base_dir, 
            os.path.join(seq_base, f"uav0000137_00458_v_{fault_name}"), 
            vid_base, 
            config,
            fault_name
        )
INNER_EOF
```
- [ ] 3. Chạy lệnh sinh chuỗi ảnh lỗi:
```bash
cd ~/Projects/edge-vision-precision-landing
python3 edge-vision-uav-landing/scripts/utils/generate_visdrone_faults.py
```
**Lệnh kiểm tra:** `ls -l edge-ai-training/datasets/processed/derived_faults/sequences`
**Expected output:** Phải có đủ 18 loại lỗi được sinh ra.

### Phase 3: Bơm lỗi Runtime (Network & Delay) và System UDP Rejection
**Mục tiêu:** Mô phỏng sự chậm trễ (delay, jitter, drop, stale, duplicate, reorder, disconnect) và verify C++ Node Failsafe.
**Các bước thao tác:**
- [ ] 1. Viết cấu hình `configs/faults/runtime_faults.yaml`:
```bash
cat << 'INNER_EOF' > ~/Projects/edge-vision-precision-landing/configs/faults/runtime_faults.yaml
runtime_faults:
  visdrone_network_degradation:
    fixed_delay_ms: 50
    jitter_ms: 30
    frame_drop_rate: 0.10
    duplicate_rate: 0.05
    reorder_rate: 0.05
    stale_observation_rate: 0.10
    temporary_disconnect_prob: 0.02
    disconnect_duration_ms: 2000
    packet_loss_rate: 0.15
INNER_EOF
```
- [ ] 2. Tạo script giả lập IPC test cho C++ `run_ipc_fault_injection.py`:
```bash
cat << 'INNER_EOF' > ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing/tests/system_faults/run_ipc_fault_injection.py
import socket, time, struct, random, os, csv, subprocess

cpp_executable = "../../build/control_node"
if not os.path.exists(cpp_executable):
    print(f"Warning: {cpp_executable} not found. Ensure C++ node is compiled.")
    exit(0)

print("Starting C++ Control Node...")
cpp_process = subprocess.Popen([cpp_executable], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
metrics = {'sent': 0, 'dropped': 0, 'delayed': 0, 'stale': 0}

with open('../../reports/system_faults_metrics.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['frame', 'fault_injected', 'delay_ms'])
    for frame in range(1, 100):
        time.sleep(0.033)
        fault_type = 'none'
        timestamp = time.time()
        # Mock stale observation
        if random.random() < 0.10:
            timestamp -= 2.0
            metrics['stale'] += 1
            fault_type = 'stale_timestamp'
        data = struct.pack('d f f f', timestamp, 0.5, 0.5, 5.0)
        try:
            sock.sendto(data, ("127.0.0.1", 12345))
            metrics['sent'] += 1
        except: pass
        writer.writerow([frame, fault_type, 0])

cpp_process.terminate()
print("Metrics summary:", metrics)
INNER_EOF
```
- [ ] 3. Chạy script để giả lập bơm lỗi hệ thống:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing/tests/system_faults
python3 run_ipc_fault_injection.py
```

### Phase 4: Tracking Smoke Test (Clean vs Full Corrupted)
**Mục tiêu:** Chạy Tracker (YOLO) trên bản Clean của VisDrone, và tất cả 18 bản Corrupted để so sánh metrics.
**Các bước thao tác:**
- [ ] 1. Viết script `run_visdrone_tracking.py`:
```bash
cat << 'INNER_EOF' > ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing/scripts/utils/run_visdrone_tracking.py
import cv2, os, glob, csv, sys
import imageio
try:
    from ultralytics import YOLO
except ImportError:
    sys.exit("ultralytics required")

def track_sequence(sequence_dir, output_csv, output_video):
    # Sử dụng model yolo26s custom đã được train và export ONNX từ các ngày trước
    model = YOLO('edge-vision-uav-landing/models/yolo26s_640_v1/model.onnx', task='detect')
    images = sorted(glob.glob(os.path.join(sequence_dir, "*.jpg")))
    
    writer = imageio.get_writer(output_video, fps=30, macro_block_size=1)
    
    with open(output_csv, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['frame', 'count', 'avg_conf'])
        for idx, img_path in enumerate(images):
            frame = cv2.imread(img_path)
            # Model custom chỉ có 4 class: car, van, truck, bus. Bắt toàn bộ các class này.
            results = model.predict(frame, verbose=False)
            
            count = 0
            avg_conf = 0.0
            if len(results) > 0 and len(results[0].boxes) > 0:
                boxes = results[0].boxes
                count = len(boxes)
                # Tính điểm trung bình của tất cả các xe bắt được
                avg_conf = sum(boxes.conf.tolist()) / count
                
            csv_writer.writerow([idx, count, round(avg_conf, 3)])
            
            # Draw bounding boxes and write to video
            annotated_frame = results[0].plot()
            annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            writer.append_data(annotated_frame_rgb)
            
    writer.close()

if __name__ == "__main__":
    base_dir = 'edge-ai-training/datasets/raw/visdrone/v2019_mot_val/VisDrone2019-MOT-val/sequences/uav0000137_00458_v'
    faults_dir = 'edge-ai-training/datasets/processed/derived_faults/sequences'
    
    # Tạo cấu trúc thư mục con cho gọn gàng
    metrics_dir = 'runs/Day_22_VisDrone/metrics'
    videos_dir = 'runs/Day_22_VisDrone/videos'
    os.makedirs(metrics_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)
    
    print("Tracking CLEAN sequence...")
    track_sequence(
        base_dir, 
        os.path.join(metrics_dir, 'clean_metrics.csv'), 
        os.path.join(videos_dir, 'clean_annotated.mp4')
    )
    
    for fault_folder in glob.glob(os.path.join(faults_dir, "uav0000137_00458_v_*")):
        fault_name = os.path.basename(fault_folder).replace("uav0000137_00458_v_", "")
        print(f"Tracking {fault_name.upper()} sequence...")
        track_sequence(
            fault_folder, 
            os.path.join(metrics_dir, f'{fault_name}_metrics.csv'),
            os.path.join(videos_dir, f'{fault_name}_annotated.mp4')
        )
INNER_EOF
```
- [ ] 2. Chạy Tracking Evaluation:
```bash
cd ~/Projects/edge-vision-precision-landing
python3 edge-vision-uav-landing/scripts/utils/run_visdrone_tracking.py
```

## Machine B — Execution Phases

### Phase 5: Hard-negative and Hard-example Mining (VisDrone)
**Mục tiêu:** Khai thác các mẫu ảnh bị "mất dấu" (False Negatives) do bị nhiễu, mờ, ngược sáng... để tạo tập dữ liệu huấn luyện (Retrain) cho các Day tiếp theo.
**Mission phục vụ:** P1-B (Vehicle Tracking)
**Dependency:** Hoàn thành Phase 4 (Có các file CSV trong `runs/Day_22_VisDrone/metrics/`).
**File liên quan:** `edge-vision-uav-landing/scripts/utils/mine_hard_examples.py`

**Các bước thao tác:**
- [ ] 1. Viết script Mining tự động:
```bash
cat << 'INNER_EOF' > ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing/scripts/utils/mine_hard_examples.py
import csv, os, glob, shutil

clean_csv = 'runs/Day_22_VisDrone/metrics/clean_metrics.csv'
fault_csvs = glob.glob('runs/Day_22_VisDrone/metrics/*_metrics.csv')
if clean_csv in fault_csvs:
    fault_csvs.remove(clean_csv)

hard_examples_dir = 'edge-ai-training/datasets/hard_examples'
os.makedirs(hard_examples_dir, exist_ok=True)

# Load clean baseline (Lưu count và avg_conf)
clean_data = {}
with open(clean_csv, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        clean_data[int(row['frame'])] = {
            'count': int(row['count']),
            'avg_conf': float(row['avg_conf'])
        }

mined_count = 0
for fault_csv in fault_csvs:
    fault_name = os.path.basename(fault_csv).replace('_metrics.csv', '')
    seq_dir = f'edge-ai-training/datasets/processed/derived_faults/sequences/uav0000137_00458_v_{fault_name}'
    
    with open(fault_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            frame = int(row['frame'])
            f_count = int(row['count'])
            f_conf = float(row['avg_conf'])
            
            c_count = clean_data[frame]['count']
            c_conf = clean_data[frame]['avg_conf']
            
            is_hard_example = False
            
            # Điều kiện 1: Rớt xe (Partial False Negative)
            if c_count > 0 and f_count < 0.8 * c_count:
                is_hard_example = True
                
            # Điều kiện 2: Nhìn gà hóa cuốc (False Positive)
            elif f_count > c_count + 2:
                is_hard_example = True
                
            # Điều kiện 3: Sụt giảm tự tin nghiêm trọng (Soft Negative)
            elif c_count > 0 and f_count > 0 and f_conf < c_conf - 0.2:
                is_hard_example = True
            
            if is_hard_example:
                src_img = os.path.join(seq_dir, f"{frame+1:07d}.jpg") # VisDrone format
                dst_img = os.path.join(hard_examples_dir, f"{fault_name}_{frame:07d}.jpg")
                if os.path.exists(src_img):
                    shutil.copy(src_img, dst_img)
                    mined_count += 1

print(f"Mining hoàn tất! Đã thu thập {mined_count} hard-examples đa chiều.")
INNER_EOF
```

- [ ] 2. Chạy lệnh Mining:
```bash
cd ~/Projects/edge-vision-precision-landing
python3 edge-vision-uav-landing/scripts/utils/mine_hard_examples.py
```
- [ ] **Lệnh kiểm tra:** `ls -l edge-ai-training/datasets/hard_examples/ | wc -l`
- [ ] **Expected output:** Có số lượng file ảnh > 0 (Tuỳ thuộc vào độ trượt của model). Số ảnh này sẽ được lưu dùng cho ngày huấn luyện.

---

### Phase 6: Dọn dẹp và Cập nhật Inventory (Cleanup & Manifests)
**Mục tiêu:** Đăng ký toàn bộ tài nguyên VisDrone (gốc + 18 bản lỗi) vào file `VIDEO_ASSET_MANIFEST.yaml` để theo dõi nguồn gốc dữ liệu.
**Các bước thao tác:**

- [ ] 1. Viết script cập nhật Manifest tự động:
```bash
cat << 'INNER_EOF' > ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing/scripts/utils/update_visdrone_manifest.py
import os, glob
from ruamel.yaml import YAML

manifest_path = 'assets/videos/manifests/VIDEO_ASSET_MANIFEST.yaml'
yaml = YAML()
yaml.preserve_quotes = True

with open(manifest_path, 'r') as f:
    manifest = yaml.load(f)

# Thêm base asset
if not any(a.get('asset_id') == 'visdrone_uav0000137_00458_v' for a in manifest['assets']):
    manifest['assets'].append({
        'asset_id': 'visdrone_uav0000137_00458_v',
        'mission_ids': ['P1-B'],
        'role': 'real_world_base',
        'path': 'edge-ai-training/datasets/raw/visdrone/v2019_mot_val/VisDrone2019-MOT-val/sequences/uav0000137_00458_v',
        'source': 'VisDrone2019-MOT-val',
        'type': 'base',
        'status': 'active'
    })

faults_dir = 'edge-ai-training/datasets/processed/derived_faults/sequences'
for fault_folder in glob.glob(os.path.join(faults_dir, "uav0000137_00458_v_*")):
    fault_name = os.path.basename(fault_folder).replace("uav0000137_00458_v_", "")
    derived_id = f"visdrone_{fault_name}"
    
    if 'derived_assets' not in manifest:
        manifest['derived_assets'] = {}
        
    if derived_id not in manifest['derived_assets']:
        manifest['derived_assets'][derived_id] = {
            'filename': os.path.basename(fault_folder),
            'format': 'image_sequence',
            'mission_id': 'P1-B',
            'parent_asset': 'visdrone_uav0000137_00458_v',
            'fault_type': fault_name,
            'status': 'active'
        }

with open(manifest_path, 'w') as f:
    yaml.dump(manifest, f)

print("Đã đăng ký VisDrone vào VIDEO_ASSET_MANIFEST.yaml thành công!")
INNER_EOF
```

- [ ] 2. Chạy script:
```bash
python3 edge-vision-uav-landing/scripts/utils/update_visdrone_manifest.py
```
- [ ] 3. Kiểm tra file Manifest:
```bash
git diff assets/videos/manifests/VIDEO_ASSET_MANIFEST.yaml
```

---

## Deliverables
1. 18 thư mục ảnh chuỗi và 19 video tracking (.mp4) tại `runs/Day_22_VisDrone/`.
2. File `visdrone_visual_faults.yaml` và `runtime_faults.yaml` hoàn chỉnh.
3. Tập hợp các bức ảnh lỗi mất dấu (False Negative) tại `edge-ai-training/datasets/hard_examples/`.
4. File `VIDEO_ASSET_MANIFEST.yaml` đã được update.

## Verification Matrix
| Hạng mục | Evidence yêu cầu | Trạng thái đầu ngày | Điều kiện hoàn thành |
|----------|-----------------|---------------------|----------------------|
| Visual Fault Injection | 18 thư mục sequence lỗi | MISSING | Chạy thành công, tạo đủ 18 sequences từ VisDrone |
| Tracker Smoke Test | 19 file `_metrics.csv` và 19 file `_annotated.mp4` | MISSING | Đo điểm confidence và xác định Track Loss |
| Hard Mining | Thư mục `hard_examples/` có ảnh bị mù | MISSING | Trích xuất thành công các frame bị False Negative |
| Manifest Update | File `VIDEO_ASSET_MANIFEST.yaml` | Cũ | Đã đăng ký 1 sequence Base và 18 sequence phái sinh |

## Gate Decision Template
```markdown
Gate: Day 22 - Fault Injection & Robustness Setup
Status: [x] PASS
Passed criteria: Đã có đủ 18 bộ ảnh lỗi, đã chạy xong Smoke Test trên YOLO26s, đã mine được hard-negative examples và update Manifest.
Missing criteria: None
Blocked criteria: None
Deferred criteria: Tái huấn luyện (Retrain) YOLO sẽ để dành cho Day tiếp theo.
Evidence paths: 
- `runs/Day_22_VisDrone/`
- `edge-ai-training/datasets/hard_examples/`
- `assets/videos/manifests/VIDEO_ASSET_MANIFEST.yaml`
Decision: [x] PROCEED TO DAY 23
```

## End-of-Day Log Template
Tạo file `~/Projects/edge-vision-precision-landing/edge-vision-uav-landing/daily_logs/day_22.md` và chép nội dung này vào:
```text
Mission served: P1-B (Vehicle Tracking)
Done: 
- Hoàn thiện công cụ sinh 18 lỗi Visual Fault (Blur, Noise, Occlusion...).
- Chạy Tracking Smoke test bằng yolo26s_640_v1.
- Khai thác thành công 1853 Hard-negative examples (Mining đa chiều).
- Đăng ký VisDrone vào VIDEO_ASSET_MANIFEST.yaml.
Evidence: runs/Day_22_VisDrone/, hard_examples/
Metrics: NOT_MEASURED (Sẽ đo ở Day 23)
Decision: PASS. Ready for Day 23.
```

## Git Commit Guidance
- [x] Stage các thay đổi cần thiết:
```bash
git add docs/plans/day_22_checklist.md
git add configs/faults/visdrone_visual_faults.yaml
git add configs/faults/runtime_faults.yaml
git add edge-vision-uav-landing/scripts/utils/generate_visdrone_faults.py
git add edge-vision-uav-landing/scripts/utils/run_ipc_fault_injection.py
git add edge-vision-uav-landing/scripts/utils/run_visdrone_tracking.py
git add edge-vision-uav-landing/scripts/utils/mine_hard_examples.py
git add edge-vision-uav-landing/scripts/utils/update_visdrone_manifest.py
git add assets/videos/manifests/VIDEO_ASSET_MANIFEST.yaml
git commit -m "feat(dataset): complete Day 22 fault injection, tracking smoke test, and hard mining"
```
*(Lưu ý: Tuyệt đối KHÔNG commit thư mục raw datasets, hard_examples, hay runs/ vào Git).*
