# Real-world Dataset Upgrade Plan Review

## Executive Verdict
`APPROVE_WITH_REQUIRED_FIXES`

## Điểm đúng
- Nhận thức được nhu cầu chuyển từ dữ liệu synthetic sang real-world cho tracking và stabilization.
- Tách biệt rõ ràng 2 luồng: P1-B (Tracking) và P1-A (ArUco).
- Hiểu được kỹ thuật Metamorphic (Bơm lỗi trên video gốc).

## Điểm sai
- Xóa toàn bộ dữ liệu synthetic. (Phải giữ lại làm `deterministic_regression_fixture`).
- Gán cho 1 sequence duy nhất là "Full benchmark". (1 sequence chỉ là `SMOKE_VALIDATED`, cần `FULL_MULTI_SEQUENCE_BENCHMARK_PENDING`).
- Đánh đồng pseudo-label do OpenCV sinh ra là "absolute ground truth" cho bài toán ArUco. (Phải gọi là `auto-generated candidate annotation`).
- Sửa raw data thay vì tạo pipeline xử lý độc lập.

## Điểm còn thiếu
- Target-selection policy chưa tường minh trong tài liệu.
- Phân biệt giữa VisDrone-MOT (có persistent target_id) và VisDrone-VID/DET.
- Tách biệt rạch ròi giữa Media Faults (encode vào video) và Runtime Faults (thay đổi timing lúc replay).
- Biến đổi ground truth sau khi qua Stabilization (Warp/Crop transform).

## Roadmap impact
- Gate 3 (Day 21): Tiếp tục bằng test fixtures / synthetic. Real-world evidence chuyển thành pending (không block toàn bộ Gate).
- Day 22 (Robustness): Bổ sung thêm Derived faults trên real corpus, không chặn luồng chạy test bằng dữ liệu synthetic.

## Required fixes
- Đổi vai trò synthetic sang `deterministic_regression_fixture`.
- Cấu trúc thư mục dataset 4 tầng (raw, interim, processed, manifests).
- Parser phải giữ `target_id`, `class`, `occlusion`, `truncation`.
- Tách riêng script tạo `Media faults` và `Runtime faults`.
- Viết import command hỗ trợ `--dry-run`.

## Scope được phép triển khai
Triển khai toàn bộ Parser, Target Selector, Fault Injectors, Test Fixtures, và Manifest validation. Chỉ giữ trạng thái `BLOCKED_ON_EXTERNAL_DATA` đối với các khâu cần trực tiếp file video thực.

## Blockers
- KHÔNG CÓ BLOCKER NÀO CẢN TRỞ VIỆC VIẾT PIPELINE CODE.
- Blocker duy nhất là "Manual download required" đối với bộ VisDrone-MOT thật.

## Final recommendation
Triển khai ngay các module độc lập. Xây dựng tài liệu hướng dẫn manual import cho System Engineer.
