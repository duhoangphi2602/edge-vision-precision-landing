# Day 1 Manual Execution Checklist (Simplified & Explained)

## 1. Laptop (Machine A): Khởi tạo Project 1 (`edge-vision-uav-landing`)
**Mục tiêu:** Xây dựng khung thư mục chuẩn cho mã nguồn C++/Python và tài liệu.

💡 **Quyết định kiến trúc & Giải thích:**
- **Vì sao tách biệt `src/perception` (Python) và `src/control_cpp` (C++)?**
  Python có hệ sinh thái AI/OpenCV cực tốt để code thuật toán nhận diện nhanh, nhưng nó bị vướng GIL (Global Interpreter Lock) và Garbage Collection, dẫn đến **không đảm bảo thời gian thực cứng (hard real-time)** để điều khiển bay (PID Controller). C++ thì ngược lại, quản lý bộ nhớ thủ công và độ trễ cực thấp, cực kỳ phù hợp để gửi tín hiệu MAVLink an toàn. Việc ép tách thư mục này buộc chúng ta phải thiết kế một cầu nối giao tiếp IPC (Inter-Process Communication qua UDP/ZeroMQ) ngay từ đầu, tránh việc code "mì gõ" dính chùm mọi thứ vào một script Python duy nhất dẫn đến crash UAV.

- [x] **Mở terminal trên Laptop (Machine A)** và chạy lệnh:
  ```bash
  cd ~/Projects/edge-vision-precision-landing
  mkdir -p edge-vision-uav-landing
  cd edge-vision-uav-landing
  
  mkdir -p src/{perception,estimation,ipc,evaluation,utils}
  mkdir -p src/control_cpp/{include,src,tests}
  mkdir -p src/interface_cpp/{include,src,tests}
  mkdir -p configs tests/{python,cpp} scripts reports logs videos models docs daily_logs
  
  touch README.md TECHNICAL_DESIGN.md PROBLEM.md REQUIREMENTS.md TEST_PLAN.md RESULTS.md LIMITATIONS.md MODEL_CARD.md DATASET_MANIFEST.md CLEAN_CLONE_TEST.md PORTFOLIO_SUMMARY.md
  ```
- [x] Dùng lệnh `tree -L 2` để kiểm tra, đảm bảo đã có thư mục `daily_logs` và `src`.

## 2. PC GPU (Machine B): Khởi tạo ML Workspace (`edge-ai-training`)
**Mục tiêu:** Tạo không gian tách biệt để chứa data train và model.

💡 **Quyết định kiến trúc & Giải thích:**
- **Vì sao phải tách riêng thư mục training ra khỏi Project 1?**
  Trong thực tiễn MLOps, môi trường huấn luyện (cần PyTorch, GPU, hàng chục GB hình ảnh) rất khác với môi trường suy diễn/triển khai (chỉ cần ONNXRuntime/TensorRT, CPU/NPU nhỏ). Nếu bạn gộp thư mục training vào trong repo project chính, kho lưu trữ Git sẽ phình to hàng chục GB. Khi một thiết bị Edge (như Raspberry Pi hay Jetson) pull code về để chạy, nó sẽ bị phung phí tài nguyên để tải dữ liệu huấn luyện mà nó không bao giờ dùng tới.
- **Docker hay Venv ở bước này?**
  Tại Machine B (PC GPU) phục vụ training, **bạn NÊN dùng `.venv` (hoặc Conda)**. Lý do: Setup Docker GPU pass-through trên Linux tốn thời gian và đôi khi làm mất tính năng autocomplete của IDE (nếu chưa map đúng volume). Dùng `.venv` cho phép bạn visualize ảnh, debug code train YOLO cực kỳ nhanh và mượt mà.

- [x] **Mở terminal trên PC GPU (Machine B)** và chạy lệnh:
  ```bash
  cd ~/Projects/edge-vision-precision-landing
  mkdir -p edge-ai-training/{datasets,models,experiments,logs,scripts,reports}
  
  touch edge-ai-training/experiments/EXP_PLAN.md
  touch edge-ai-training/datasets/DATASET_SOURCES.md
  ```
- [x] Kiểm tra bằng lệnh `ls -la edge-ai-training`.

## 3. Cả 2 máy (Shared): Setup `.gitignore` và `requirements.txt`
**Mục tiêu:** Đồng nhất thư viện Python và chặn đẩy file rác lên Git.

💡 **Quyết định kiến trúc & Giải thích:**
- **Chiến lược sử dụng `.venv` vs `Docker` cho toàn dự án:**
  - **Dùng `.venv`:** Ở giai đoạn phát triển ban đầu (Day 1 - Day 5), ta dùng `.venv` để chạy thử các script Python OpenCV, check thuật toán qua webcam. Nó nhẹ, mở VSCode lên là code được ngay, không phải chờ build image.
  - **Dùng `Docker`:** Từ giai đoạn tích hợp hệ thống (Day 10 trở đi), đặc biệt là khi phải compile C++ và thiết lập luồng ROS 2, ta **BẮT BUỘC dùng Docker**. Docker sẽ tạo ra môi trường đóng gói y hệt hệ điều hành của con UAV thật, giúp đảm bảo tính "Reproducibility" (Ai tải về, hay máy tính nhúng nào kéo về cũng chạy được 100% không văng lỗi thiếu thư viện OS).
  - Bước chốt `requirements.txt` hôm nay chính là tiền đề để sau này ta copy nó vào file `Dockerfile` một cách sạch sẽ.

