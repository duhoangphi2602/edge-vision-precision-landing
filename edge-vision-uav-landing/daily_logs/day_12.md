# Day 12: Robustness v0.1 and constrained-runtime baseline

## Mission served
P1-A, P1-B, ML

## Done
- **Machine A:** Cập nhật Hybrid SITL với fault injection (network delay, packet drop, CPU throttle). Chạy các kịch bản nhiễu để verify failsafe reaction.
- **Machine B:** Export YOLO26n và YOLO26s sang định dạng ONNX. Chạy benchmark đo tốc độ inference latency (P50/P95). Tổng hợp báo cáo Robustness.

## Evidence
- Files: `robustness_sitl_scenarios_v0.1.yaml`, `runtime_benchmark.csv`, `robustness_v0_1.md`
- Runs: `runs/day12/*.csv`
- Models: `models/optimized/yolo26n_640.onnx`, `edge-ai-training/models/optimized/yolo26s_640.onnx`

## Metrics
- P50 Latency (ONNX): 11.12 ms (MEASURED)
- P95 Latency (ONNX): 14.25 ms (MEASURED)
- Stale packet rejection rate (tại 100ms delay): 100% successful failsafe triggering (MEASURED)

## Problems
- (Clear) Không có sự cố crash hay model suy giảm đáng kể. Cả Nano và Small đều hoạt động <15ms P95 trên máy tính.

## Decision
- PASS. Chốt sử dụng YOLO26s ONNX.

## Tomorrow
- Day 13: Vehicle tracking mode, ONNX integration, and challenge evaluation.
