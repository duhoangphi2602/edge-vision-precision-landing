# ROADMAP Dataset Realism Patch

## Mục đích

Patch này thay thế tư duy “train được YOLO là hoàn thành” bằng tư duy sản phẩm:

- Xác định rõ bài toán AI.
- Sử dụng dữ liệu UAV thực tế.
- Thu thập, chuyển đổi, gán nhãn và kiểm định dữ liệu.
- Tách tập dữ liệu theo video/sequence để tránh data leakage.
- Đánh giá detection và tracking bằng dữ liệu chưa từng thấy.
- Lưu đầy đủ nguồn, giấy phép, cấu hình và limitation.
- Chỉ dùng `coco8.yaml` làm smoke test kỹ thuật, không dùng làm baseline portfolio.

---

# 1. Bổ sung vào phần “Các lựa chọn kỹ thuật chính”

## AI Mission Definition

AI extension của project không phải là demo YOLO chung chung.

### Bài toán chính

**Phát hiện và bám theo một phương tiện mặt đất được chọn từ góc nhìn UAV hoặc UAV-like camera.**

### Scope v0.1

- Primary target: `vehicle`
- Nguồn class có thể được ánh xạ vào `vehicle`:
  - car
  - van
  - truck
  - bus
- Detector: YOLO nano trước, sau đó mới cân nhắc small.
- Tracker: ByteTrack/BoT-SORT hoặc tracker đơn giản có target-selection logic.
- Output cho control:
  - target_id
  - bounding box
  - center_x, center_y
  - normalized_error_x, normalized_error_y
  - confidence
  - timestamp
  - lost_duration
- Mục tiêu không phải phân loại mọi vật thể, mà là giữ ổn định target được chọn trong video UAV.

### Scope mở rộng

- `person` hoặc `two_wheeler` chỉ thêm sau khi vehicle baseline đạt quality gate.
- Không tăng số class chỉ để làm project trông lớn hơn.
- Mission-specific model được ưu tiên hơn model nhiều class nhưng dữ liệu thiếu hoặc không liên quan.

---

# 2. Thêm mục mới: Dataset Engineering Strategy

## Dataset tiers

### Tier 0 — Pipeline smoke test

Mục tiêu:

- Kiểm tra Ultralytics CLI.
- Kiểm tra CUDA.
- Kiểm tra data loader.
- Kiểm tra model có tạo checkpoint và log.

Dataset được phép:

- `coco8.yaml`

Quy tắc:

- Chỉ chạy 1–3 epochs.
- Experiment name bắt buộc có tiền tố `SMOKE_`.
- Không đưa metric của COCO8 vào Results Report.
- Không gọi weight từ COCO8 là “YOLO baseline v0.1”.
- Không dùng COCO8 để quyết định model tốt hay xấu.

### Tier 1 — Public UAV-domain baseline

Dataset ưu tiên:

1. **VisDrone2019-DET**
   - Aerial images.
   - Small and dense targets.
   - Có official train/validation/test-dev split.
   - Ultralytics hỗ trợ `VisDrone.yaml` và tự convert annotation.

2. **UAVDT**
   - UAV video sequences.
   - Tập trung mạnh vào vehicle detection và tracking.
   - Có điều kiện altitude, camera view, illumination và occlusion.
   - Phù hợp cho tracking evaluation và domain analysis.

Quyết định roadmap:

- Detection baseline v0.1: dùng `VisDrone.yaml`.
- Tracking evaluation v0.1: dùng video/sequence từ UAVDT hoặc VisDrone-VID.
- Nếu tài nguyên hạn chế, tạo reproducible subset từ official training split; không chọn ảnh thủ công theo cảm tính.

### Tier 2 — Project-specific adaptation set

Tạo một tập nhỏ nhưng liên quan trực tiếp tới demo:

- 300–800 frame được chọn từ 5–10 video/sequence khác nhau.
- Nguồn:
  - Video UAV có giấy phép cho phép sử dụng.
  - Video tự tạo trong Gazebo/SITL.
  - Video tự quay mô phỏng góc cao nếu ghi rõ domain gap.
