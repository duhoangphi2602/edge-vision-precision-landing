# Day 04: PID Visual Servoing & Resolution Ablation

## Done
- [x] Cài đặt PID với anti-windup (unwind), first-sample handling, reset function.
- [x] Hoàn thiện `control_metrics.py` đo overshoot/settling time.
- [x] Xuất `pid_simulation_summary.csv` cho 3 kịch bản offset.

## Metrics
- PID Settling Time: 2.05s - 4.05s (Rất nhanh, đạt chuẩn < 5.0s)
- PID Overshoot: 0.0% (Critically Damped tuyệt đối)

## Problems
- Auto-batch (`batch=-1`) làm nhiễu kết quả ablation giữa TRN_001 và TRN_002 do batch size tự động co giãn theo imgsz. Cần lưu ý trong so sánh.
