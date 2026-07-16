# Day 09: Closed-loop 2D landing simulation and domain-adaptation comparison

## Mission served
P1-A, ML

## Done
- **Machine A:** Xây dựng và chạy closed-loop 2D simulator. Chạy 4 kịch bản offset và chứng minh PID + State Machine hội tụ an toàn. Xuất file CSV log và báo cáo v0.
- **Machine B:** Hoãn fine-tune custom model do dataset PARTIALLY_COLLECTED. Đã log vào EXPERIMENT_REGISTRY.csv.

## Evidence
- `src/simulation_2d/closed_loop_2d_sim.py`
- `reports/sim_2d_*.csv`
- `docs/closed_loop_2d_v0.md`
- `EXPERIMENT_REGISTRY.csv`

## Metrics
- Settling time (2D Simulation): < 10s (MEASURED in CSV)
- Final Error (2D Simulation): < 0.05m (MEASURED in CSV)

## Problems
- Dataset custom cho Vehicle Tracking vẫn chưa sẵn sàng. (Known limitation).

## Decision
- PASS_WITH_DOCUMENTED_LIMITATION. Tiếp tục sang Day 10.

## Tomorrow
- Day 10: UDP IPC schema, receiver prototype, and tracking evaluation harness.
