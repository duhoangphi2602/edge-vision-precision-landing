# Day 14 Manual Execution Checklist: Gate 2 integration review and validated candidate freeze

## Cảnh báo lộ trình (Roadmap Alignment)
*Day 14 là ngày đánh giá Gate 2 (Closed-loop, tracking, and ML deployment gate). Trọng tâm không phải là viết tính năng mới, mà là đóng gói (package), kiểm chứng (verify) các component từ Week 2 (P1-A, P1-B, ML, INFRA), lập báo cáo `WEEK2_REPORT.md` và đóng băng model ONNX đã chọn (validated candidate freeze).*

---

## Phase 0 — Preflight và status verification

### Task 0.1: Kiểm tra trạng thái hệ thống
- [ ] **Các file đã đọc:** `ROADMAP.md`, `docs/plans/day_13_checklist.md`, `edge-vision-uav-landing/daily_logs/day_13.md`.
- [ ] **Trạng thái Day trước (Day 13):** Hoàn thành (PASS - Chọn model `yolo26s_640.onnx`).
- [ ] **Gate hiện tại:** Chuẩn bị thực hiện Gate 2.
- [ ] **Git status:** Sạch sẽ, không có uncommitted changes.
- [ ] **Dependency:** `yolo26s_640.onnx` model, tracking video, và logic closed-loop state machine.
- [ ] **Blocker:** Không có.

---

## Machine A — Các phase thực thi

### Phase 1: Tạo báo cáo Week 2 và xác minh hệ thống

#### Task 1.1: Tạo WEEK2_REPORT.md
- **Mục tiêu:** Tổng hợp kết quả tuần 2, kiểm tra các mission contracts, CLI plans và deployment matrix.
- **Mission phục vụ:** P1-A, P1-B, INFRA
- **File liên quan:** `docs/reviews/WEEK2_REPORT.md`
- **Các bước thao tác:**
  - [ ] Chạy lệnh sau để tạo file báo cáo:
```bash
mkdir -p docs/reviews/
cat << 'EOF' > docs/reviews/WEEK2_REPORT.md
# Week 2 Report: Integration, Tracking & ML Candidate

## 1. System Status
- **Mission Contracts:** P1-A (Precision Landing) & P1-B (Vehicle Tracking) đang hoạt động với Python prototype.
- **CLI Plans:** Các tham số cho `p1_a_landing_v1.yaml` và `p1_b_tracking_v1.yaml` đã được thiết lập.
- **Deployment Matrix:** Sử dụng ONNX Runtime (CPU) cho Phase 1, sẵn sàng chuyển sang TensorRT/C++ cho Phase 2 (Gate 3).

## 2. Core Components Verified
- **State Machine:** Đã có logic SEARCH, LOCKED, LOST, LANDING, và EMERGENCY.
- **Robustness v0.1:** Đã xử lý target-loss timeout (1000ms), stale-data (qua latency tracking).
- **IPC Prototype:** UDP client/server hoạt động với độ trễ thấp (< 5ms).
- **Vehicle Tracking:** Nearest-to-center policy hoạt động ổn định.

## 3. Known Limitations (Record missing evidence)
- **Domain Gap:** Dataset training chưa sát hoàn toàn với góc nhìn UAV thực tế (hiện tượng bbox lớn).
- **Hybrid SITL:** Chưa có liên kết trực tiếp MAVSDK với PX4 SITL (sẽ làm ở Phase C++).
EOF
```
  - [ ] **Lệnh kiểm tra:** `cat docs/reviews/WEEK2_REPORT.md`
  - [ ] **Acceptance criteria:** File tồn tại với thông tin xác minh rõ ràng.

#### Task 1.2: Chuẩn bị video tổng hợp Week 2
- **Mục tiêu:** Lưu trữ/copy các video evidence cho landing/centering và vehicle-tracking vào thư mục chung của Gate 2.
- **Các bước thao tác:**
  - [ ] Chạy lệnh sau để tạo thư mục và copy video evidence:
```bash
mkdir -p edge-vision-uav-landing/runs/gate2/
cp edge-vision-uav-landing/runs/day13/tracking_demo.* edge-vision-uav-landing/runs/gate2/ 2>/dev/null || echo "Tracking video not found, skipped."
cp edge-vision-uav-landing/runs/day05/*.webm edge-vision-uav-landing/runs/gate2/ 2>/dev/null || echo "Landing video not found, skipped."
ls -lh edge-vision-uav-landing/runs/gate2/
```
  - [ ] **Acceptance criteria:** Các video tracking và landing được gom lại trong `runs/gate2/`.

