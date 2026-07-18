# Video Asset Standardization Plan Review

## 1. Context
- **Current Day:** Day 21
- **Related Missions:** `P1-A`, `P1-B`, `P2-A`, `Infrastructure`

## 2. Verdict
**Needs revision**

## 3. Evaluation of Proposed Changes

| Change | Mission | Benefit | Risk | Required revision | Verdict |
| ------ | ------- | ------- | ---- | ----------------- | ------- |
| Dùng chung 1 base video (`car-detection.mp4`) | `INFRA` | Tiết kiệm dung lượng | Gây sai lệch bối cảnh bài toán | Phải dùng video riêng theo từng mission (P1-A, P1-B, P2-A) | Needs revision |
| Xóa trực tiếp `test_traffic.mp4` | `INFRA` | Dọn dẹp rác | Gây lỗi các module phụ thuộc | Phải scan, copy sang canonical path, update code và chạy regression trước khi xóa | Blocked by missing evidence |
| Tạo `scripts/utils/video_converter.py` | `INFRA` | Tái sử dụng code | Gây phụ thuộc chéo giữa các project | Phải thiết kế thành CLI độc lập tại `tools/video/create_viewable_copy.py` | Needs revision |
| Sửa `run_replay_test.py` (Day 5) | `P1-A` | Sinh lỗi thực tế | Dùng nhầm video car cho ArUco | Dùng video ArUco riêng, cấu hình fault bằng YAML có seed | Needs revision |
| Sửa `vehicle_tracking_demo.py` (Day 13/14) | `P1-B` | Chuẩn hóa video | Sai cấu trúc lưu trữ | Phải đọc từ `videos/base/p1b_...` và xuất ra thư mục `runs/<RUN_ID>/` | Needs revision |
| Bỏ giới hạn 200 frame ở Day 21 | `P2-A` | Phân tích toàn diện | Code chạy quá lâu khi debug | Thêm tham số CLI `--max-frames`, `--duration-sec` cho smoke test | Needs revision |

## 4. Các lỗi quan trọng nhất trong plan cũ
1. **Sai lệch Mission Alignment:** Gom chung mọi video test vào 1 file duy nhất (dùng video xe cho P1-A ArUco).
2. **Sai quy trình Cleanup:** Đề xuất xóa ngay file cũ mà không update reference và chạy regression test.
3. **Quản lý Output yếu kém:** Đề xuất ghi trực tiếp output đè lên project root thay vì tạo Run ID folder (`runs/<RUN_ID>/`).
4. **Thiếu tính linh hoạt:** Hardcode việc tạo file `_viewable.mp4` thay vì dùng các flag `--export-viewable`.
5. **Thiếu cơ chế tự động:** Không có Manifest quản lý cấu trúc file, không có checksum, validation chỉ dùng mắt người thay vì `ffprobe` và mã MD5.

## 5. Những phần được giữ nguyên
- Tầm nhìn chuẩn hóa cấu trúc dữ liệu video (Base vs Generated).
- Ý tưởng cung cấp video định dạng H.264 song song với MP4 Edge-AI format.
- Ý tưởng nâng cấp script để hỗ trợ xử lý toàn bộ thời lượng video.

## 6. Những phần bắt buộc sửa
- Bắt buộc lập `VIDEO_ASSET_MANIFEST.yaml` chứa thông tin checksum, FPS, codec, role.
- Phải chia `videos/base/` thành các nhánh mission riêng biệt.
- Converter phải là CLI `tools/...` độc lập với các flag tùy chỉnh mạnh mẽ.
- Bất kỳ quá trình processing nào cũng phải sinh ra `runs/<RUN_ID>/` folder.
- Fault injection phải được tách biệt theo từng mission và driven bởi YAML config + seed.

## 7. Revised Execution Order
1. VID_001 — Inventory toàn bộ video và references
2. VID_002 — Phân loại asset theo mission
3. VID_003 — Tạo canonical directory structure
4. VID_004 — Tạo video manifest và checksum contract
5. VID_005 — Thiết kế video conversion CLI
6. VID_006 — Refactor P1-A replay input
7. VID_007 — Refactor P1-B tracking input
8. VID_008 — Refactor P2-A stabilization input
9. VID_009 — Thêm duration/max-frames và export-viewable flags
10. VID_010 — Thêm run directory và overwrite protection
11. VID_011 — Thêm fault config, seed và resolved config
12. VID_012 — Bổ sung codec/functional/regression verification
13. VID_013 — Deprecate asset cũ
14. VID_014 — Cleanup asset cũ sau khi được người dùng xác nhận

## 8. Điều kiện cần đạt trước khi xóa/di chuyển video
1. Hoàn tất scan reference (VID_001).
2. Đã copy video sang canonical path, lập checksum trên YAML (VID_004).
3. Đã update toàn bộ reference sang path mới.
4. Chạy regression test thành công (VID_012).
5. Chứng minh không còn script/tài liệu nào gọi tới path cũ (VID_013).
6. Người dùng trực tiếp Review và xác nhận an toàn (VID_014).
