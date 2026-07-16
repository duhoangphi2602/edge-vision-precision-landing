# Day 08: MAVLink Design, Landing State Machine & Dataset Freeze

## Mission served
P1-A, ML

## Done
- **Machine A:** Khởi tạo `MAVLINK_DESIGN.md`. Implement và test `LandingStateMachine` (Python), chứng minh từ chối tín hiệu stale.
- **Machine B:** Thực hiện Audit Dataset v0.1, ghi nhận trạng thái PARTIALLY_COLLECTED, tránh fabricate data.

## Evidence
- `docs/MAVLINK_DESIGN.md`
- `reports/state_machine_test_output.log`

## Metrics
- Stale rejection timeout: 0.2s (Verified in tests)

## Problems
- Dataset custom chưa thu thập đủ số lượng frame.

## Decision
- PASS. Chờ đến Day 09 để thực hiện 2D Simulation.

## Tomorrow
- Day 09: Closed-loop 2D landing simulation and domain-adaptation comparison.
