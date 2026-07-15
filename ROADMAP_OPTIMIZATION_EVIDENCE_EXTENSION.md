# ROADMAP Optimization & Evidence Extension

## Mục đích

Phần mở rộng này bổ sung cho `ROADMAP_DATASET_REALISM_PATCH.md`.

Mục tiêu là bảo đảm portfolio không chỉ chứng minh khả năng:

- tải dataset;
- train YOLO;
- tạo `best.pt`;

mà còn chứng minh khả năng:

- xác định mục tiêu tối ưu;
- thiết kế thí nghiệm có kiểm soát;
- tối ưu dữ liệu dựa trên lỗi;
- tối ưu runtime cho edge deployment;
- so sánh trước/sau bằng số liệu;
- lựa chọn mô hình theo accuracy–latency–memory trade-off;
- xác nhận kết quả có thể lặp lại.

---

# 1. Optimization Objective & Deployment Constraints

Trước khi thực hiện tối ưu, mỗi experiment plan phải ghi rõ:

- Tối ưu chỉ số nào.
- Ràng buộc nào không được vi phạm.
- Máy và runtime dùng để benchmark.
- Dataset version và split.
- Baseline dùng để so sánh.

## Chỉ số chất lượng

- mAP50.
- mAP50-95.
- Precision.
- Recall.
- AP theo class.
- AP hoặc recall đối với small/tiny object.
- False positive trên negative sequences.
- False negative trên hard sequences.
- Target-lock rate khi tích hợp tracker.
- Recovery time sau khi mất target.

## Chỉ số deployment

- Batch size inference = 1.
- FPS.
- Mean latency.
- P50 latency.
- P95 latency.
- Peak RAM.
- Peak VRAM nếu chạy GPU.
- CPU utilization.
- Model size.
- Thời gian khởi động model.
- Control-loop jitter khi perception chạy đồng thời.

## Ràng buộc ban đầu

Các giá trị sau là mục tiêu kỹ thuật ban đầu, không được ghi là kết quả nếu chưa đo:

- CPU inference FPS >= 10.
- P95 inference latency <= 150 ms.
- Không làm control loop hoặc failsafe bị nghẽn.
- Batch size benchmark = 1.
- Model phải export và chạy được bằng ONNX Runtime.
- Model được chọn phải nằm trên Pareto frontier về accuracy–latency–memory.

Các ngưỡng được phép điều chỉnh sau khi có benchmark đầu tiên, nhưng mọi thay đổi phải được ghi trong decision log.

---

# 2. Experiment Registry & Ablation Protocol

Tạo:

```text
edge-ai-training/experiments/EXPERIMENT_REGISTRY.csv
edge-ai-training/experiments/EXPERIMENT_TEMPLATE.md
edge-ai-training/reports/ablation_report.md
```

## Trường bắt buộc trong registry

- experiment_id
- date
- purpose
- parent_experiment
- dataset_version
- train_split
- val_split
- test_split
- model
- pretrained_weights
- image_size
- epochs
- patience
- batch
- optimizer
- learning_rate
- augmentation_profile
- seed
- runtime
- precision
- status
- best_epoch
- mAP50
- mAP50_95
- precision_metric
- recall_metric
- AP_small
- FPS
- latency_p50_ms
- latency_p95_ms
- peak_ram_mb
- model_size_mb
- artifact_path
- decision
- notes

## Quy tắc ablation

- Mỗi experiment chỉ thay đổi một nhóm yếu tố chính.
- Không đồng thời thay model, dataset, image size và augmentation trong cùng một ablation.
- Giữ nguyên split khi so sánh.
- Giữ nguyên benchmark input và runtime.
- Mọi experiment phải chỉ ra baseline/parent.
- Experiment lỗi hoặc kết quả kém vẫn phải được ghi.
- Không chọn model dựa vào một metric duy nhất.

## Experiment sequence khuyến nghị

| ID | Thay đổi chính | Mục đích |
|---|---|---|
| EXP_001 | YOLO11n, 640, public UAV dataset | Baseline |
| EXP_002 | Image size cao hơn | Small-object recall |
| EXP_003 | Augmentation profile | Robustness |
| EXP_004 | YOLO11s | Capacity trade-off |
| EXP_005 | Public → custom fine-tune | Domain adaptation |
| EXP_006 | ONNX FP32 | Runtime baseline |
| EXP_007 | FP16 nếu backend hỗ trợ | Precision/runtime trade-off |
| EXP_008 | INT8 quantization | Edge optimization |
| EXP_009 | Hard-negative mining | Giảm false positive |
| EXP_010 | Hard-example fine-tuning | Giảm failure case |

Không bắt buộc chạy toàn bộ experiment nếu kết quả trước đó đã chứng minh một nhánh không phù hợp. Quyết định dừng phải có lý do và số liệu.

---

# 3. Quantization & Runtime Optimization

Sau khi chọn được candidate model, benchmark tối thiểu:

- PyTorch FP32.
- ONNX Runtime FP32.
- OpenVINO FP32 hoặc FP16 nếu phù hợp.
- INT8 chỉ thực hiện khi có calibration dataset đại diện.

## Quy tắc INT8

- Calibration set không được lấy từ held-out test set.
- Calibration set phải có đủ điều kiện sáng, góc nhìn và kích thước target.
- Báo cáo accuracy drop sau quantization.
- Không chọn INT8 nếu giảm recall của mission target vượt mức chấp nhận.
- Ghi rõ backend, opset, dynamic/static shape và số thread.

## Output

```text
reports/runtime_benchmark.csv
reports/quantization_report.md
models/model_registry.json
```

---

