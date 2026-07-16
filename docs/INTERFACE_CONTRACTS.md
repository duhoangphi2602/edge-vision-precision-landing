# Interface Contracts

## Observation Schema v1 (Perception to Control)
**Protocol:** UDP
**Format:** JSON (string payload)

```json
{
  "schema_version": "1.0",
  "mission_id": "P1_A_FIXED_ARUCO_LANDING",
  "timestamp_capture_ns": 1680000000000000000,
  "timestamp_publish_ns": 1680000000050000000,
  "sequence_id": 1234,
  "frame_id": 1234,
  "source_type": "gazebo",
  "target_found": true,
  "marker_dictionary": "DICT_4X4_50",
  "marker_id": 0,
  "center_px": {"x": 320.0, "y": 240.0},
  "error_px": {"x": 0.0, "y": 0.0},
  "normalized_error": {"x": 0.0, "y": 0.0},
  "pose_valid": true,
  "translation_camera_m": {"x": 0.0, "y": 0.0, "z": 5.0},
  "rotation_rvec": [0.0, 0.0, 0.0],
  "detection_latency_ms": 15.5
}
```

## Control Rules
- Control node MUST reject malformed packets.
- Control node MUST reject stale packets (timeout configurable, default 200ms).
- Control node MUST handle out-of-order packets (drop if sequence_id < last_processed).
