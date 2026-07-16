# Day 06: Production Alignment & Cross-Process IPC

## Done
- Định nghĩa JSON schema cho Observation theo ROADMAP 3.1.5.
- Cấu hình YAML cho Fixed ArUco Landing (mission P1-A).
- Hoàn thiện UDP Sender/Receiver với cơ chế stale data rejection (> 200ms).
- Thiết lập Experiment Registry cho Machine B.

## Metrics & Test
- UDP truyền tin thành công ở localhost (Port 5005).
- Receiver lọc thành công gói tin bị trễ hoặc rớt mạng.

## Next Action
- Tích hợp UDP vào PID Controller cũ và chuyển sang môi trường Gazebo SITL (Day 07).