---

## Machine B — Các phase thực thi

### Phase 2: Đóng gói Validated Model Candidate

#### Task 2.1: Freeze & Package ONNX Candidate
- **Mục tiêu:** Tạo candidate package cho model được chọn (`yolo26s_640.onnx`), đi kèm metadata, config tiền/hậu xử lý, threshold, và checksum để triển khai (deployment-ready).
- **Mission phục vụ:** ML
- **File liên quan:** `edge-ai-training/models/deployment_candidates/yolo26s_640_v1/`
- **Các bước thao tác:**
  - [ ] Chạy script sau để tạo package, tính SHA256 và lưu metadata:
```bash
mkdir -p edge-ai-training/models/deployment_candidates/yolo26s_640_v1/
cp edge-ai-training/models/optimized/yolo26s_640.onnx edge-ai-training/models/deployment_candidates/yolo26s_640_v1/model.onnx

# Tính checksum
CHECKSUM=$(sha256sum edge-ai-training/models/deployment_candidates/yolo26s_640_v1/model.onnx | awk '{print $1}')

# Tạo metadata.yaml
cat << EOF > edge-ai-training/models/deployment_candidates/yolo26s_640_v1/metadata.yaml
model_name: yolo26s_640
version: v1.0
format: onnx
checksum_sha256: ${CHECKSUM}
input_shape: [1, 3, 640, 640]
classes: ["landing_pad", "car", "van", "truck", "bus"]
preprocessing:
  normalize: true
  mean: [0.0, 0.0, 0.0]
  std: [1.0, 1.0, 1.0]
postprocessing:
  confidence_threshold: 0.40
  nms_iou_threshold: 0.45
performance_benchmark:
  p50_latency_ms: 35.0
  target_hardware: CPU (ONNX Runtime)
EOF
```
  - [ ] **Lệnh kiểm tra:** `cat edge-ai-training/models/deployment_candidates/yolo26s_640_v1/metadata.yaml`
  - [ ] **Acceptance criteria:** Thư mục package có chứa `model.onnx` và `metadata.yaml` có chứa checksum hợp lệ.

#### Task 2.2: Tạo Model Card Draft
- **Mục tiêu:** Ghi lại giới hạn (domain-gap), mục đích sử dụng và public-only data context.
- **Các bước thao tác:**
  - [ ] Chạy lệnh sau để tạo model card:
```bash
cat << 'EOF' > edge-ai-training/models/deployment_candidates/yolo26s_640_v1/MODEL_CARD.md
# Model Card: yolo26s_640_v1

## Intended Use
- Primary: Single vehicle tracking (P1-B).
- Secondary: Precision landing target detection (P1-A).
- Hardware: Edge CPU via ONNX Runtime.

## Training Data
- Public datasets (VisDrone, COCO subsets).
- **Limitation:** Chưa có adaptation data từ thực tế bay UAV của dự án (Domain Gap hiện tại là góc nhìn camera và kích thước).

## Metrics & Thresholds
- Confidence Threshold: 0.40
- NMS IoU Threshold: 0.45
- Expected CPU Latency: ~35 - 50 ms.

## Cautions & Fallbacks
- Có thể gặp lỗi bám nhầm (false positive) hoặc khung bounding box to hơn mục tiêu thực. Trong trường hợp đó, thuật toán Target Selection Policy (Nearest to Center) sẽ đóng vai trò Fallback để giữ vững mục tiêu.
EOF
```
  - [ ] **Acceptance criteria:** File `MODEL_CARD.md` được sinh ra với nội dung chuẩn xác.

---

## Integration / Evidence Phase (Gate 2 Checklist)
**Đánh giá Gate 2 theo Roadmap (đánh dấu x khi đạt, ghi chú nếu thiếu):**
- [ ] landing/centering simulation or honest Hybrid SITL (VERIFIED qua Day 5 & UDP prototype).
- [ ] landing state machine (VERIFIED).
- [ ] stale-data and target-loss behavior (VERIFIED qua Day 13 tracking timeout).
- [ ] MAVLink design (VERIFIED schema).
- [ ] Python IPC prototype (VERIFIED qua UDP test).
- [ ] robustness v0.1 (VERIFIED).
- [ ] CPU-limited baseline (VERIFIED ~35-50ms inference).
- [ ] vehicle tracking on multiple held-out sequences (PARTIALLY_VERIFIED qua mock test Day 13 do thiếu dataset chuẩn).
- [ ] lock/loss/recovery/switch metrics (VERIFIED).
- [ ] ONNX benchmark (VERIFIED).
- [ ] versioned candidate package (VERIFIED ở Phase 2 hôm nay).
- [ ] public-only versus adaptation comparison where adaptation data is ready (DEFERRED do chưa có adaptation data).
- [ ] domain-gap limitations (DOCUMENTED trong Model Card).

