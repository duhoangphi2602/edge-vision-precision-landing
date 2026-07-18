# Day 20 A/B Architecture Stress Test Report

## 1. Executive Summary
- **Goal:** Compare Python-only Monolithic architecture vs. Hybrid Python-C++ decoupled architecture under perception stalls (simulating CPU pressure/heavy YOLO inference).
- **Result:** Hybrid architecture maintains strict ~30Hz control loop even when perception stalls for >800ms. Python-only architecture stalls entirely, missing flight control deadlines.

## 2. Test Configuration
- **Control Rate Target:** 30Hz (33ms)
- **Perception Rate Target:** 10Hz (100ms)
- **Stall Injection:** 800ms latency injected at T=5.0s.

## 3. Findings
| Metric | Python-Only (Monolithic) | Hybrid (Python + C++) |
|---|---|---|
| Control Loop Jitter | High (dt spikes to >800ms) | Low (~33ms consistent) |
| Control Rate under Stall | Drops to <1.5Hz | Maintains 30Hz |
| Failsafe Capability | Blocked during perception stall | Active (C++ runs freely, can detect stale target and trigger Zero-Velocity) |
| System Safety | Low | High |

## 4. Conclusion
The decoupled architecture (C++ control node + Python IPC) strictly separates perception latency from control execution. This fulfills the roadmap safety requirements for SITL/Edge deployments, preventing drone crashes due to edge CPU frame drops.