- Gán nhãn bằng CVAT.
- Có annotation guideline.
- Có ít nhất một lần review label.
- Giữ riêng sequence test, không đưa frame cùng video vào cả train và validation.

### Tier 3 — Held-out challenge set

Không dùng để train hoặc tune.

Bao gồm các case:

- high altitude / tiny target
- oblique camera
- motion blur
- partial occlusion
- crowded traffic
- low contrast
- camera motion
- target leaving and re-entering frame

Đây là tập để quay demo thất bại/thành công và viết Error Analysis.

---

# 3. Quy tắc nguồn dữ liệu và crawling

## Không crawl tùy tiện

Không được tải hàng loạt ảnh từ Google Images hoặc video bất kỳ rồi coi là dataset hợp lệ.

Nếu crawling được sử dụng, bắt buộc:

- Chỉ lấy từ nguồn có giấy phép rõ ràng.
- Ghi URL nguồn, tác giả, license và ngày tải.
- Không chứa dữ liệu riêng tư hoặc nội dung không được phép sử dụng.
- Chạy deduplication.
- Kiểm tra ảnh hỏng.
- Kiểm tra domain relevance.
- Không để ảnh gần giống nhau lọt vào cả train và validation.

Ưu tiên theo thứ tự:

1. Official benchmark dataset.
2. Open-license video/image collection.
3. Synthetic data từ Gazebo.
4. Custom capture.
5. Crawling có kiểm soát và có license.

Crawling là kỹ năng bổ sung, không phải mục tiêu tự thân.

---

# 4. Cấu trúc workspace dữ liệu

```text
edge-ai-training/
├── datasets/
│   ├── raw/                         # Không sửa trực tiếp
│   │   ├── visdrone/
│   │   ├── uavdt/
│   │   └── custom_sources/
│   ├── interim/                     # Frame extract, converted annotations
│   ├── processed/
│   │   └── uav_vehicle_v1/
│   │       ├── images/
│   │       │   ├── train/
│   │       │   ├── val/
│   │       │   └── test/
│   │       ├── labels/
│   │       │   ├── train/
│   │       │   ├── val/
│   │       │   └── test/
│   │       └── data.yaml
│   ├── manifests/
│   │   ├── DATASET_SOURCES.md
│   │   ├── DATASET_MANIFEST.json
│   │   ├── ANNOTATION_GUIDELINES.md
│   │   └── SPLIT_MANIFEST.csv
│   └── README.md
├── scripts/
│   ├── download_dataset.py
│   ├── extract_video_frames.py
│   ├── convert_visdrone_to_yolo.py
│   ├── remap_vehicle_classes.py
│   ├── split_by_sequence.py
│   ├── audit_dataset.py
│   ├── detect_duplicates.py
│   └── visualize_labels.py
├── experiments/
├── reports/
│   ├── dataset_audit_v1.md
│   ├── class_distribution_v1.csv
│   └── error_analysis/
└── models/
```

Quy tắc:

- `raw/` là immutable.
- Mọi conversion phải chạy lại được bằng script.
- Không commit dataset lớn vào Git.
- Commit manifest, scripts, checksums, config và sample nhỏ.
- Có thể dùng DVC/Git LFS nếu triển khai kịp.

---

# 5. Dataset requirements và quality gate

Trước khi train baseline portfolio, dataset phải đạt:

## Source and legal

- [ ] Có tên dataset/source.
- [ ] Có đường dẫn nguồn.
- [ ] Có giấy phép hoặc điều kiện sử dụng được ghi lại.
- [ ] Có citation nếu dataset yêu cầu.

## Annotation

- [ ] Mọi ảnh có image-label pairing hợp lệ.
- [ ] Bounding box nằm trong giới hạn ảnh.
- [ ] Không có width/height bằng 0.
- [ ] Class ID nằm trong danh sách class.
- [ ] Có visualization sample để kiểm tra bằng mắt.
- [ ] Annotation guideline định nghĩa rõ trường hợp occlusion/truncation/ignore.

## Split integrity

- [ ] Split theo sequence/video, không random frame thuần túy.
- [ ] Không có frame gần kề của cùng video nằm ở train và validation.
- [ ] Không có duplicate hoặc near-duplicate xuyên split.
- [ ] Test set không dùng để tune.

