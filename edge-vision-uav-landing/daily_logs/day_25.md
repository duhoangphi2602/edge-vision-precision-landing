Mission served: INFRA, P1-A, P1-B, P2-A
Done: 
- Tạo `scripts/setup.sh` cho Native SITL deployment.
- Cập nhật `Dockerfile` và `docker-compose.yml` cho CPU replay testing.
- Viết `run_all_tests.sh` hỗ trợ headless mode CI.
- Khởi tạo thư mục `releases/v1.0/` và auto-generate `checksums.txt`.
Evidence: scripts/setup.sh, Docker configs, release folder tree, checksums.
Metrics: N/A
Problems: Môi trường Docker cần user tự build image để verify full.
Decision: PASS
Tomorrow: Day 26 (Project 2 completion and multi-sequence comparison)
