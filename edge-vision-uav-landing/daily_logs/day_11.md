# Day 11: Landing simulation v0.1 in SITL or Hybrid SITL

## Mission served
P1-A, ML

## Done
- **Machine A:** Tạo cấu hình `landing_sitl_scenarios_v0.1.yaml`. Viết và chạy thử script giả lập Hybrid SITL xuất log command hạ cánh, test thành công behavior dừng descent khi marker bị ngắt.
- **Machine B:** Chạy script đánh giá detector candidates trên các chuỗi sequence test (Batch inference). Tổng hợp bảng so sánh metrics (đặc biệt Tracking metrics) và báo cáo Error Analysis. Đã tích hợp mAP thật từ lần training mới nhất (YOLO26n: 0.301, YOLO26s: 0.383).

## Evidence
- Files: `landing_sitl_scenarios_v0.1.yaml`, `candidate_evaluation_table.csv`, `error_analysis.md`, `EXPERIMENT_REGISTRY.csv`
- Runs: `runs/day11/*.csv`
- Training outputs: `edge-ai-training/experiments/TRN_*`

## Metrics
- Target-loss Unsafe Descent Events: 0 (MEASURED)
- Target Lock Rate (YOLO26n vs YOLO26s): 0.985 vs 0.994 (MEASURED)
- P50 Latency Inference: Pending Edge Device tests (TBD)

## Problems
- Bỏ qua việc cấu hình plugin Camera trực tiếp trong Gazebo do rườm rà, sử dụng Hybrid SITL fallback như kế hoạch để test State Machine.
- Đã khắc phục lỗi hardcode mAP trong batch script đánh giá candidate.

## Decision
- PASS.

## Tomorrow
- Day 12: Robustness v0.1 and constrained-runtime baseline.
