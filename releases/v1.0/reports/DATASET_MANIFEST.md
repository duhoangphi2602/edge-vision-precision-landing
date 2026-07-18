# Dataset Manifest (v1.0)

## 1. Nguồn Dữ Liệu
- **Tên Dataset:** UAV-Vehicle-Tracking-V1
- **Nguồn gốc:** VisDrone-VID, UAVDT, và Custom synthetic data.
- **Licenses:** Public Research / Custom.
- **Classes:** `car`, `van`, `truck`, `bus`.

## 2. Statistics & Splits
| Split | Images | Bounding Boxes | Mục đích |
|-------|--------|----------------|----------|
| Train | NOT_MEASURED | NOT_MEASURED | Đào tạo mô hình YOLO |
| Val   | NOT_MEASURED | NOT_MEASURED | Tuning thresholds |
| Test  | NOT_MEASURED | NOT_MEASURED | Đánh giá độc lập (Held-out) |

## 3. Limitations & Biases
- Data thu thập chủ yếu vào ban ngày, điều kiện ánh sáng tốt.
- Thiếu dữ liệu về môi trường mưa, sương mù dày đặc.
- Góc quay (angle) chủ yếu là góc nghiêng từ UAV, thiếu góc thẳng đứng hoàn toàn (nadir).
