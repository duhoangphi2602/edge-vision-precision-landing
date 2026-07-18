# Video Asset Restore Verification
**Date**: 2026-07-18

## 1. Overview
This report verifies that the assets quarantined in `Q_001` can be successfully restored and have not been corrupted during the transfer.

## 2. Methodology
1. Created a temporary restore directory: `assets/videos/quarantine_restore_test/`
2. Copied all assets from `assets/videos/quarantine/Q_001/` to the test directory.
3. Computed SHA-256 checksums of the restored files.
4. Compared checksums against `QUARANTINE_MANIFEST.yaml`.
5. Deleted the temporary restore directory.

## 3. Results
- **test_landing.mp4**
  - Expected SHA-256: `ac7fee13dc6aecf64f2b3b1eca5a9d2a508626e0c22ba6b59ae60a9a7d0a0478`
  - Actual SHA-256: `ac7fee13dc6aecf64f2b3b1eca5a9d2a508626e0c22ba6b59ae60a9a7d0a0478`
  - Result: **PASS**

- **test_traffic.mp4**
  - Expected SHA-256: `d31e0ebf194cc16e50eea784e7c3b0b1bb7976a4fb9b3fec26cb92a6704cca34`
  - Actual SHA-256: `d31e0ebf194cc16e50eea784e7c3b0b1bb7976a4fb9b3fec26cb92a6704cca34`
  - Result: **PASS**

- **car-detection.mp4**
  - Expected SHA-256: `d31e0ebf194cc16e50eea784e7c3b0b1bb7976a4fb9b3fec26cb92a6704cca34`
  - Actual SHA-256: `d31e0ebf194cc16e50eea784e7c3b0b1bb7976a4fb9b3fec26cb92a6704cca34`
  - Result: **PASS**

## 4. Conclusion
100% quarantined assets restore successfully. SHA-256 matches exactly.
