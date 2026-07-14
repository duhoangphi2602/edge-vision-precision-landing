# Next Action Plan

## 1. Current State
Day 1 (Initialization) and Day 2 (ArUco Detection + Video Reader) are complete. The perception pipeline is generating pixel errors real-time and YOLO environment on GPU is validated. 

## 2. Current ROADMAP Day: DAY_03

## 3. Immediate Next Step
Start DAY_03 implementation: Camera calibration and pose estimation. 
Convert the 2D pixel errors into 3D metric distances (meters).

## 4. Machine A Tasks
- Implement `src/estimation/camera_calibration.py`.
- Implement `src/estimation/pose_estimator.py`.
- Create `configs/camera.yaml`.
- Generate `reports/calibration_report.md`.

## 5. Machine B Tasks
- Train YOLO model v0.1 on actual UAV/landing dataset.
- Save best model and generate initial training report (results.csv, confusion matrix).

## 6. Shared Tasks
- Commit changes for Day 3.

## 7. Commands User Should Run Manually
(Check environment)
```bash
lsb_release -a
uname -a
python3 --version
git status
```

## 8. Files User Should Create/Edit Manually
- Provide camera calibration image samples or choose synthetic calibration approach.

## 9. Verification
- `pose_estimator.py` should run and output 3D translation vector (tvec).
- `reports/calibration_report.md` should contain camera intrinsic parameters.

## 10. Risks
- Calibration requires good sample images. If real images are bad, pose estimation will be inaccurate. Synthetic calibration fallback might be needed.

## 11. Stop Conditions
- Stop once Day 3 execution plan is approved.

## 12. Review Checklist Before Continuing
- [ ] Read DAY_03 Execution Plan.
- [ ] Confirm calibration approach (Option A: Real images, Option B: Synthetic).
