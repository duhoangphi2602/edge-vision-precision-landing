# Video Asset Codec Verification Report

**Status**: PASS
**Date**: 2026-07-18

## 1. Environment Discovery
Native `ffprobe` and `ffmpeg` were not available in the agent's environment PATH, despite being installed manually on the host. 
We successfully loaded the bundled FFmpeg binary from `imageio_ffmpeg`:
`ffmpeg_exe`: `/home/hoangphi/Projects/edge-vision-precision-landing/.venv/lib/python3.14/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2`

## 2. Codec Verification Results (Agent-executed codec verification)

| Mission | Run ID | File Path | Codec | Pix Fmt | Res | FPS | Dur | Expected | Diff | Decode | PASS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1-A | 20260718_114145 | runs/P1-A/20260718_114145/output_raw_viewable.mp4 | h264 | yuv420p | 640x480 | 30 | 30.00 | 30.00 | 0.0s | OK | **PASS** |
| P1-B | 20260718_113524 | runs/P1-B/20260718_113524/output_raw_viewable.mp4 | h264 | yuv420p | 768x432 | 12.5 | 30.16 | 30.16 | 0.0s | OK | **PASS** |
| P2-A (SBS) | 20260718_113318 | runs/P2-A/20260718_113318/side_by_side_raw_viewable.mp4 | h264 | yuv420p | 1536x432 | 12.5 | 30.08 | 30.16 | 0.08s| OK | **PASS** |
| P2-A (Stab) | 20260718_113318 | runs/P2-A/20260718_113318/stabilized_raw_viewable.mp4 | h264 | yuv420p | 768x432 | 12.5 | 30.08 | 30.16 | 0.08s| OK | **PASS** |

*Note: FPS and duration tolerance requirements were met. An initial issue in P1-B outputting 12 fps instead of 12.5 fps was fixed in `vehicle_tracking_demo.py` prior to the final PASS.*

### Raw Codec Evidence
Stored in `docs/reports/codec_probe/`:
- `*_metadata.log`: Contains output of `ffmpeg -hide_banner -i <path>`
- `*_decode_errors.log`: Contains output of `ffmpeg -v error -i <path> -f null -`
- `*_sha256.txt`: Checksum of the video

## 3. Conclusion
All criteria for `h264`, `yuv420p`, duration, resolution, and error-free decoding were met.
**VID_014 is UNBLOCKED.**
