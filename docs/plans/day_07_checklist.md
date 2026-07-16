# Day 07 Manual Execution Checklist: Gate 1 Foundation Review & Dataset v0.1 Plan

## Cảnh báo lộ trình (Roadmap Alignment)
*Theo đúng ROADMAP.md, Day 07 TẬP TRUNG HOÀN TOÀN vào việc đóng Gate 1 và lên kế hoạch Dataset v0.1. TUYỆT ĐỐI KHÔNG triển khai code C++ Control, MAVSDK, UDP C++ Receiver, hay C++ State Machine trong ngày hôm nay. Các task C++ đã được dịch chuyển sang Day 15 - Day 19.*

---

## Phase 0 — Preflight

### Task 0.1: Đọc và đối chiếu tài liệu tiến độ
- **Mục tiêu:** Xác minh các tài liệu roadmap, plan, log, và status Git để nắm rõ bối cảnh.
- **Lý do (💡 Giải thích chuyên sâu):** Việc phân loại từng hạng mục thành `Verified`, `Partially Verified`, `Missing`, `Blocked`, hoặc `Deferred` là bắt buộc cho buổi Review. Không thể đánh giá hệ thống nếu không kiểm tra Git status và history, tránh việc code chạy được trên máy cá nhân nhưng chưa commit.
- **Dependency:** Các file markdown của Day 05, Day 06 và `ROADMAP.md`.
- **Thao tác (Manual Execution):**
  - [x] **Thao tác 1:** Chuyển đến thư mục gốc và kiểm tra Git:
    ```bash
    cd ~/Projects/edge-vision-precision-landing
    git status
    ```
  - [x] **Thao tác 2:** Kiểm tra bằng mắt các file log của ngày hôm trước để đảm bảo PID và UDP schema đã tồn tại.
- **Command kiểm tra:**
  ```bash
  ls edge-vision-uav-landing/src/ipc/
  ```
- **Expected output:** Branch sạch, không có uncommitted changes. 
- **Evidence cần lưu:** Không cần lưu file mới.
- **Acceptance criteria:** Đã đọc đủ tài liệu và hiểu rõ tiến độ.
- **Fallback/blocker:** Nếu git status đang dở dang, phải commit hoặc stash trước khi Review.

---

## Phase 1 — Machine A: Gate 1 Foundation Review

### Task 1.1: Review evidence của Perception (ArUco) & PID Replay
- **Mục tiêu:** Tổng hợp bằng chứng cho thấy ArUco detector (ID 0) chạy đúng, reject sai ID, và PID controller chịu được độ trễ (delay) trong quá trình test Replay.
- **Lý do (💡 Giải thích chuyên sâu):** Gate 1 là cột mốc khẳng định "Phần mềm lõi (Computer Vision và Control) đã hoàn thiện về mặt logic". Nếu pose sai dấu (sign convention) hoặc controller crash khi rớt frame, khi lên SITL UAV lật tức thì. Do đó, evidence (file log/csv) từ Day 05 và Day 06 là cứu cánh cho Gate 1.
- **Dependency:** File `reports/pid_simulation_summary.csv` và code test.
- **Thao tác (Manual Execution):**
  - [x] **Thao tác 1:** Mở terminal kiểm tra sự tồn tại của evidence:
    ```bash
    cat edge-vision-uav-landing/reports/pid_simulation_summary.csv
    ```
  - [x] **Thao tác 2:** Chạy script kiểm tra Wrong-ID để xác minh hệ thống lọc được mục tiêu và copy log output làm bằng chứng.
    ```bash
    python edge-vision-uav-landing/test_aruco_wrong_id.py
    ```
- **Command kiểm tra:** Kiểm tra xem có log output in ra terminal không.
- **Expected output:** File CSV có số liệu, màn hình in ra kết quả PASS cho cả 2 test (Đúng ID và Sai ID).
- **Evidence cần lưu:** File CSV và log output terminal.
- **Acceptance criteria:** Wrong-marker test pass. Replay pipeline chịu được drop frame. PX4/Gazebo startup (hoặc Hybrid SITL) được ghi nhận trong documentation.
- **Fallback/blocker:** Nếu thiếu code test Wrong-ID, đánh dấu `Missing` vào báo cáo.

