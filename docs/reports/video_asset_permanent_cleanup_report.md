# Video Asset Permanent Cleanup Report

**Status**: PASS
**Date**: 2026-07-18

## 1. Environment and Codec Verification
- `ffprobe` native was missing due to sandbox limitations. We utilized `imageio_ffmpeg.get_ffmpeg_exe()` to inspect and verify the files natively via FFmpeg (`h264`, `yuv420p`, zero decode errors).
- All criteria were successfully met across P1-A, P1-B, and P2-A.
- A bug in P1-B outputting `12 fps` (due to `int()` truncation) was identified and fixed in `vehicle_tracking_demo.py` prior to cleanup execution, ensuring the output perfectly matches the expected `12.5 fps`.
- A bug in P1-A causing short duration output (14.43s instead of 30.0s) when frames were dropped due to `marker_loss` fault injection was fixed in `run_replay_test.py` by writing blank (black) frames to maintain the original duration.

## 2. Permanent Deletion Execution
Two exact duplicates of `car_detection_base_01` were identified and permanently deleted from `assets/videos/quarantine/Q_001/`:

| Deleted File | Reason | Size Freed | Replacement |
|---|---|---|---|
| `edge-vision-uav-landing/data/test_traffic.mp4` | Duplicate of canonical asset | 2.81 MB | `car_detection_base_01` |
| `videos/car-detection.mp4` | Duplicate of canonical asset | 2.81 MB | `car_detection_base_01` |

**Total Space Freed:** ~5.62 MB

## 3. Retained Assets
One legacy asset was retained as a specialized historical fixture rather than being deleted:
- `edge-vision-uav-landing/videos/test_landing.mp4`
- Retained within quarantine (`Q_001`) with role `legacy_fault_fixture` for invalid input testing. It is strictly explicitly excluded from canonical use.

## 4. Manifest Updates
- `VIDEO_ASSET_MANIFEST.yaml` and `QUARANTINE_MANIFEST.yaml` were both updated to contain tombstone records for the deleted items (`status: permanently_deleted`).
- The retained item was given `status: retained` and clear role constraints.

## 5. Post-Cleanup Regression
After deletions and manifest updates, we verified the overall integrity using `verify_video_assets.py`:
- `verify_video_assets.py` manifest parser was updated to explicitly ignore missing files that bear statuses: `quarantined`, `retained`, and `permanently_deleted`.
- Manifest validation: **PASS**
- P1-A Pipeline Smoke Test: **PASS**
- P1-B Pipeline Smoke Test: **PASS**
- P2-A Stabilization Smoke Test: **PASS**

## 6. Final Active Reference Scan
- Active runtime references to deleted files: **0**
- Active config references to deleted files: **0**
- Test dependencies on deleted files: **0**

## 7. Conclusion
**VID_014 is officially PASS.** The codebase is successfully migrated to the new standardized video assets, duplicates have been expunged, and historical references are cleanly cataloged via tombstones.

## 8. Source Change Documentation

### `edge-vision-uav-landing/src/perception/vehicle_tracking_demo.py`
- **Issue**: Lỗi FPS truncation. Khi export output video (P1-B tracking), dòng `out = cv2.VideoWriter(out_video, fourcc, int(fps), (width, height))` dùng `int(fps)`. Do input fps là 12.5, giá trị này bị cắt cụt xuống 12, khiến duration của file viewable sai lệch so với nguồn (31.42s thay vì 30.16s).
- **Cách sửa**: Bỏ `int()` để giữ nguyên giá trị float: `out = cv2.VideoWriter(out_video, fourcc, fps, (width, height))`.
- **Test trước/sau**: Trước khi sửa, output là 12 fps và duration 31.42s (FAIL codec gate do vượt tolerance). Sau khi sửa, output là 12.5 fps và duration 30.16s (PASS codec gate).

### `tests/verify_video_assets.py`
- **Issue**: Script regression test hiện tại chỉ bỏ qua các asset có status `deprecated_candidate`. Khi manifest được cập nhật với trạng thái `retained` (file legacy_test_landing không nằm ở đường dẫn cũ) và `permanently_deleted`, script báo FAIL do không tìm thấy file tại `legacy_path`.
- **Cách sửa**: Sửa điều kiện check để bỏ qua: `if asset['status'] not in ['deprecated_candidate', 'quarantined', 'permanently_deleted', 'retained']:`.
- **Lý do bỏ qua**: Các file bị xóa hoặc bị cách ly (quarantine/retained) không còn tồn tại trên original path nữa, nên validator không được phép kiểm tra sự tồn tại trên đường dẫn cũ, chỉ xác minh metadata là đủ.
- **Xác nhận an toàn**: Verifier hoàn toàn không bỏ qua nếu canonical asset bị thiếu (canonical có status `active`). Bất kỳ canonical asset nào bị mất vẫn sẽ fail test.

