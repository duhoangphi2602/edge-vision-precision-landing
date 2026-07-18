# Revised Implementation Plan: Video Asset Standardization

## Căn cứ thực thi
- **Current Day:** Day 21 (Dựa theo `docs/plans/day_21_checklist.md`).
- **Nhiệm vụ:** Chuẩn hóa toàn bộ video theo từng Mission.

## VID_001 — Inventory toàn bộ video và references
- **Mission ID:** `INFRA`
- **Mục tiêu:** Tìm tất cả file video hiện tại và code reference, ghi nhận `misaligned_input`.
- **Cách triển khai:** Quét `.mp4` và tạo báo cáo `docs/reports/video_asset_inventory.md`.

## VID_002 — Phân loại asset theo mission
- **Mission ID:** `INFRA`
- **Mục tiêu:** Map asset với P1-A, P1-B, P2-A. Xác định `test_landing.mp4` là sai mission.

## VID_003 — Tạo canonical directory structure
- **Mission ID:** `INFRA`
- **Mục tiêu:** Tạo cây thư mục `assets/videos/base/`, `assets/videos/generated/`, `assets/videos/quarantine/`, `assets/videos/manifests/`.

## VID_004 — Tạo video manifest và checksum contract
- **Mission ID:** `INFRA`
- **Mục tiêu:** Khởi tạo `VIDEO_ASSET_MANIFEST.yaml` (Hash SHA-256). 
- **Đặc biệt (P1-A):** Viết script sinh synthetic ArUco ID 0 landing video do workspace chưa có asset hợp lệ, ghi nhận generation config + seed.

## VID_005 — Thiết kế video conversion CLI
- **Mission ID:** `INFRA`
- **Mục tiêu:** Viết `tools/video/create_viewable_copy.py` với argparse. Hỗ trợ `--export-viewable`.

## VID_010 — Thêm run directory và overwrite protection
- **Mission ID:** `INFRA`
- **Mục tiêu:** Thiết lập thư mục `runs/<MISSION_ID>/<RUN_ID>/` chống ghi đè cho các script sinh data.

## VID_009 — Thêm duration/max-frames và export-viewable flags
- **Mission ID:** `INFRA`
- **Mục tiêu:** Cập nhật script nhận argparse (`--max-frames`, `--duration-sec`, `--process-full-video`).

## VID_011 — Thêm fault config, seed và resolved config
- **Mission ID:** `INFRA`
- **Mục tiêu:** Tạo YAML config tại `configs/faults/` phân tách rõ lỗi P1-A, P1-B, P2-A.

## VID_006 — Refactor P1-A replay input
- **Mission ID:** `P1-A`
- **Mục tiêu:** Sửa `run_replay_test.py` lấy video ArUco (synthetic).

## VID_007 — Refactor P1-B tracking input
- **Mission ID:** `P1-B`
- **Mục tiêu:** Sửa `vehicle_tracking_demo.py` đọc từ canonical base (car-detection), output runs/.

## VID_008 — Refactor P2-A stabilization input
- **Mission ID:** `P2-A`
- **Mục tiêu:** Sửa `generate_shaky_sample.py` & `stabilize_video.py` đọc canonical base.

## VID_012 — Bổ sung codec/functional/regression verification
- **Mission ID:** `INFRA`
- **Mục tiêu:** Dùng `ffprobe` và test tự động. Lập `docs/reports/video_asset_regression_report.md` và `docs/reports/video_asset_migration_report.md`.

## VID_013 & VID_014 — Deprecate và Cleanup (ĐANG BỊ KHÓA)
- **Tình trạng:** Chờ phê duyệt của user. Không được thực thi `rm` hay di chuyển tự động.
