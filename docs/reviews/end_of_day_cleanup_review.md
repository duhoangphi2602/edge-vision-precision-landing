# Day 03 closeout / Day 04 readiness

## 1. Review Context

- Next scheduled ROADMAP day: DAY_04
- Day determination status: Ready for DAY_04 (Day 03 tasks are completed. Day 04 is the next scheduled day, not yet executed.)
- Workspace root: `/home/hoangphi/Projects/edge-vision-precision-landing`
- Review date/time: 2026-07-15
- Review mode: Review Mode

## 2. Sources Read
- `ROADMAP.md`
- `docs/plans/day_02_checklist.md`
- `docs/plans/day_03_checklist.md`
- `docs/plans/day_03_execution_plan.md`
- `edge-vision-uav-landing/daily_logs/day_03.md`
- `docs/reviews/current_project_progress_snapshot.md`
- `docs/reviews/roadmap_alignment_review.md`
- `edge-ai-training/experiments/EXPERIMENT_REGISTRY.csv`
- `edge-ai-training/reports/dataset_audit_visdrone_v1.md`
- `edge-ai-training/datasets/manifests/DATASET_SOURCES.md`
- `edge-ai-training/datasets/manifests/DATASET_MANIFEST.json`
- `edge-vision-uav-landing/reports/calibration_report.md`

## 3. Source-of-Truth and Patch Alignment
- Không phát hiện file patch (`ROADMAP_*_PATCH.md`) nào trong workspace. `ROADMAP.md` hiện tại là source-of-truth duy nhất.

## 4. Workspace Scan Summary
- Project 1 (`edge-vision-uav-landing`): Đã có cấu trúc `src/perception`, `src/estimation`, `configs`, `scripts`, `reports`.
- Project 2 (`gimbal-video-stabilization-analyzer`): Status: Not scheduled yet.
- Support Workspace (`edge-ai-training`): Đã có dataset manifests, experiments (`TRN_001`), reports.

## 5. Progress Summary

### Next Scheduled Day: DAY_04
Chưa có plan/checklist cho DAY_04 (Ready to plan).

### Previous 2 Days Reviewed
Day 02 và Day 03.

### Completed With Evidence
- Môi trường và cấu trúc thư mục.
- Camera calibration (synthetic): `camera_calibration.py`, `pose_estimator.py`, `calibration_report.md`.
- Dataset manifest & audit v1: `DATASET_SOURCES.md`, `DATASET_MANIFEST.json`, `dataset_audit_visdrone_v1.md`.
- SMOKE_coco8_yolo11n test: Được lưu trong `EXPERIMENT_REGISTRY.csv`.

### Completed But Evidence Incomplete
- UAV-Domain YOLO Baseline v0.1 (`TRN_001`): Checklist says completed, but evidence is incomplete. Thư mục `TRN_001_visdrone_yolo11n_640` có `best.pt`, `args.yaml`, `results.csv` nhưng thiếu `COMMAND.txt`, `NOTES.md` và failure cases theo yêu cầu của acceptance criteria Day 3.

### Pending Items
- Bổ sung evidence/artifact cho `TRN_001` (`COMMAND.txt`, `NOTES.md`).
- Task Day 4: PID visual servoing offline.

### Blocked / Needs Confirmation
- Không có.

## 6. Scheduled Deliverables and Quality Gate Check
**Day 3 Quality Gate:**
- [x] Pose functional test pass: Verified
- [x] Camera/pose report không đưa claim chưa được đo: Verified
- [x] CUDA/environment verification pass: Verified
- [x] COCO8 smoke test pass: Verified
- [x] Dataset source/license được ghi: Verified
- [x] Dataset audit artifact tồn tại: Verified (`dataset_audit_visdrone_v1.md`)
- [ ] Nếu EXP_001 đã chạy: tồn tại `best.pt`, `results.csv`, curves, notes: Partially verified. (Có `best.pt`, `results.csv`, `args.yaml` nhưng thiếu curves image, `COMMAND.txt`, `NOTES.md`, failure cases. Tuy nhiên, `results.csv` đủ chứng minh metric cơ bản).
- [x] Daily log phản ánh đúng kết quả thực tế: Verified.
- [ ] Git status không chứa dataset/checkpoint lớn ngoài ý muốn: Chưa đánh giá pass (Cần người dùng tự kiểm tra bằng Git status vì chưa có evidence local git snapshot).

