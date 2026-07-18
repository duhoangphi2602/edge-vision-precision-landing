# Real-world Dataset Upgrade Validation

## Verdict
`PARTIALLY_COMPLETE`

## Plan review status
`APPROVE_WITH_REQUIRED_FIXES`

## Pipeline implementation status
`PARTIALLY_COMPLETE` (Toàn bộ code xử lý, parser, target selection, và test fixtures đã được tạo, nhưng chưa chạy được với file thực tế).

## Official source access status
`MANUAL_DOWNLOAD_REQUIRED` (Bộ dữ liệu VisDrone-MOT yêu cầu đăng nhập và click tải tay từ Baidu Pan hoặc Google Drive chính thức).

## Manual download required
`YES` (Xem `docs/plans/manual_visdrone_import_instructions.md`).

## Fixture-based test status
`PIPELINE_VERIFIED_WITH_TEST_FIXTURE` (Các parser và selection logic được chạy trên dữ liệu mẫu thu nhỏ để kiểm thử correctness).

## Real-world smoke status
`BLOCKED_ON_EXTERNAL_DATA`

## Multi-sequence benchmark status
`NOT_STARTED`

## Media fault status
`IMPLEMENTED_BUT_NOT_VERIFIED` (Các script sinh blur/noise/brightness đã sẵn sàng).

## Runtime fault status
`IMPLEMENTED_BUT_NOT_VERIFIED` (Cơ chế drop frame, network jitter, IPC delay đã sẵn sàng).

## Annotation parser status
`VERIFIED` (Qua test fixture).

## Target-selection status
`VERIFIED` (Qua test fixture).

## Manifest validation status
`VERIFIED` (Schema và validation code đã được kiểm thử).

## Stabilized ground-truth status
`IMPLEMENTED_BUT_NOT_VERIFIED` (Thuật toán biến đổi bbox qua affine transform warp/crop đã được viết).

## ArUco annotation status
`REAL_WORLD_EVIDENCE_PENDING` (Sử dụng auto-generated candidate annotation, chờ file quay thật để review và biến thành human-verified).

## Gate 3 impact
Phần core C++ (PID, Failsafe, IPC, Stale-message) KHÔNG BỊ CHẶN.
Phần đánh giá Tracking Analytics bằng dữ liệu thật: Bổ sung thành Carry-over.

## Day 22 impact
Phần Robustness test bằng Deterministic Synthetic Fixture: Tiếp tục chạy bình thường.
Phần tạo Corpus lỗi trên video thật: Tạm chuyển thành Carry-over.

## Roadmap carry-over
- Real-world benchmark upgrade
- Multi-sequence evaluation
- Derived fault robustness corpus
- Transformed ground truth for stabilization
- Human-verified ArUco annotation

## Remaining blockers
- Kéo thả thủ công file `VisDrone-MOT` video và `txt` vào thư mục `raw/visdrone/`.
