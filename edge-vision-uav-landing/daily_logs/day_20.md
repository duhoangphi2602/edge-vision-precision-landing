# Day 20 Log

**Mission served:** `P1-A, P1-B, INFRA`

**Done:**
- Completed Day 19 carry-over (log & commit).
- Machine A: Wrote Python-only reference benchmark script simulating coupled architecture.
- Machine A: Wrote Hybrid perception mock injecting 800ms stalls.
- Machine A: Executed A/B stress test comparing decoupled C++ loop vs coupled Python loop.
- Machine B: Generated A/B architecture comparison chart (`plot_ab_test.py`).
- Machine A: Generated A/B architecture comparison report.

**Evidence:**
- `logs/python_only_benchmark.csv`
- `logs/day20_hybrid_cpp_log.txt`
- `reports/ab_architecture_benchmark.png`
- `reports/day20_architecture_ab_test_report.md`

**Metrics:**
- Python-only: Control dt spiked to >800ms during perception stall.
- Hybrid C++: Control dt remained stable at ~33ms, allowing C++ to detect stale state.

**Problems:**
- None. Decoupling successfully protects flight control from heavy YOLO/Perception frame drops.

**Decision:**
- Proceed with Hybrid architecture as the standard for remaining days.

**Tomorrow:**
- Day 21 — Project 2 stabilization v0.1 and Gate 3 (or continue SITL integration).
