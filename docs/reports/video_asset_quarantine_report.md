# Video Asset Quarantine Report
**Date**: 2026-07-18

## 1. Overview
This report documents the execution of VID_013 (Controlled Quarantine). It confirms that deprecated legacy assets have been safely moved out of the active workspace and into quarantine, and that the pipeline remains fully functional.

## 2. Scan Results (Pre & Post Quarantine)
A full workspace `grep` scan was performed for `test_landing.mp4`, `test_traffic.mp4`, `car-detection.mp4`, and `car_detection.mp4`.
- **Pre-Quarantine**: 23 references were found, but **100% of them were historical** (markdown logs, reports, and reviews). No active runtime dependencies (Python scripts, tests, yaml configs) referenced these legacy files.
- **Post-Quarantine**: The codebase remains free of active dependencies on these names.

## 3. Quarantined Assets (Q_001)
The following assets were moved to `assets/videos/quarantine/Q_001/`:
- `edge-vision-uav-landing/videos/test_landing.mp4` (SHA-256 verified)
- `edge-vision-uav-landing/data/test_traffic.mp4` (SHA-256 verified)
- `videos/car-detection.mp4` (SHA-256 verified)

**No assets were permanently deleted.**

## 4. Full-Duration Regression Results
After moving the assets, the pipeline was run for its full duration (overriding `--duration-sec`).
- **P1-A ArUco Replay**: `PASS`. Tracked ID 0 correctly for the full synthetic generation.
- **P1-B Vehicle Tracking**: `PASS`. Processed the entire 30s `car_detection_base.mp4` sequence without crash.
- **P2-A Stabilization Generation**: `PASS`. Generated full jitter motion successfully.
- **P2-A Stabilization Filter**: `PASS`. Processed full sequence via Lucas-Kanade optic flow.

## 5. Verification Checks
- **Codec Verification**: `PASS` via OpenCV/imageio. Note: Strict `ffprobe` verification is **blocked** as `ffprobe` is not installed on the host OS. A fallback string check using `imageio_ffmpeg` stdout confirmed `h264` and `yuv420p` presence.
- **Run Manager Architecture**: `PASS`. `scripts/utils/run_manager.py` was successfully imported via path-independent `sys.path.append(str(Path(__file__).parent.parent.parent))` and works uniformly across all projects.

## 6. Exceptions
- No assets were marked as "Unknown provenance".
- No historical evidence (like day logs or old markdown files) was deleted.

## 7. Quarantine Retention Decisions
- **test_landing.mp4**: `Retain as historical fixture`. It may have value as a legacy fault fixture.
- **test_traffic.mp4**: `Safe for permanent deletion`. It is an exact duplicate of `car-detection.mp4` and no longer used.
- **car-detection.mp4**: `Safe for permanent deletion`. Replaced by `car_detection_base.mp4`. Since it is only 4.7MB, it could be retained until archive, but it serves no purpose.

## 8. Status
VID_013 is **COMPLETED**.
**VID_014 (Permanent Cleanup)** is ready for user approval, but has NOT been executed yet.

## Post-Quarantine Cleanup (Phase 3)
On 2026-07-18, a permanent cleanup (VID_014) was executed:
- **test_traffic.mp4** and **car-detection.mp4** were confirmed as pure duplicates of the canonical `car_detection_base_01` and were permanently deleted (reclaiming ~5.6 MB).
- **test_landing.mp4** was marked as `retained` inside the quarantine directory to serve as a legacy fault fixture.
- See `video_asset_permanent_cleanup_report.md` for full details.

