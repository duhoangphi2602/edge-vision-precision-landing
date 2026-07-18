# Video Asset Inventory Report

## 1. Inventory Summary
This report lists all video files (mp4/avi) currently found in the project and traces every reference to them in the codebase and documentation. 
**Date**: 2026-07-18

## 2. Found Video Assets

### 2.1 Base/Input Videos
- `videos/car-detection.mp4`
  - **Status:** Needs classification. (Will map to P1-B and P2-A)
- `edge-vision-uav-landing/data/test_traffic.mp4`
  - **Status:** Needs classification. Duplicate of car-detection.
- `edge-vision-uav-landing/videos/test_landing.mp4`
  - **Status:** `misaligned_input` (Legacy noise fixture, invalid for P1-A ArUco landing).

### 2.2 Generated Output Videos
- `gimbal-video-stabilization-analyzer/data/input/shaky_input.mp4`
- `gimbal-video-stabilization-analyzer/data/input/shaky_input_viewable.mp4`
- `edge-vision-uav-landing/runs/day13/tracking_demo.mp4`
- `edge-vision-uav-landing/runs/gate2/tracking_demo.mp4`

## 3. Reference Traces

### `car-detection.mp4`
- `gimbal-video-stabilization-analyzer/scripts/generate_shaky_sample.py`
- `docs/plans/day_21_checklist.md`

### `test_traffic.mp4`
- `docs/plans/day_13_checklist.md`

### `test_landing.mp4`
- `edge-vision-uav-landing/scripts/run_replay_test.py`
- `docs/plans/day_05_checklist.md`
- `docs/plans/day_21_checklist.md`

### Other Mentions (Checklists/Manifests)
- `edge-ai-training/manifests/tracking_eval_sequences.yaml` (Points to `seq_*.mp4` which don't exist yet).
- `edge-ai-training/scripts/evaluate_challenge_sequences.py`
- `edge-vision-uav-landing/src/perception/vehicle_tracking_demo.py` (`tracking_demo.mp4`)
- `gimbal-video-stabilization-analyzer/scripts/stabilize_video.py` (`shaky_input.mp4`, `stabilized.mp4`, `side_by_side.mp4`)
- `ROADMAP.md` (Points to `videos/inputs/aruco_landing_replay.mp4`, `uav_vehicle_tracking_01.mp4`, `uav_shaky_vehicle_01.mp4`).

## 4. Conclusion
We have identified all video assets and their references. 
- `test_landing.mp4` is confirmed as a `misaligned_input` and `legacy_fault_fixture` for P1-A.
- `car-detection.mp4` and `test_traffic.mp4` are identical and need to be unified for P1-B and P2-A.