## Coverage

- [ ] Có nhiều altitude/viewpoint.
- [ ] Có target nhỏ.
- [ ] Có motion blur hoặc camera motion.
- [ ] Có occlusion.
- [ ] Có background đa dạng.
- [ ] Có negative frames hoặc frame không có target nếu pipeline yêu cầu.

## Report

- [ ] Tổng số image/frame.
- [ ] Tổng số object.
- [ ] Class distribution.
- [ ] Bounding-box size distribution.
- [ ] Số sequence.
- [ ] Tỷ lệ train/val/test.
- [ ] Known limitations.

Không đạt các mục trên thì chưa được gọi là dataset version chính thức.

---

# 6. Thay Task 5 Day 3

## 5. PC GPU (Machine B): UAV-domain YOLO Baseline v0.1

**Mục tiêu:** Tạo baseline detector đầu tiên trên dữ liệu UAV thật, đồng thời chứng minh đầy đủ quy trình dataset engineering và experiment tracking.

### Quyết định kiến trúc

- `coco8.yaml` chỉ dùng để smoke test môi trường.
- Baseline portfolio dùng `VisDrone.yaml`.
- Bài toán v0.1 ưu tiên phát hiện vehicle từ aerial viewpoint.
- Giữ official split để có kết quả so sánh và tránh leakage.
- Model ban đầu dùng `yolo11n.pt` để phù hợp mục tiêu edge deployment.
- Baseline 640 px dùng làm mốc đầu tiên; độ phân giải cao hơn sẽ là experiment riêng vì VisDrone có nhiều small objects.

### Bước A — Kiểm tra GPU và môi trường

```bash
cd ~/Projects/edge-vision-precision-landing/edge-ai-training
source ../.venv/bin/activate

nvidia-smi
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE')"
yolo checks
```

### Bước B — Smoke test, không phải baseline

```bash
yolo detect train \
  data=coco8.yaml \
  model=yolo11n.pt \
  epochs=1 \
  imgsz=640 \
  batch=4 \
  device=0 \
  project=experiments \
  name=SMOKE_coco8_yolo11n
```

Pass khi:

- CUDA được sử dụng.
- Training hoàn thành.
- Có `weights/last.pt`.
- Không có lỗi dataset hoặc out-of-memory.

Sau khi pass, không dùng metric của run này trong portfolio.

### Bước C — Tạo dataset manifest trước khi train thật

Cập nhật:

```text
datasets/manifests/DATASET_SOURCES.md
datasets/manifests/DATASET_MANIFEST.json
experiments/EXP_PLAN.md
```

Ghi tối thiểu:

- Dataset: VisDrone2019-DET
- Task: aerial object detection
- Split: official train/val/test-dev
- Classes: 10 original classes
- Mission classes: vehicle-related classes
- Model: yolo11n pretrained
- Image size: 640
- Seed: 42
- Baseline purpose
- Known domain gaps

### Bước D — Chạy dataset audit

Train lần đầu bằng `VisDrone.yaml` sẽ tự tải và convert dataset nếu phiên bản Ultralytics hỗ trợ.

Sau khi dataset có trên máy, chạy hoặc tạo `scripts/audit_dataset.py` để kiểm tra:

- image/label count
- missing labels
- corrupted images
- invalid boxes
- class distribution
- bbox area distribution
- train/val leakage
- sample visualization

Output bắt buộc:

```text
reports/dataset_audit_visdrone_v1.md
reports/class_distribution_visdrone_v1.csv
reports/label_samples/
```

### Bước E — Train baseline UAV-domain v0.1

```bash
yolo detect train \
  data=VisDrone.yaml \
  model=yolo11n.pt \
  epochs=30 \
  patience=10 \
  imgsz=640 \
  batch=-1 \
  device=0 \
  seed=42 \
  deterministic=True \
  cache=disk \
  project=experiments \
  name=EXP_001_visdrone_yolo11n_640_baseline
```

Lý do bắt đầu 30 epochs:

- Đây là baseline, chưa phải final training.
- Early stopping giúp tránh chạy 50 epochs máy móc.
- Sau khi xem learning curves mới quyết định resume hoặc chạy experiment mới.

