# Roadmap Alignment Review

- Workspace hiện tại có bám roadmap không? **Có.** Các thư mục phân tách rõ ràng.
- DAY_03 có đúng thứ tự roadmap không? **Đúng.** Day 1 và Day 2 đã hoàn thành.
- Tên Project 1 có đúng không? **Đúng.** Là `edge-vision-uav-landing/`.
- Folder Project 1 có đúng `edge-vision-uav-landing/` không? **Đúng.**
- Có dùng sai `precision-landing-uav-sitl` không? **Không dùng tên này cho thư mục.**
- `edge-ai-training/` có đang được hiểu đúng là workspace hỗ trợ không? **Đúng.** Nằm ở root, riêng rẽ với code deploy.
- Project 2 đã bị triển khai quá sớm chưa? **Chưa.** Không có thư mục của project 2.
- Các file trong `edge-vision-uav-landing/` có phù hợp với roadmap không? **Có.** Đủ docs, cấu trúc src/ theo roadmap.
- Có thiếu file quan trọng nào không? **Không.**
- Có file nào đang nằm sai vị trí không? **Không.**
- Có phù hợp workflow 2 máy không? **Có.** Log Day 1 và Day 2 cho thấy sự tách biệt rõ ràng Machine A và Machine B.
- Có phù hợp Ubuntu 26.04, CPU-first laptop, GPU-first PC không? **Phù hợp.** Quyết định không dùng cv2.flip, dùng V4L2 phù hợp với môi trường Linux.