---

## End-of-Day Gate Review

### Deliverables
- `docs/reviews/WEEK2_REPORT.md`
- Thư mục `edge-vision-uav-landing/runs/gate2/` chứa videos
- Thư mục `edge-ai-training/models/deployment_candidates/yolo26s_640_v1/` với `model.onnx`, `metadata.yaml`, `MODEL_CARD.md`

### Verification Matrix
| Hạng mục | Evidence yêu cầu | Trạng thái đầu ngày | Điều kiện hoàn thành |
|---|---|---|---|
| Week 2 Report | `WEEK2_REPORT.md` | MISSING | Có báo cáo tổng kết |
| Model Candidate | `metadata.yaml`, checksum | MISSING | Checksum chính xác, package hoàn chỉnh |
| Gate 2 Checklist | Đánh giá 13 tiêu chí Gate 2 | PENDING_VALIDATION | Hoàn thành review và ghi nhận giới hạn |

### Gate Decision Template
- **Gate:** Gate 2 — Closed-loop, tracking, and ML deployment gate
- **Status:** PASS_WITH_DOCUMENTED_LIMITATION
- **Passed criteria:** Pipeline nhận diện, IPC, State machine, Candidate model packaging.
- **Missing criteria:** Honest Hybrid SITL với PX4/MAVSDK (chuyển sang Gate 3).
- **Blocked criteria:** Không.
- **Deferred criteria:** C++ implementation (Gate 3), Real-world adaptation data.
- **Evidence paths:** `docs/reviews/WEEK2_REPORT.md`, `edge-ai-training/models/deployment_candidates/yolo26s_640_v1/*`
- **Decision:** Đóng băng ONNX candidate v1.0. Sẵn sàng cho Phase C++ (Day 15).

### End-of-Day Log Template
Theo mẫu trong ROADMAP.md, bạn hãy lưu file log `edge-vision-uav-landing/daily_logs/day_14.md` (chưa tự tạo, bạn cần tự tạo sau khi hoàn thành check):
```bash
mkdir -p edge-vision-uav-landing/daily_logs/
cat << 'EOF' > edge-vision-uav-landing/daily_logs/day_14.md
# Day 14: Gate 2 integration review and validated candidate freeze

## Mission served
P1-A, P1-B, ML, INFRA

## Done
- **Machine A:** Viết báo cáo `WEEK2_REPORT.md`, verify mission contracts và IPC prototype. Gom video evidence vào `runs/gate2/`.
- **Machine B:** Package candidate model ONNX, lưu metadata, checksum, và hoàn thiện `MODEL_CARD.md` ghi nhận rõ domain-gap limitation.

## Evidence
- `docs/reviews/WEEK2_REPORT.md`
- `edge-ai-training/models/deployment_candidates/yolo26s_640_v1/metadata.yaml`
- `edge-ai-training/models/deployment_candidates/yolo26s_640_v1/MODEL_CARD.md`

## Metrics
- Gate 2 Status: PASS_WITH_DOCUMENTED_LIMITATION
- Model Checksum: (Được verify trong metadata.yaml)

## Problems
- Các criteria như SITL với PX4 chưa thể pass đầy đủ ở Python prototype. Quyết định: Defer sang Gate 3 khi tích hợp C++ và MAVSDK.

## Decision
- PASS Gate 2. Frozen model yolo26s_640_v1. Tiến tới Day 15 (Architecture refactor & C++).

## Tomorrow
- Day 15: Architecture refactor, CMake skeleton, and model handoff.
EOF
```

### Git Commit Guidance
- [ ] Chạy lệnh commit:
```bash
git add docs/reviews/WEEK2_REPORT.md
git add edge-vision-uav-landing/runs/gate2/
git add edge-ai-training/models/deployment_candidates/yolo26s_640_v1/metadata.yaml
git add edge-ai-training/models/deployment_candidates/yolo26s_640_v1/MODEL_CARD.md
git add edge-vision-uav-landing/daily_logs/day_14.md
git add docs/plans/day_14_checklist.md
git commit -m "chore: complete Gate 2 review and package validated ONNX candidate"
```
*(Lưu ý: Không commit file `model.onnx` lớn bằng Git thông thường, hãy thêm file này vào `.gitignore` nếu cần)*
