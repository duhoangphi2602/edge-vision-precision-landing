# Video Asset Regression Report
**Date**: 2026-07-18

## 1. Overview
This report summarizes the regression testing for Phase 2 of the video asset standardization (Tasks VID_006 through VID_012).

## 2. P1-A ArUco Landing Replay (VID_006)
- **Script**: `edge-vision-uav-landing/scripts/run_replay_test.py`
- **Input Asset**: `assets/videos/base/p1a_aruco_landing/aruco_id0_landing_v1.mp4`
- **Verification**: 
  - [x] Detected ArUco ID 0 successfully.
  - [x] Wrong marker ID rejection (simulated).
  - [x] Smoke test ran via `--duration-sec 1`.
  - [x] Metrics logged to `metrics.csv`.
- **Result**: PASS

## 3. P1-B Vehicle Tracking (VID_007)
- **Script**: `edge-vision-uav-landing/src/perception/vehicle_tracking_demo.py`
- **Input Asset**: `assets/videos/base/p1b_vehicle_tracking/car_detection_base.mp4`
- **Verification**:
  - [x] YOLO tracking on `car` class.
  - [x] End-to-end and inference latency separated.
  - [x] Target state (SEARCH, LOCKED, LOST) correctly logged.
  - [x] Smoke test ran successfully.
- **Result**: PASS

## 4. P2-A Video Stabilization (VID_008)
- **Script**: `gimbal-video-stabilization-analyzer/scripts/generate_shaky_sample.py` & `stabilize_video.py`
- **Input Asset**: Derived from `car_detection_base.mp4`
- **Verification**:
  - [x] Shaky video generation is deterministic via seed.
  - [x] Transform metrics saved to CSV.
  - [x] Stabilization produces `raw` and `side_by_side` outputs.
- **Result**: PASS

## 5. CLI & Safety (VID_009, VID_010, VID_011)
- [x] All scripts use argparse and `run_manager.py`.
- [x] Output paths properly mapped to `runs/<MISSION_ID>/<RUN_ID>`.
- [x] Configurations properly loaded and merged.
- [x] Missing input properly handled with non-zero exit codes.

## 6. Conclusion
All scripts have been fully refactored and verified. No prior functionality was lost.
**Ready for VID_013** (Deprecation of old assets) pending user approval.
