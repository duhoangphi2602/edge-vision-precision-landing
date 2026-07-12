# Next Action Plan

## 1. Current State
- The Day 2 Execution Plan file was deleted as requested.
- I have scanned the workspace and confirmed that the Day 2 source code files (`configs/perception.yaml`, `src/utils/overlay.py`, `src/perception/video_reader.py`, `src/perception/aruco_detector.py`, `scripts/run_perception.py`) **already exist**.
- These tasks have been marked as `[x]` in `docs/plans/day_02_checklist.md`.
- The immediate next action is for you (the user) to **test the completed code** and run the ML tasks on Machine B.

## 2. Immediate Next Step
- Test the ArUco perception pipeline on Machine A (Laptop).
- Run the YOLO baseline training on Machine B (PC GPU).

## 3. Testing Steps for Completed Tasks (Machine A)
Vui lòng thực hiện các bước sau trên Laptop (Machine A) để nghiệm thu code vừa viết:

1. **Chuẩn bị môi trường & Thiết bị:**
   - Mở terminal tại `~/Projects/edge-vision-precision-landing`
   - Kích hoạt môi trường: `source .venv/bin/activate`
   - Chuẩn bị một mã **ArUco Marker (DICT_4X4_50, ID: 0)** (bạn có thể mở trên điện thoại bằng cách search Google image "Aruco marker DICT_4X4_50 ID 0").

2. **Chạy Pipeline:**
   - Đi vào thư mục project: `cd edge-vision-uav-landing`
   - Chạy script: `python scripts/run_perception.py`

3. **Nghiệm thu trực quan (Visual Verification):**
   - Đảm bảo cửa sổ "Edge Vision Perception" hiện lên với luồng camera mượt mà.
   - Giữa màn hình có một hình chữ thập màu xanh lá (Tâm camera).
   - Đưa ArUco marker vào khung hình. Phải thấy khung bao (bounding box) màu xanh lá quanh marker và một chấm đỏ ở tâm marker.
   - Nhìn góc trên bên trái, thông số `ID: 0`, `e_x` và `e_y` nhảy real-time tùy thuộc vào độ lệch của marker so với tâm màn hình.

4. **Nghiệm thu dữ liệu (Data Verification):**
   - Nhấn phím `q` để tắt luồng camera.
   - Kiểm tra file log: `cat logs/perception_baseline.csv`
   - Đảm bảo file có chứa các dòng dữ liệu với `error_x`, `error_y` và `latency_ms` thay vì chỉ có header.

## 4. Machine B Tasks (PC GPU)
Sau khi test trên Machine A thành công, hãy sang Machine B để chạy huấn luyện YOLO:

1. Mở terminal tại `~/Projects/edge-vision-precision-landing/edge-ai-training`
2. Kích hoạt môi trường: `source ../.venv/bin/activate`
3. Chạy lệnh train:
   ```bash
   yolo detect train model=yolo11n.pt data=coco8.yaml imgsz=640 epochs=10 batch=16 project=experiments name=yolo_baseline_v0
   ```

## 5. Daily Log & Git Commit
Sau khi cả 2 máy test thành công, hãy:
1. Tạo file nhật ký `edge-vision-uav-landing/daily_logs/day_02.md` với template trong `day_02_checklist.md`.
2. Commit code lên Git:
   ```bash
   cd ~/Projects/edge-vision-precision-landing
   git add .
   git commit -m "day02: implement video reader, aruco detector and run perception pipeline"
   ```

## 6. Stop Conditions
- Không triển khai Day 3 khi Day 2 chưa test xong và chưa commit. Vui lòng phản hồi kết quả test cho tôi.
