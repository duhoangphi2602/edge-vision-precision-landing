# Day 24 Execution Checklist: Results Report, Model Card, Dataset Manifest & Limitations

## Phase 0 — Preflight and Status Verification
- [x] **Verify Files Read:** `ROADMAP.md`, `day_23_checklist.md`, `day_23.md`.
- [x] **Current Day:** DAY 24.
- [x] **Previous Day Status:** Day 23 `PASS_WITH_DOCUMENTED_LIMITATION`.
- [x] **Gate Status:** Day 23 Gate passed with limitation (missing true data from Day 21/22).
- [x] **Blockers / Dependencies:** Day 21 (Retrain YOLO) & Day 22 (Fault Injection) chưa hoàn thiện -> **BLOCKED** số liệu thực tế.
- [x] **Safe to proceed:** Việc tạo cấu trúc file `RESULTS.md`, `MODEL_CARD.md` và `DATASET_MANIFEST.md` có thể tiến hành độc lập. Theo chính sách Fallback của ROADMAP: "Leave cells explicitly `not measured` rather than estimate". Chúng ta sẽ điền sẵn form tài liệu và để trống (hoặc ghi `NOT_MEASURED`) các cell dữ liệu thực tế.

---

## Machine A — Execution Phases (Results Report)

### Phase 1: Tạo tài liệu RESULTS.md
**Mục tiêu:** 
Tổng hợp kết quả đo đạc từ các phase test (Landing, Tracking, Stabilization).
**Lý do thực hiện:** 
Đáp ứng Mission P1-A, P1-B, P2-A. Phân định rõ giữa Engineering Targets (Mục tiêu đề ra) và Measured Results (Kết quả đo được).
**Dependency:** Blocked phần dữ liệu thật bởi Day 22.
**Trạng thái hiện tại:** MISSING
**File liên quan:** `docs/RESULTS.md`

**Các bước thao tác:**
- [x] 1. Copy và chạy toàn bộ lệnh sau vào terminal để tạo file `RESULTS.md`.

````bash
cat << 'INNER_EOF' > ~/Projects/edge-vision-precision-landing/docs/RESULTS.md
# Project Results Report (v1.0)

> **Lưu ý:** Báo cáo này tách biệt giữa *Engineering Targets* và *Measured Results*. Do thiếu dữ liệu từ hệ thống (bị skip ở Day 21/22), các ô dữ liệu hiện tại được đánh dấu `NOT_MEASURED` hoặc `PENDING_VALIDATION` theo đúng Fallback Policy của Roadmap.

## 1. P1-A: Fixed Fiducial Precision Landing

### 1.1. Performance & Latency (Edge Runtime)
| Metric | Engineering Target | Measured Result | Evidence / Config |
|--------|-------------------|-----------------|-------------------|
| Marker-mode vision loop | >= 15 FPS | NOT_MEASURED | Pending Run ID |
| Observation stale threshold | <= 200 ms | NOT_MEASURED | Pending Run ID |
| C++ control loop | 30-50 Hz | NOT_MEASURED | Pending Run ID |

### 1.2. Accuracy & Dynamics (SITL)
| Metric | Engineering Target | Measured Result | Evidence / Config |
|--------|-------------------|-----------------|-------------------|
| Final horizontal error | <= 0.50 m | NOT_MEASURED | Pending Run ID |
| Pixel-only final error fallback | <= 30 px | NOT_MEASURED | Pending Run ID |
| Overshoot | <= 25% | NOT_MEASURED | Pending Run ID |
| Settling time | <= 5-8 s | NOT_MEASURED | Pending Run ID |
| Landing success | >= 8/10 | NOT_MEASURED | Pending Run ID |

---

## 2. P1-B: Single Ground-Vehicle Tracking

### 2.1. Robustness & Tracking Metrics
| Metric | Engineering Target | Measured Result | Evidence / Config |
|--------|-------------------|-----------------|-------------------|
| ONNX CPU FPS | >= 10-15 | NOT_MEASURED | Pending Run ID |
| P95 inference latency | <= 100-150 ms | NOT_MEASURED | Pending Run ID |
| Target-switch count | Minimized | NOT_MEASURED | Pending Run ID |
| Target lock rate (Clean baseline) | > 90% | NOT_MEASURED | Pending Run ID |
| Target lock rate (Faults) | > 70% | NOT_MEASURED | Pending Run ID |

---

## 3. P2-A: UAV Video Stabilization

### 3.1. Stabilization Trade-offs
| Metric | Measured Result | Note |
|--------|-----------------|------|
| Camera trajectory jitter | NOT_MEASURED | |
| Processing FPS | NOT_MEASURED | |
| Target lost-frame rate change| NOT_MEASURED | |