Nếu VRAM hoặc disk không đủ:

```bash
batch=8
cache=False
```

### Bước F — Lưu experiment artifacts

Experiment phải có:

```text
experiments/EXP_001_visdrone_yolo11n_640_baseline/
├── args.yaml
├── results.csv
├── results.png
├── confusion_matrix.png
├── confusion_matrix_normalized.png
├── PR_curve.png
├── P_curve.png
├── R_curve.png
├── F1_curve.png
├── labels.jpg
├── train_batch*.jpg
├── val_batch*_pred.jpg
└── weights/
    ├── best.pt
    └── last.pt
```

Tạo thêm:

```text
experiments/EXP_001_visdrone_yolo11n_640_baseline/NOTES.md
experiments/EXP_001_visdrone_yolo11n_640_baseline/COMMAND.txt
```

`NOTES.md` phải ghi:

- GPU
- Ultralytics version
- PyTorch/CUDA version
- Dataset version
- Train duration
- Best epoch
- mAP50
- mAP50-95
- precision
- recall
- observed failure cases
- quyết định keep/drop/resume

### Expected output

- Smoke test môi trường pass.
- VisDrone được tải/convert thành công.
- Có dataset audit report.
- Có baseline UAV-domain thật.
- Có `best.pt`.
- Có metrics và error samples.
- Không dùng COCO8 làm bằng chứng chất lượng.

### Quality gate

Task chỉ được đánh dấu hoàn thành khi:

- [ ] `SMOKE_coco8_yolo11n` pass.
- [ ] Dataset source/license/citation đã được ghi.
- [ ] Dataset audit không có lỗi nghiêm trọng.
- [ ] Baseline dùng `VisDrone.yaml`, không dùng COCO8.
- [ ] Experiment có seed và command tái lập được.
- [ ] Có `best.pt`, `results.csv` và curves.
- [ ] Có ít nhất 20 ảnh failure case được xem hoặc lưu.
- [ ] Có quyết định cho experiment kế tiếp.

---

# 7. Sửa Day 4 PC GPU

Thay vì chỉ chạy 416 và 640 trên dữ liệu không rõ nguồn:

## Experiment resolution and domain trade-off

- EXP_002: yolo11n, VisDrone, imgsz=640
- EXP_003: yolo11n, VisDrone, imgsz=960 hoặc 1280 nếu VRAM cho phép
- Cùng seed, cùng split, cùng model family.
- So sánh:
  - mAP50
  - mAP50-95
  - AP theo class
  - recall của tiny/small boxes
  - VRAM
  - train time
  - PyTorch inference latency
  - model size

Không kết luận model tốt hơn chỉ bằng mAP tổng; phải xét edge latency và target-size recall.

---

# 8. Sửa Day 5 PC GPU

## Detection error analysis v0.1

Tạo:

- `scripts/eval_yolo.py`
- `scripts/export_failure_cases.py`
- `reports/yolo_v0_1_report.md`

Báo cáo phải có:

- precision, recall, mAP50, mAP50-95
- per-class AP
- false positive samples
- false negative samples
- small-object failures
- occlusion failures
- motion-blur failures
- crowded-scene failures
- domain gap với demo project

Không chỉ xuất confusion matrix rồi kết thúc.

---

# 9. Sửa Day 6–8 PC GPU

## Day 6 — Project-specific data collection plan

- Chọn 5–10 video UAV/synthetic sequences.
- Lưu source/license.
- Extract frame theo interval, tránh lấy quá nhiều frame gần nhau.
- Tạo `ANNOTATION_GUIDELINES.md`.
- Khởi tạo CVAT task.
- Gán nhãn thử 50–100 frame.
- Review lỗi annotation trước khi label toàn bộ.

## Day 7 — Dataset version v0.1

- Hoàn thành tối thiểu 300 frame custom/synthetic có chất lượng.
- Split theo video:
  - train sequences
  - validation sequences
  - held-out test sequences
- Chạy audit.
- Đóng băng dataset version:
  - `uav_vehicle_custom_v0_1`
- Ghi checksum và manifest.

