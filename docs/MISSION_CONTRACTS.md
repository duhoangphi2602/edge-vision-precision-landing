# Mission Contracts (v1.0)

## 1. Perception Observation Schema (UDP)
Được gửi từ Perception Process sang Control Process.

```json
{
  "schema_version": "1.0",
  "mission_id": "P1_A_FIXED_ARUCO_LANDING",
  "timestamp_capture_ns": 1690000000000,
  "timestamp_publish_ns": 1690000005000,
  "sequence_id": 1,
  "frame_id": 100,
  "source_type": "replay",
  "target_found": true,
  "marker_dictionary": "DICT_4X4_50",
  "marker_id": 0,
  "center_px": {"x": 320.0, "y": 240.0},
  "error_px": {"x": 10.5, "y": -5.0},
  "normalized_error": {"x": 0.03, "y": -0.02},
  "pose_valid": true,
  "translation_camera_m": {"x": 0.1, "y": 0.0, "z": 2.5},
  "rotation_rvec": [0.01, 0.02, -0.01],
  "detection_latency_ms": 12.5
}