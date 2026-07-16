# Error Analysis Report (TRN_002)

## Mục đích
Phân tích các mẫu nhận diện sai của mô hình YOLO 960px để lên chiến lược Data-Centric cho tuần 2.

## Phân loại lỗi thường gặp
1. **Tiny Object Misses (False Negative):** Các mục tiêu quá xa (< 10x10 px) vẫn bị bỏ sót dù đã tăng độ phân giải lên 960px.
2. **Occlusion (False Negative):** Drone/Xe bị lấp sau tán cây.
3. **Background Confusion (False Positive):** Cục đá hoặc vết nứt trên đường bị nhận diện nhầm thành phương tiện.
4. **Motion Blur:** Các frame drone xoay ngang nhanh gây mờ (smear) làm vỡ đặc trưng mục tiêu.

## Đề xuất cho Tier 2 Dataset
- Bổ sung data augmentation `motion_blur` vào cấu hình huấn luyện.
- Lọc thêm các video có môi trường độ nhiễu cao (gió giật, chuyển động nhanh).
- Cần có ảnh Negative (không có mục tiêu) để giảm False Positive từ background.