## Day 8 — Fine-tune v0.2

Hai chiến lược cần benchmark:

- Public-only: VisDrone baseline.
- Public + custom fine-tune: VisDrone -> custom adaptation.

Không train custom-only nếu custom set quá nhỏ.

Output:

- EXP_004 public baseline.
- EXP_005 public-to-custom fine-tune.
- Comparison report.

---

# 10. Sửa Day 10 và Day 13 tracking

## Tracking evaluation không được chỉ quay một video đẹp

Tracking phải chạy trên nhiều sequence và log:

- target ID continuity
- ID switches
- track fragmentation
- target lock rate
- lost-target duration
- recovery time
- center error jitter
- FPS
- P50/P95 latency

Split tracking test theo sequence.

Ít nhất:

- 3 easy sequences
- 3 medium sequences
- 3 hard sequences

Phải giữ lại cả failure video.

---

# 11. Sửa Quality Gates

## Gate 1 — Day 7

YOLO pass khi:

- [ ] Không dùng COCO8 làm baseline.
- [ ] Có public UAV-domain model.
- [ ] Có dataset manifest.
- [ ] Có dataset audit.
- [ ] Có train/val split hợp lệ.
- [ ] Có metrics và failure cases.
- [ ] Có kế hoạch custom adaptation data.

## Gate 2 — Day 14

YOLO/tracking pass khi:

- [ ] Có detector UAV-domain.
- [ ] Có custom/synthetic adaptation set.
- [ ] Có public-only vs fine-tuned comparison.
- [ ] Tracking chạy trên nhiều held-out sequences.
- [ ] Có target-lock, recovery và latency metrics.
- [ ] Có ONNX benchmark.
- [ ] Có limitation về domain gap.

## Gate 4 — Day 30

ML portfolio pass khi:

- [ ] Dataset source/license/citation đầy đủ.
- [ ] Conversion và audit scripts tái lập được.
- [ ] Không có data leakage đã biết.
- [ ] Model card liên kết đúng dataset version.
- [ ] Results report có error analysis.
- [ ] Demo chứa cả success và failure case.
- [ ] Không claim real-world robustness nếu chỉ test simulation/replay.

---

# 12. Quy tắc agent bắt buộc

Thêm vào cuối ROADMAP hoặc AGENT rules:

1. Agent không được dùng `coco8.yaml`, `coco128.yaml` hoặc dataset demo khác làm portfolio baseline.
2. Dataset demo chỉ được dùng cho smoke test và experiment name phải có `SMOKE_`.
3. Trước mọi training task, agent phải chỉ ra:
   - project mission
   - target classes
   - dataset source
   - license/citation
   - split strategy
   - expected metrics
   - experiment ID
4. Nếu chưa có dataset phù hợp, agent phải tạo task:
   - tìm nguồn
   - tải
   - convert
   - extract frame
   - annotate
   - review
   - audit
   - version
5. Agent không được bỏ qua dataset engineering chỉ để tạo `best.pt` nhanh.
6. Agent không được random split các frame từ cùng một video nếu điều đó gây leakage.
7. Agent không được đánh dấu training hoàn thành nếu chưa lưu:
   - command
   - config
   - seed
   - metrics
   - curves
   - best.pt
   - notes
8. Agent phải lưu failure cases và viết nguyên nhân dự kiến.
9. Agent phải ưu tiên dữ liệu liên quan đúng UAV viewpoint hơn dataset lớn nhưng sai domain.
10. Mọi claim trong README phải khớp với dữ liệu và test đã thực hiện.

---

# 13. Nguồn tham khảo chính

- Ultralytics COCO8: https://docs.ultralytics.com/datasets/detect/coco8/
- Ultralytics VisDrone: https://docs.ultralytics.com/datasets/detect/visdrone/
- VisDrone official repository: https://github.com/VisDrone/VisDrone-Dataset
- UAVDT official benchmark: https://sites.google.com/view/grli-uavdt
- Ultralytics data collection and annotation guide: https://docs.ultralytics.com/guides/data-collection-and-annotation/
- CVAT Ultralytics YOLO format: https://docs.cvat.ai/docs/dataset_management/formats/format-yolo-ultralytics/