# Day 12: Robustness v0.1 & Latency Report

## 1. Latency Benchmark (ONNX vs PyTorch)
| Model   | Format   |   P50_Latency_ms |   P95_Latency_ms |
|:--------|:---------|-----------------:|-----------------:|
| YOLO26n | PyTorch  |            12.75 |            17.05 |
| YOLO26n | ONNX     |             8.9  |            14.08 |
| YOLO26s | PyTorch  |            12.03 |            20.33 |
| YOLO26s | ONNX     |            11.12 |            14.25 |

**Conclusion:** YOLO26n ONNX đạt yêu cầu realtime với P50 = 8.9ms (<100ms).

## 2. Controller Failsafe Evaluation (Hybrid SITL)
### Scenario: fault_cpu_throttle_10hz
- Total steps simulated: 100
- Final Altitude: 1.55m
- Failsafe Triggered (HOLD/SEARCH state): Yes

### Scenario: fault_frame_drop_50
- Total steps simulated: 300
- Final Altitude: 5.0m
- Failsafe Triggered (HOLD/SEARCH state): Yes

### Scenario: fault_delay_100ms
- Total steps simulated: 300
- Final Altitude: 1.3333m
- Failsafe Triggered (HOLD/SEARCH state): Yes

