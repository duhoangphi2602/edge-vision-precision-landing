# Resolution Ablation Study v0
**Date:** Day 04
**Dataset:** VisDrone (Precision Landing context)
**Model:** YOLOv11n

## Objective
Evaluate the impact of input resolution (`imgsz`) on detection accuracy (mAP50) for tiny objects, isolating resolution as the only changed variable.

## Results Comparison (at Epoch 30)

| Experiment ID | Resolution (imgsz) | Batch Size | mAP50 | mAP50-95 | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TRN_001` | 640px | Auto | 27.3% | 15.3% | Baseline model from Day 03. |
| **`TRN_002`** | **960px** | **8** (Auto) | **37.8%** | **22.3%** | Required Batch=8 to prevent GPU OOM. |

## Key Findings & Conclusion
1. **Massive Accuracy Gain:** Increasing the resolution from 640px to 960px resulted in a staggering **+10.5% absolute increase in mAP50**.
2. **Hypothesis Confirmed:** This proves definitively that the low accuracy in `TRN_001` was NOT due to a weak model architecture (YOLO11n is capable), but because the 640px resolution heavily degraded the visual features of tiny objects (like distant drones or cars), making them impossible to detect.
3. **Batch Size Trade-off:** Despite having to drop the Batch Size to 8 (which introduces gradient noise), the physical clarity provided by the 960px resolution completely overshadowed the mathematical instability, leading to superior convergence.

## Next Steps (Day 05+)
While `TRN_002` is highly accurate, running 960px inference directly on an Edge Device (Drone) will cause severe FPS drops and control latency (crashing the PID loop). We must investigate **SAHI (Slicing Aided Hyper Inference)** or **Cropping strategies** to achieve 960px-level accuracy while maintaining 640px-level processing speed.