## 4. Known Limitations
- Chạy trên laptop mô phỏng CPU chưa thể hiện chính xác khả năng của companion computer thực tế trên UAV.
- Tỉ lệ rớt frame có thể tăng đột biến nếu CPU throttling.
INNER_EOF
````
- [x] 2. **Lệnh kiểm tra:** `cat ~/Projects/edge-vision-precision-landing/docs/RESULTS.md`
- [x] 3. **Expected output:** Hiển thị nội dung markdown của report vừa tạo, có đầy đủ các bảng được điền sẵn chữ `NOT_MEASURED`.
- [x] 4. **Evidence cần lưu:** Không (đây chỉ là thao tác ghi file).
- [x] 5. **Acceptance criteria:** File `RESULTS.md` được tạo thành công và tuân thủ Fallback Policy (không bịa số liệu).
- [x] 6. **Failure condition & Fallback:** Báo lỗi permission denied -> Chạy lệnh với quyền ghi hợp lệ.

---

## Machine B — Execution Phases (Model Card & Dataset Manifest)

### Phase 2: Tạo DATASET_MANIFEST.md
**Mục tiêu:**
Ghi lại thông tin chi tiết về tập dữ liệu (Nguồn, số lượng, phương pháp chia split, failure class).
**Lý do thực hiện:**
Phục vụ ML Mission, đảm bảo khả năng tracking nguồn gốc dữ liệu.
**Dependency:** Không.
**Trạng thái hiện tại:** MISSING
**File liên quan:** `docs/DATASET_MANIFEST.md`

**Các bước thao tác:**
- [x] 1. Copy và chạy lệnh sau để tạo `DATASET_MANIFEST.md`:

````bash
cat << 'INNER_EOF' > ~/Projects/edge-vision-precision-landing/docs/DATASET_MANIFEST.md
# Dataset Manifest (v1.0)

## 1. Nguồn Dữ Liệu
- **Tên Dataset:** UAV-Vehicle-Tracking-V1
- **Nguồn gốc:** VisDrone-VID, UAVDT, và Custom synthetic data.
- **Licenses:** Public Research / Custom.
- **Classes:** `car`, `van`, `truck`, `bus`.

## 2. Statistics & Splits
| Split | Images | Bounding Boxes | Mục đích |
|-------|--------|----------------|----------|
| Train | NOT_MEASURED | NOT_MEASURED | Đào tạo mô hình YOLO |
| Val   | NOT_MEASURED | NOT_MEASURED | Tuning thresholds |
| Test  | NOT_MEASURED | NOT_MEASURED | Đánh giá độc lập (Held-out) |

## 3. Limitations & Biases
- Data thu thập chủ yếu vào ban ngày, điều kiện ánh sáng tốt.
- Thiếu dữ liệu về môi trường mưa, sương mù dày đặc.
- Góc quay (angle) chủ yếu là góc nghiêng từ UAV, thiếu góc thẳng đứng hoàn toàn (nadir).
INNER_EOF
````
- [x] 2. **Lệnh kiểm tra:** `cat ~/Projects/edge-vision-precision-landing/docs/DATASET_MANIFEST.md`
- [x] 3. **Expected output:** Nội dung manifest hiện ra đầy đủ.
- [x] 4. **Evidence cần lưu:** Không.
- [x] 5. **Acceptance criteria:** Liệt kê đầy đủ license, classes, mục đích các split và list ra ít nhất 1 limitation rõ ràng.
- [x] 6. **Failure condition & Fallback:** Không ghi được file -> Đảm bảo đã mkdir thư mục `docs/`.

### Phase 3: Tạo MODEL_CARD.md
**Mục tiêu:**
Tạo Model Card chuẩn mực cho mô hình đã train.
**Lý do thực hiện:**
Cung cấp thông tin minh bạch về kiến trúc, tài nguyên chạy, giới hạn của mô hình cho người tích hợp.
**Dependency:** Blocked phần metric thật bởi Day 21.
**Trạng thái hiện tại:** MISSING
**File liên quan:** `docs/MODEL_CARD.md`

**Các bước thao tác:**
- [x] 1. Copy và chạy lệnh sau để tạo `MODEL_CARD.md`:

````bash
cat << 'INNER_EOF' > ~/Projects/edge-vision-precision-landing/docs/MODEL_CARD.md
# Model Card: Edge-YOLO-Vehicle

## 1. Thông Tin Chung
- **Model Version:** 1.0 (PENDING_VALIDATION)
- **Architecture:** YOLO (ONNX Exported)
- **Input Size:** 640x640 (RGB)
- **Task:** Object Detection (Classes: car, van, truck, bus)
- **Runtime:** ONNXRuntime (CPU/GPU)

## 2. Intended Use (Mục đích sử dụng)
- **Primary Use Case:** Nhận diện và cung cấp bounding box của phương tiện trên mặt đất từ camera UAV (Góc nhìn từ trên cao).
- **Out of Scope:** Không dùng để nhận diện người, động vật, biển báo giao thông. Không dùng để đo lường vận tốc phương tiện trong thế giới thực khi chưa calibrate camera.

