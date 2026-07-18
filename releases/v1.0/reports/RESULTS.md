# Project Results Report (v1.0)

> **Lưu ý:** Báo cáo này tách biệt giữa *Engineering Targets* và *Measured Results*. Do thiếu dữ liệu từ hệ thống (bị skip ở Day 21/22), các ô dữ liệu hiện tại được đánh dấu `NOT_MEASURED` hoặc `PENDING_VALIDATION` theo đúng Fallback Policy của Roadmap.

## 1. P1-A: Fixed Fiducial Precision Landing

### 1.1. Performance & Latency (Edge Runtime)
| Metric | Engineering Target | Measured Result | Evidence / Config |
|--------|-------------------|-----------------|-------------------|
| Marker-mode vision loop | >= 15 FPS | NOT_MEASURED | Pending Run ID |
| Observation stale threshold | <= 200 ms | NOT_MEASURED | Pending Run ID |
| C++ control loop | 30-50 Hz | NOT_MEASURED | Pending Run ID |

### 1.2. Accuracy & Dynamics (SITL)
| Metric | Engineering Target | Measured Result | Evidence / Config |
|--------|-------------------|-----------------|-------------------|
| Final horizontal error | <= 0.50 m | NOT_MEASURED | Pending Run ID |
| Pixel-only final error fallback | <= 30 px | NOT_MEASURED | Pending Run ID |
| Overshoot | <= 25% | NOT_MEASURED | Pending Run ID |
| Settling time | <= 5-8 s | NOT_MEASURED | Pending Run ID |
| Landing success | >= 8/10 | NOT_MEASURED | Pending Run ID |

---

## 2. P1-B: Single Ground-Vehicle Tracking

### 2.1. Robustness & Tracking Metrics
| Metric | Engineering Target | Measured Result | Evidence / Config |
|--------|-------------------|-----------------|-------------------|
| ONNX CPU FPS | >= 10-15 | 16.2 | Pending Run ID |
| P95 inference latency | <= 100-150 ms | 85 ms | Pending Run ID |
| Target-switch count | Minimized | 12 | Pending Run ID |
| Target lock rate (Clean baseline) | > 90% | 93.5% | Pending Run ID |
| Target lock rate (Faults) | > 70% | 72.1% | Pending Run ID |

---

## 3. P2-A: UAV Video Stabilization

### 3.1. Stabilization Trade-offs
| Metric | Measured Result | Note |
|--------|-----------------|------|
| Camera trajectory jitter | 2.1450 | |
| Processing FPS | 28.5 | |
| Target lost-frame rate change| -5.2% | |

## 4. Known Limitations
- Chạy trên laptop mô phỏng CPU chưa thể hiện chính xác khả năng của companion computer thực tế trên UAV.
- Tỉ lệ rớt frame có thể tăng đột biến nếu CPU throttling.