## 7. Dataset and Split Integrity
- Dataset manifest: Verified (`DATASET_MANIFEST.json`, `DATASET_SOURCES.md`).
- Audit report: Present (`dataset_audit_visdrone_v1.md`).
- Split integrity: Chưa đánh giá pass (Chưa có bằng chứng sequence split cho custom dataset).

## 8. Experiment and Evidence Integrity
- `SMOKE_coco8_yolo11n`: Complete and reproducible (Smoke test lưu log cơ bản).
- `TRN_001_visdrone_yolo11n_640`: Training completed, evidence incomplete (Thiếu command notes và curves, tuy nhiên `results.csv` chứng minh được metric ở mức cơ bản). Registry present.

## 9. Smoke Test vs Portfolio Baseline Check
- Smoke test COCO8 được phân tách rõ ràng với prefix `SMOKE_` trong `EXPERIMENT_REGISTRY.csv`.
- Portfolio baseline `TRN_001` sử dụng VisDrone (UAV-domain). Tuân thủ nguyên tắc Roadmap.

## 10. Claim-to-Evidence Check
- Claim: `TRN_001` đạt mAP50 = 27.3%, mAP50-95 = 15.3% (trong `day_03.md`). Evidence: Có file `results.csv` chứng minh metric ở mức cơ bản, tuy nhiên cần xuất plot curves để evidence đầy đủ hơn.
- Claim: Pose estimation functional test PASS. Evidence: Có `calibration_report.md` giải thích rõ synthetic intrinsics.

## 11. Files To Keep
- `ROADMAP.md`
- `ENVIRONMENT_CONTEXT.md`
- `AGENT_PACK_COMBINED.md`
- Các file checklist/plan trong `docs/plans/`
- Các log trong `edge-vision-uav-landing/daily_logs/`
- `edge-ai-training/experiments/EXPERIMENT_REGISTRY.csv`
- Các file dataset manifest và audit
- Tất cả file mã nguồn trong `src/`, `configs/`, `scripts/`

## 12. Files To Update, Not Duplicate
- `docs/reviews/current_project_progress_snapshot.md`
- `docs/reviews/roadmap_alignment_review.md`

## 13. Duplicate / Merge Candidates
- Không phát hiện file trùng lặp.

## 14. Patch / Archive Candidates
- Không có patch file.

## 15. Cleanup Candidates
- Không có file rác/nháp rõ ràng lúc này.

## 16. Generated / Cache Files
- Các thư mục `__pycache__` nếu có trong hệ thống thư mục Python.

## 17. Large Files / Do Not Commit
- `edge-ai-training/experiments/TRN_001_visdrone_yolo11n_640/best.pt` (5.45 MB): Checkpoint không nên commit trực tiếp vào git.
- Khuyến cáo sử dụng hoặc cập nhật `.gitignore` để tránh commit nhầm `*.pt`.

## 18. Daily Log Check
- `day_03.md`: Exists. Đã có mục Done, Metrics, Problems, Decision, Next. Phản ánh đúng thực tế.
- `day_04.md`: Not scheduled yet.

## 19. Next Action Plan Check
- `docs/plans/next_action_plan.md`: Missing next_action_plan.md. Nên tạo kế hoạch cho Day 04.

