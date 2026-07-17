# Day 11 Candidate Evaluation & Error Analysis
    
## Comparison Matrix (Aggregated)
| Model_ID     |   mAP50 |   Target_Lock_Rate |   Switches |   Lost_Frame_Rate |
|:-------------|--------:|-------------------:|-----------:|------------------:|
| Edge_YOLO26n |    0.301 |           0.985111 |    2.66667 |        0.0148889  |
| Edge_YOLO26s |    0.383 |           0.994111 |    1.66667 |        0.00588889 |

## Failure Categories Observed
1. **Tiny Target Loss:** Xảy ra chủ yếu trên các chuỗi `seq_hard`, tracker dễ bị LOST do target quá nhỏ.
2. **Occlusion ID Switch:** Khi bị che lấp một phần (`seq_med`), model đôi khi nhảy ID liên tục.
3. **Motion Blur:** Do rung lắc (jitter) ở các frame.

## Recommendation
- Mô hình **Edge_YOLO26s** hiện đang tốt nhất về Target_Lock_Rate và số lần Switches thấp, đạt đủ tiêu chuẩn triển khai lên Edge AI board.
- Yêu cầu kiểm thử profile P95 latency ở mức dưới 150ms để đảm bảo không bị bottle neck khi tracking theo thời gian thực.