- [x] **Trên máy nào cũng được**, mở terminal và chạy lệnh:
  ```bash
  cd ~/Projects/edge-vision-precision-landing
  touch requirements.txt .gitignore
  ```
- [x] Mở file `requirements.txt` bằng trình soạn thảo và chèn nội dung sau:
  ```txt
  numpy
  opencv-python
  opencv-contrib-python
  pyyaml
  pytest
  pytest-cov
  matplotlib
  pandas
  onnx
  onnxruntime
  ultralytics
  psutil
  rich
  ```
- [x] Mở file `.gitignore` và chèn nội dung sau:
  ```gitignore
  .venv/
  __pycache__/
  *.pyc
  build/
  dist/
  *.egg-info/
  logs/
  videos/
  models/*.pt
  models/*.onnx
  models/*.engine
  models/openvino_model/
  edge-ai-training/datasets/
  edge-ai-training/models/
  *.avi
  *.mp4
  *.bag
  *.ulg
  .DS_Store
  .vscode/
  ```

## 4. PC GPU (Machine B): Quy tắc vận hành 1 - Sinh log/metric baseline
**Mục tiêu:** Tuân thủ chuẩn "Mỗi ngày phải có metric". Ngày 1 sẽ chốt file schema CSV.

💡 **Quyết định kiến trúc & Giải thích:**
- **Vì sao rảnh rỗi đi tạo file CSV khi chưa code thuật toán?**
  Đây là ứng dụng tư duy **Design by Contract (Thiết kế theo giao kèo)**. Thay vì code thuật toán rắc rối rồi mới nghĩ cách in log, ta ép module phải phục vụ việc đo lường ngay từ đầu. File CSV chuẩn này (`timestamp, error_x, error_y, latency`) chính là "giao kèo". Ngày mai viết code Perception kiểu gì không cần biết, nhưng cuối cùng output phải trả ra đúng định dạng này thì hệ thống C++ Control phía sau mới lấy để chạy PID được.

- [x] **Trên PC GPU (Machine B)**, chạy lệnh:
  ```bash
  cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
  echo "timestamp_ns,frame_id,detected,error_x,error_y,latency_ms" > logs/perception_baseline.csv
  ```
- [x] Dùng `cat logs/perception_baseline.csv` để xác nhận file đã có header.

## 5. Laptop (Machine A): Quy tắc vận hành 2 - Viết nhật ký `day_01.md`
**Mục tiêu:** Ghi lại tiến độ hằng ngày theo đúng template của ROADMAP.

- [x] **Trên Laptop (Machine A)**, dùng trình soạn thảo mở file `edge-vision-uav-landing/daily_logs/day_01.md` và chèn nội dung:
  ```md
  # Day 01
  
  ## Done
  - [Machine A] Initialized monorepo and Project 1 structure `edge-vision-uav-landing`.
  - [Machine A] Created core requirements and design document skeletons.
  - [Machine B] Initialized `edge-ai-training` workspace for ML operations.
  - [Shared] Established `.gitignore` and `requirements.txt`.
  - [Shared] Created perception baseline metric file to enforce daily metric rule.
  
  ## Metrics
  - FPS: N/A
  - Latency: N/A
  - Error: N/A
  - CPU/RAM: N/A
  - Test pass/fail: N/A
  
  ## Problems
  - None today. Environment on both machines is fully ready.
  
  ## Decision
  - Followed MLOps separation: detached `edge-ai-training` from edge deployment codebase.
  - Will use `.venv` for prototyping Day 1-5, and transition to `Docker` for C++/IPC reproducibility later.
  
  ## Tomorrow
  - Laptop: Implement `video_reader.py` and `aruco_detector.py`.
  - PC GPU: Prepare YOLO baseline training environment and tiny test dataset.
  ```

## 6. Laptop (Machine A): Quy tắc vận hành 3 - Code Commit cuối ngày
**Mục tiêu:** Đóng băng trạng thái hoàn thành Day 1.

- [ ] **Trên Laptop (Machine A)**, chạy lệnh:
  ```bash
  cd ~/Projects/edge-vision-precision-landing
  git init
  git add .
  git commit -m "day01: initialize product roadmap, requirements and folder structures"
  ```
- [ ] Chạy `git log -1` để kiểm tra commit đã thành công chưa.

## 7. Nghiệm thu Day 1 (Acceptance)
- [x] Code và tài liệu chuẩn đã nằm đúng trong `edge-vision-uav-landing`.
- [ ] Đã có `.gitignore` chặn được tệp rác.
- [x] Đã viết xong `day_01.md`.
- [x] Đã tạo metric baseline đầu tiên.
- [ ] Đã commit code thành công.