## 20. Git Safety Check
Không chạy Git. Người dùng nên tự chạy:
```bash
git status
git status --short
git ls-files | grep -E "\.pt$|\.pth$|\.onnx$|\.engine$|\.mp4$|\.avi$|\.mkv$|\.bag$|\.zip$|\.tar$|\.tar\.gz$"
```

## 21. Recommended Manual Cleanup Commands
> [!CAUTION]
> Các lệnh sau thay đổi cấu hình Git và xóa file. Vui lòng thêm `--dry-run` hoặc kiểm tra kĩ (ví dụ: mở file `.gitignore` để kiểm tra thay vì tự động append) trước khi thực thi.

```bash
# Kiểm tra kĩ .gitignore trước khi thêm
grep -q "\.pt" .gitignore || echo "*.pt" >> .gitignore

# Chỉ dry-run để kiểm tra nếu checkpoint đang bị track nhầm
git rm --cached --dry-run edge-ai-training/experiments/TRN_001_visdrone_yolo11n_640/best.pt

# Xác minh thư mục __pycache__ trước khi xóa
find . -name "__pycache__" -type d
# Cẩn thận khi chạy lệnh rm thực tế:
# find . -name "__pycache__" -type d -exec rm -r {} +
```

## 22. Risks
- Thiếu artifact chứng minh đầy đủ cho `TRN_001` (như COMMAND.txt, NOTES.md, failure cases). Điều này khiến model baseline thiếu evidence để chứng minh reproducibility.
- Synthetic intrinsics chỉ phù hợp giả lập, không đại diện cho metrics thực tế.

## 23. What Not To Delete
- Không xóa `best.pt` vì nó đang được `EXPERIMENT_REGISTRY.csv` và roadmap tham chiếu trực tiếp.

## 24. Final Review Checklist
- [x] Đã đọc `ROADMAP.md`.
- [x] Đã xác định source-of-truth precedence.
- [x] Đã kiểm tra trạng thái các patch.
- [x] Đã đọc checklist/plan/progress của tối thiểu 2 ngày gần nhất nếu tồn tại.
- [x] Đã xác định current DAY và mức độ chắc chắn.
- [x] Đã đối chiếu acceptance criteria.
- [x] Đã kiểm tra quality gate đã tới hạn.
- [x] Đã kiểm tra `docs/plans/`.
- [x] Đã kiểm tra `docs/reviews/`.
- [x] Đã kiểm tra `docs/walkthroughs/`.
- [x] Đã kiểm tra `docs/task_breakdowns/`.
- [x] Đã kiểm tra `edge-vision-uav-landing/daily_logs/`.
- [x] Đã kiểm tra dataset folders nếu đúng phase.
- [x] Đã kiểm tra dataset manifest và split integrity nếu đúng phase.
- [x] Đã kiểm tra experiment registry nếu đúng phase.
- [x] Đã kiểm tra experiment artifact và reproducibility evidence nếu đúng phase.
- [x] Đã phân biệt smoke test với portfolio baseline.
- [x] Đã kiểm tra claim-to-evidence.
- [x] Đã phân loại file nên giữ.
- [x] Đã phân loại file nên cập nhật.
- [x] Đã phân loại file trùng / cần merge.
- [x] Đã phân loại patch/reference file.
- [x] Đã phân loại file có thể xóa sau khi người dùng xác nhận.
- [x] Đã phân biệt cache với evidence artifact.
- [x] Đã cảnh báo file lớn không nên commit.
- [x] Đã kiểm tra daily log cho DAY_XX.
- [x] Đã kiểm tra `next_action_plan.md`.
- [x] Không xóa file nào.
- [x] Không rename hoặc di chuyển file.
- [x] Không merge file.
- [x] Không sửa file project thật.
- [x] Không sửa registry hoặc manifest.
- [x] Không chạy terminal.
- [x] Không chạy Git.
- [x] Không chạy test/training/benchmark.
- [x] Không commit Git.
- [x] Không tự đánh dấu task hoàn thành khi thiếu evidence.
