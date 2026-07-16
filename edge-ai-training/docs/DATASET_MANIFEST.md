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