## 3. Performance Metrics
> *Dữ liệu đang chờ từ experiment registry (Day 21)*
- **mAP50:** NOT_MEASURED
- **mAP50-95:** NOT_MEASURED
- **Inference Latency (CPU Batch 1):** NOT_MEASURED
- **Model Size:** NOT_MEASURED MB

## 4. Failure Behavior
- **False Negatives:** Dễ mất mục tiêu khi phương tiện đi vào bóng râm gắt hoặc bị che khuất bởi tán cây (Occlusion).
- **False Positives:** Đôi khi nhầm lẫn các vật thể hình hộp (ví dụ: container rác) thành xe tải nếu nhìn từ góc thẳng đứng.
INNER_EOF
````
- [x] 2. **Lệnh kiểm tra:** `cat ~/Projects/edge-vision-precision-landing/docs/MODEL_CARD.md`
- [x] 3. **Expected output:** Nội dung Model Card chuẩn hiện ra.
- [x] 4. **Evidence cần lưu:** Không.
- [x] 5. **Acceptance criteria:** Bao gồm rõ ràng Intended Use và Out of scope. Các thông số đo đạc để NOT_MEASURED.
- [x] 6. **Failure condition & Fallback:** Báo lỗi -> Tạo thủ công file hoặc cấp quyền cho file.

---

## Integration / Evidence Phase
Tổng hợp tài liệu:
- [x] Báo cáo kết quả: `docs/RESULTS.md`
- [x] Quản lý dữ liệu: `docs/DATASET_MANIFEST.md`
- [x] Quản lý mô hình: `docs/MODEL_CARD.md`

## Deliverables
- `docs/RESULTS.md` (Template)
- `docs/DATASET_MANIFEST.md` (Template)
- `docs/MODEL_CARD.md` (Template)

## Verification Matrix
| Hạng mục | Evidence yêu cầu | Trạng thái đầu ngày | Điều kiện hoàn thành |
|----------|-----------------|---------------------|----------------------|
| Results Report | File `RESULTS.md` | MISSING | Tồn tại file, tách biệt Engineering Targets & Measured Results, các metrics ghi `NOT_MEASURED`. |
| Dataset Manifest | File `DATASET_MANIFEST.md` | MISSING | Tồn tại file, liệt kê class, nguồn và split data. |
| Model Card | File `MODEL_CARD.md` | MISSING | Tồn tại file, ghi rõ Intended Use, Out of Scope và Limitations. |

## Gate Decision Template
```markdown
Gate: Day 24 - Final Documentation & Metrics
Status: [x] PASS_WITH_DOCUMENTED_LIMITATION
Passed criteria: Đã tạo đủ 3 tài liệu theo cấu trúc roadmap. Phân biệt rõ giữa Target và Result. Không bịa số liệu.
Missing criteria: Các con số đo lường thực tế (Bị block bởi Day 21, 22).
Blocked criteria: Day 21 & Day 22 chưa cung cấp log và run artifacts.
Deferred criteria: Điền số liệu thật vào các ô `NOT_MEASURED` sau khi nghiệm thu Day 21, 22.
Evidence paths:
- `docs/RESULTS.md`
- `docs/DATASET_MANIFEST.md`
- `docs/MODEL_CARD.md`
Decision: [x] PASS_WITH_DOCUMENTED_LIMITATION
```

## End-of-Day Log Template
Sau khi hoàn thành, copy mẫu sau vào `edge-vision-uav-landing/daily_logs/day_24.md`:
```markdown
Mission served: P1-A, P1-B, P2-A, ML
Done: 
- Tạo template chuẩn cho RESULTS.md, DATASET_MANIFEST.md, MODEL_CARD.md.
Evidence: docs/RESULTS.md, docs/DATASET_MANIFEST.md, docs/MODEL_CARD.md
Metrics: NOT_MEASURED (Pending Day 21 & 22)
Problems: Thiếu dữ liệu thực tế từ các ngày benchmark trước. Đã áp dụng fallback policy.
Decision: PASS_WITH_DOCUMENTED_LIMITATION
Tomorrow: Day 25 (Docker, setup scripts, and reproducibility)
```

## Git Commit Guidance
Chỉ hướng dẫn stage đúng file cần thiết.
- [x] Stage các file tài liệu vừa tạo:
```bash
git add docs/RESULTS.md docs/DATASET_MANIFEST.md docs/MODEL_CARD.md docs/plans/day_24_checklist.md edge-vision-uav-landing/daily_logs/day_24.md
```
- [x] Commit với message mô tả fallback:
```bash
git commit -m "docs: generate templates for results, model card and dataset manifest (pending day 21/22 metrics)"
```