### Task 1.2: Viết báo cáo Gate 1 (WEEK1_REPORT) & Cập nhật README
- **Mục tiêu:** Tạo văn bản báo cáo chính thức chốt lại trạng thái Gate 1.
- **Lý do (💡 Giải thích chuyên sâu):** Viết báo cáo giúp rà soát toàn bộ các criterion. Trạng thái `PASS_WITH_DOCUMENTED_LIMITATION` là công cụ mạnh mẽ trong kỹ thuật hệ thống để đi tiếp mà không giấu giếm rủi ro kỹ thuật.
- **Dependency:** Số liệu từ Task 1.1.
- **Thao tác (Manual Execution):**
  - [x] **Thao tác 1:** Tạo file báo cáo:
    ```bash
    touch edge-vision-uav-landing/docs/WEEK1_REPORT.md
    ```
  - [x] **Thao tác 2:** Copy TOÀN BỘ nội dung sau vào `edge-vision-uav-landing/docs/WEEK1_REPORT.md`:
    ```markdown
    # Gate 1 Foundation Review & Week 1 Report

    ## 1. Trạng thái tổng quan
    **Quyết định:** `PASS_WITH_DOCUMENTED_LIMITATION`
    
    ## 2. Kết quả kiểm tra (Checklist)
    | Hạng mục | Phân loại | Ghi chú / Evidence |
    |---|---|---|
    | ArUco `DICT_4X4_50`, ID 0 | Verified | Log output: PASS (test_aruco_wrong_id) |
    | Correct-ID / Wrong-ID tests | Verified | Log output: Rejected marker ID != 0 |
    | Pixel-error & Sign convention | Verified | Trục x, y chuẩn OpenCV |
    | Python PID tests & Metrics | Verified | `reports/pid_simulation_summary.csv` |
    | Replay Pipeline & Fault Injection | Verified | Xử lý được drop frame, noise |
    | Mission Config & Schema (JSON/UDP) | Verified | `MISSION_CONTRACTS.md` |
    | PX4/Gazebo Startup / Hybrid SITL | Deferred | Đang xử lý ở Phase SITL kế tiếp |

    ## 3. Blockers / Limitations
    - **Limitation 1:** Giao tiếp UDP Python <-> C++ chưa thực thi (được dời sang Day 15+). Hiện tại đang test thuần Python.
    - **Limitation 2:** SITL Gazebo chưa bay thực tế, mới đo đạc controller độc lập.
    ```
- **Command kiểm tra:**
  ```bash
  cat edge-vision-uav-landing/docs/WEEK1_REPORT.md
  ```
- **Expected output:** Báo cáo Markdown hiển thị rõ ràng bảng kết quả.
- **Evidence cần lưu:** `WEEK1_REPORT.md`.
- **Acceptance criteria:** Báo cáo có kết luận rõ ràng, mọi hạng mục đều có phân loại.
- **Fallback/blocker:** N/A.

---

## Phase 2 — Machine B: Dataset v0.1 Plan

### Task 2.1: Lập kế hoạch Dataset, Audit & Sequence-based Split
- **Mục tiêu:** Tạo file Dataset Manifest ghi rõ nguồn, quy chuẩn nhãn và cách chia dataset.
- **Lý do (💡 Giải thích chuyên sâu):** "Sequence-based train/val/held-out split". Trong video UAV, các frame liên tiếp rất giống nhau. Nếu chia ngẫu nhiên (random split), frame tập test sẽ gần như y hệt tập train, gây ra "data leakage". Bắt buộc phải chia dữ liệu theo Sequence (đoạn video khác nhau).
- **Dependency:** `EXPERIMENT_REGISTRY.csv`.
- **Thao tác (Manual Execution):**
  - [x] **Thao tác 1:** Tạo file Dataset Manifest:
    ```bash
    mkdir -p edge-ai-training/docs
    touch edge-ai-training/docs/DATASET_MANIFEST.md
    ```
  - [x] **Thao tác 2:** Copy và dán đoạn code sau vào `edge-ai-training/docs/DATASET_MANIFEST.md`:
    ```markdown
    # Dataset Manifest (v0.1 Plan)
    
    ## 1. Nguồn dữ liệu (Source / License)
    - **Baseline Dataset:** VisDrone 2019 (UAV-domain). License: Phục vụ nghiên cứu/phi thương mại.
    - **Adaptation Dataset (v0.1):** Dữ liệu thu thập tùy chỉnh (Custom).

    ## 2. Annotation Guidelines
    - Bounding Box phải bao trọn toàn bộ xe (kể cả bóng đổ mờ nếu cấu trúc xe vẫn rõ).
    - Các class được map về `car`, `van`, `truck`, `bus`.
    
    ## 3. Sequence-based Split Policy
    **TUYỆT ĐỐI KHÔNG CHIA RANDOM THEO FRAME.**
    - **Train Split:** 70% số sequence.
    - **Validation Split:** 15% số sequence (dùng cho Early Stopping).
    - **Held-out Test Split:** 15% số sequence (Dùng để chốt metrics P1-B. Mô hình không được tiếp xúc tập này trong lúc huấn luyện).

    ## 4. Sequence Inventory (Audit v0.1)
    - Đang thống kê số lượng video clip cụ thể trong VisDrone...
    - Kế hoạch: Xây dựng tool lọc các sequence có độ cao và góc quay tương đương với yêu cầu Mission P1-B.
    ```
