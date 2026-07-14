# DAY_03 Execution Plan

## 1. Goal of DAY_03
- Estimate 3D pose of the ArUco marker using camera intrinsic parameters.
- Transform pixel error (2D) to metric error (3D coordinates in meters).
- Train first viable YOLO tracking model (v0.1) on PC GPU.

## 2. What Previous Days Already Completed
- ArUco marker detection pipeline.
- 2D pixel error calculation.
- Overlay drawing and metric logging to CSV.
- ML workspace initialization and PyTorch validation.

## 3. What Must Be Finished Before Starting DAY_03
- Code from Day 1 and 2 must be merged/committed. (Done)

## 4. Scope
- Camera parameter estimation (Calibration).
- Pose estimation math (solvePnP).
- Update YOLO training pipeline to train on an actual dataset (v0.1).

## 5. Out of Scope
- PID control.
- Drone integration (PX4/SITL).
- Gimbal project.

## 6. Machine A Tasks
- Create `src/estimation/camera_calibration.py` (Script to calculate or load camera matrix).
- Create `src/estimation/pose_estimator.py` (Class to run `cv2.solvePnP` on ArUco corners).
- Create `configs/camera.yaml` (Stores intrinsics).
- Write `reports/calibration_report.md`.

## 7. Machine B Tasks
- Prepare target tracking dataset (e.g., UAV tracking or landing pad).
- Train YOLO baseline v0.1: `yolo detect train ... name=yolo_baseline_v0_1`
- Save `best.pt` and `results.csv`.

## 8. Shared Tasks
- Ensure coordinate systems (Camera vs Marker frames) are documented properly.

## 9. Files/Folders Expected to Change After User Approval
- `edge-vision-uav-landing/configs/camera.yaml`
- `edge-vision-uav-landing/src/estimation/__init__.py`
- `edge-vision-uav-landing/src/estimation/camera_calibration.py`
- `edge-vision-uav-landing/src/estimation/pose_estimator.py`
- `edge-vision-uav-landing/reports/calibration_report.md`
- `edge-ai-training/experiments/` (Logs and models for v0.1)
- `edge-vision-uav-landing/daily_logs/day_03.md` (At the end of day)

## 10. Commands User Should Run Manually
(On Laptop)
```bash
git status
git branch
git checkout -b day03/pose-estimation
# Run calibration script (will be provided)
python scripts/calibrate_camera.py
```
(On PC GPU)
```bash
# Run training script
yolo detect train data=uav_dataset.yaml model=yolo11n.pt epochs=50 project=experiments name=v0.1
```

## 11. Verification Commands
```bash
# Verify pose estimation output
python src/estimation/pose_estimator.py
```

## 12. Risks
- OpenCV's `solvePnP` can suffer from ambiguity if the marker is very small or far away, leading to flip errors.

## 13. Acceptance Criteria
- 3D pose (tvec, rvec) is successfully printed or logged.
- Camera intrinsics are saved to `configs/camera.yaml`.
- YOLO v0.1 model weights are produced.

## 14. Stop Conditions
- Stop and wait for user approval before modifying any code.
