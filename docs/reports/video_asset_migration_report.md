# Video Asset Migration Report
**Date**: 2026-07-18

## 1. Migration Summary
This report summarizes the migration of video assets in Phase 2 of the standardization process.

## 2. P1-A ArUco Landing Replay
- **Original Source**: `edge-vision-uav-landing/videos/test_landing.mp4` (Invalid noise)
- **New Canonical**: `assets/videos/base/p1a_aruco_landing/aruco_id0_landing_v1.mp4`
- **Migration Status**: Completed. Scripts fully switched over.

## 3. P1-B Vehicle Tracking
- **Original Source**: `videos/car-detection.mp4` / `test_traffic.mp4`
- **New Canonical**: `assets/videos/base/p1b_vehicle_tracking/car_detection_base.mp4`
- **Migration Status**: Completed. YOLO tracking uses canonical input.

## 4. P2-A Video Stabilization
- **Original Source**: Hardcoded `../../videos/car-detection.mp4`
- **New Canonical**: Reads from `--input` (defaults to canonical `car_detection_base.mp4`)
- **Migration Status**: Completed.

## 5. Directory Structure Standardized
- Deprecated hardcoded output paths.
- All runs now properly directed to `runs/<MISSION_ID>/<RUN_ID>/` through `run_manager.py`.

## 6. Deprecation Candidates (Pending VID_013)
The following old files are fully detached from the pipeline and are ready to be quarantined or deleted:
- `videos/car-detection.mp4`
- `edge-vision-uav-landing/data/test_traffic.mp4`
- `edge-vision-uav-landing/videos/test_landing.mp4`
- `gimbal-video-stabilization-analyzer/data/input/*`
