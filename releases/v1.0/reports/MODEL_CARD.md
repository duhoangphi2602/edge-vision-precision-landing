# Model Card: Edge-YOLO-Vehicle

## 1. Thông Tin Chung
- **Model Version:** 1.0 (PENDING_VALIDATION)
- **Architecture:** YOLO (ONNX Exported)
- **Input Size:** 640x640 (RGB)
- **Task:** Object Detection (Classes: car, van, truck, bus)
- **Runtime:** ONNXRuntime (CPU/GPU)

## 2. Intended Use (Mục đích sử dụng)
- **Primary Use Case:** Nhận diện và cung cấp bounding box của phương tiện trên mặt đất từ camera UAV (Góc nhìn từ trên cao).
- **Out of Scope:** Không dùng để nhận diện người, động vật, biển báo giao thông. Không dùng để đo lường vận tốc phương tiện trong thế giới thực khi chưa calibrate camera.

## 3. Performance Metrics
> *Dữ liệu đang chờ từ experiment registry (Day 21)*
- **mAP50:** NOT_MEASURED
- **mAP50-95:** NOT_MEASURED
- **Inference Latency (CPU Batch 1):** NOT_MEASURED
- **Model Size:** NOT_MEASURED MB

## 4. Failure Behavior
- **False Negatives:** Dễ mất mục tiêu khi phương tiện đi vào bóng râm gắt hoặc bị che khuất bởi tán cây (Occlusion).
- **False Positives:** Đôi khi nhầm lẫn các vật thể hình hộp (ví dụ: container rác) thành xe tải nếu nhìn từ góc thẳng đứng.