# 4. Hard-Negative & Hard-Example Mining

## Hard-negative mining

Chạy model trên video/ảnh không có target mong muốn để tìm false positive, ví dụ:

- mái nhà;
- bóng đổ;
- biển báo;
- vật thể hình chữ nhật;
- texture giống xe;
- phương tiện quá xa hoặc không thuộc scope.

Lưu:

```text
datasets/interim/hard_negatives/
reports/error_analysis/hard_negative_manifest.csv
```

## Hard-example mining

Thu thập các case:

- tiny target;
- motion blur;
- occlusion;
- low contrast;
- target sát biên ảnh;
- camera nghiêng;
- crowded scene;
- target rời và quay lại frame.

Mỗi sample phải có:

- source sequence;
- frame index;
- failure category;
- model version;
- prediction;
- ground truth;
- quyết định thêm/không thêm vào training.

Không đưa trực tiếp toàn bộ failure từ test set vào training. Phải tạo hoặc tìm sample tương tự từ train/custom pool để bảo toàn held-out test.

---

# 5. Before/After Dataset Cleaning Evidence

Tạo hai snapshot:

```text
reports/dataset_audit_before_cleaning.md
reports/dataset_audit_after_cleaning.md
reports/dataset_cleaning_delta.csv
```

Báo cáo delta tối thiểu:

- corrupted images;
- missing labels;
- invalid boxes;
- empty labels;
- duplicate images;
- near-duplicates;
- cross-split duplicates;
- class distribution;
- bbox-size distribution;
- số sequence;
- số sample bị loại;
- lý do loại.

Không được tuyên bố “dataset clean” nếu chưa có script audit và bằng chứng trước/sau.

---

# 6. Before/After Optimization Comparison

Mỗi thay đổi được giữ lại phải có bảng so sánh với baseline:

| Metric | Baseline | Candidate | Delta | Constraint pass |
|---|---:|---:|---:|---|
| mAP50-95 | | | | |
| Vehicle recall | | | | |
| AP small | | | | |
| FPS | | | | |
| P95 latency | | | | |
| Peak RAM | | | | |
| Model size | | | | |
| Target-lock rate | | | | |

Mọi cải thiện phải ghi rõ chi phí đánh đổi.

Không dùng từ “optimized”, “faster”, “more robust” nếu không có baseline và số đo tương ứng.

---

# 7. Pareto-Based Model Selection

Không tự động chọn model có mAP cao nhất.

## Hard constraints

Loại model nếu:

- không đạt runtime target;
- vượt giới hạn memory;
- làm nghẽn control loop;
- không export được sang runtime mục tiêu;
- recall mission target giảm quá mức;
- fail trên held-out challenge set.

## Soft objectives

Trong các model đạt hard constraints, ưu tiên:

1. Vehicle/mission-target recall.
2. AP small.
3. Target-lock rate.
4. P95 latency thấp.
5. Model size nhỏ.
6. mAP50-95.

Tạo:

```text
reports/model_selection_matrix.csv
reports/model_selection_decision.md
```

`model_selection_decision.md` phải giải thích vì sao model được chọn phù hợp với mission, không chỉ vì có metric cao nhất.

---

# 8. Repeatability & Multi-Seed Validation

Trong giai đoạn khám phá có thể dùng một seed cố định, ví dụ `42`.

Trước khi gọi một cấu hình là final candidate:

- Chạy tối thiểu 3 seed, ví dụ `42`, `123`, `3407`.
- Giữ nguyên dataset, split và hyperparameter.
- Báo cáo mean và standard deviation.
- Ghi rõ failed run hoặc outlier.
- Chỉ multi-seed cho 1–2 candidate cuối, không lãng phí tài nguyên cho mọi experiment.

Output:

```text
reports/repeatability_report.md
reports/final_candidate_multi_seed.csv
```

---

# 9. Phân bổ theo roadmap

## Day 3

Chỉ cần:

- GPU/environment verification.
- COCO8 smoke test 1 epoch.
- Chọn public UAV dataset.
- Tạo experiment plan và dataset manifest.
- Bắt đầu audit hoặc baseline nếu dữ liệu đã sẵn sàng.

Không ép Day 3 hoàn thành toàn bộ tám nhóm tối ưu.

## Day 4–5

- Baseline evaluation.
- Resolution ablation.
- Failure categorization.
- Before/after dataset audit.
- Experiment registry.

## Day 6–8

- Custom data collection.
- Annotation review.
- Hard-negative/hard-example pool.
- Public-to-custom fine-tuning.
- Before/after optimization report.

## Day 10–14

- Tracking metrics.
- Runtime matrix.
- ONNX/OpenVINO.
- Quantization nếu phù hợp.
- Pareto model selection.

## Day 15–30

- End-to-end benchmark.
- Multi-seed validation cho final candidate.
- Model card.
- Dataset card.
- Limitations.
- Final evidence package.

---

# 10. Agent Rules bổ sung

1. Không gọi một model là “optimized” nếu chưa có baseline comparison.
2. Không thay đổi nhiều biến trong một ablation mà không giải thích.
3. Không sử dụng test set để chọn augmentation, tune threshold hoặc fine-tune.
4. Không đưa failure samples trực tiếp từ held-out test vào train.
5. Không chạy INT8 nếu chưa có calibration set đại diện.
6. Không chọn model chỉ dựa trên mAP.
7. Không ghi metric ước đoán vào daily log.
8. Không ghi thời gian hoặc latency nếu chưa dùng công cụ đo.
9. Không coi một seed duy nhất là bằng chứng final.
10. Không ép toàn bộ optimization workflow vào một ngày; phân bổ theo dependency và quality gate.