- **Command kiểm tra:** 
  ```bash
  cat edge-ai-training/docs/DATASET_MANIFEST.md
  ```
- **Expected output:** Manifest hiển thị đầy đủ tiêu chuẩn chia dataset.
- **Evidence cần lưu:** `DATASET_MANIFEST.md`.
- **Acceptance criteria:** Tài liệu nêu rõ chiến lược "Sequence-based split". Kế hoạch adaptation dataset v0.1 được đề ra.
- **Fallback/blocker:** Thiếu storage để tải toàn bộ VisDrone -> Báo cáo tình trạng bộ nhớ.

---

## Phase 3 — Tổng kết cuối ngày (Daily Log)

### Task 3.1: Viết Daily Log Day 07
- **Mục tiêu:** Lưu nhật ký xác nhận Day 07 hoàn tất đúng roadmap.
- **Lý do (💡 Giải thích chuyên sâu):** Daily Log là bằng chứng kiểm toán quá trình phát triển (auditing), giúp truy vết lại "vào ngày này chúng ta đã chốt phương án nào".
- **Dependency:** Báo cáo Gate 1.
- **Thao tác (Manual Execution):**
  - [x] **Thao tác 1:** Tạo file log mới:
    ```bash
    touch edge-vision-uav-landing/daily_logs/day_07.md
    ```
  - [x] **Thao tác 2:** Copy và dán toàn bộ đoạn sau vào `edge-vision-uav-landing/daily_logs/day_07.md`:
    ```markdown
    # Day 07: Gate 1 Foundation Review & Dataset v0.1 Plan

    ## Done
    - **Machine A:** Thực hiện rà soát Gate 1. Xác nhận ArUco detector hoạt động, loại bỏ được wrong-ID, PID vượt qua bài test nhiễu và độ trễ.
    - **Machine A:** Lập báo cáo `WEEK1_REPORT.md` với kết luận `PASS_WITH_DOCUMENTED_LIMITATION`.
    - **Machine B:** Lập kế hoạch `DATASET_MANIFEST.md`, chốt nguyên tắc "Sequence-based split" để ngăn rò rỉ dữ liệu.

    ## Metrics & Test
    - Mọi đánh giá Gate 1 đều dựa trên evidence (csv, logs, demo video) đã có từ Day 05-06.
    
    ## Next Action
    - Chuyển sang Day 08: Thiết kế MAVLink và viết Python Reference State Machine.
    ```
  - [x] **Thao tác 3:** Commit tất cả thay đổi:
    ```bash
    git add edge-vision-uav-landing/docs/ edge-ai-training/docs/ edge-vision-uav-landing/daily_logs/
    git commit -m "docs: finalize Gate 1 foundation review and dataset v0.1 plan for Day 07"
    ```
- **Command kiểm tra:**
  ```bash
  git log -1
  ```
- **Expected output:** Commit thành công với lời nhắn rõ ràng.
- **Evidence cần lưu:** `day_07.md` và git commit hash.
- **Acceptance criteria:** Không có bất kỳ dòng code C++ core nào được triển khai sai timeline. Git working tree gọn gàng.
- **Fallback/blocker:** N/A.
