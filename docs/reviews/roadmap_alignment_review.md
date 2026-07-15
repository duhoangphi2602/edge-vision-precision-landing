# Roadmap Alignment Review (Đánh giá mức độ bám sát Roadmap)

- Workspace hiện tại có bám roadmap không? **Có.** Các thư mục được phân tách rõ ràng.
- DAY_03 có đúng thứ tự roadmap không? **Đúng.** Day 1 và Day 2 đã hoàn thành trọn vẹn.
- Tên Project 1 có đúng không? **Đúng.** Tên chuẩn là `edge-vision-uav-landing/`.
- Folder Project 1 có đúng `edge-vision-uav-landing/` không? **Đúng.**
- Có dùng sai `precision-landing-uav-sitl` không? **Không dùng tên này cho thư mục.**
- `edge-ai-training/` có đang được hiểu đúng là workspace hỗ trợ không? **Đúng.** Nó nằm ở root, tách biệt hoàn toàn với mã nguồn deploy của Project 1.
- Project 2 đã bị triển khai quá sớm chưa? **Chưa.** Không tồn tại thư mục của Project 2.
- Các file trong `edge-vision-uav-landing/` có phù hợp với roadmap không? **Có.** Các thư mục `src/` và các tài liệu (docs) bám sát cấu trúc của roadmap.
- Có thiếu file quan trọng nào không? **Không.**
- Có file nào đang nằm sai vị trí không? **Không.**
- Có phù hợp workflow 2 máy không? **Có.** Log của Day 1 và Day 2 cho thấy sự phân chia công việc rất rõ ràng giữa Machine A và Machine B.
- Có phù hợp Ubuntu 26.04, CPU-first laptop, GPU-first PC không? **Phù hợp.** Đã có những quyết định kỹ thuật cụ thể (chẳng hạn không dùng `cv2.flip`, dùng backend `V4L2`) để tối ưu và fix lỗi trên môi trường Linux.
