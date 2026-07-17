# Edge CPU Environment Validation

## Decision
PASS_WITH_LIMITATION

## Changes
- Removed `opencv-python` from root `requirements.txt` to eliminate namespace collision with `opencv-contrib-python`.
- Created a specialized CPU/headless profile: `edge-vision-uav-landing/requirements_edge_cpu.txt`.
- Uninstalled all OpenCV variants in the current `.venv` and re-installed only `opencv-contrib-python==5.0.0.93`.

## Development Environment
- Python: 3.14.4
- OpenCV package: opencv-contrib-python
- OpenCV version: 5.0.0.93
- cv2 path: /home/hoangphi/Projects/edge-vision-precision-landing/.venv/lib/python3.14/site-packages/cv2/__init__.py
- ArUco available: True

## Edge CPU Test Environment
- Python: 3.14.4
- OpenCV package: opencv-contrib-python-headless
- OpenCV version: 5.0.0.93
- ONNX Runtime: 1.27.0
- Available providers: ['AzureExecutionProvider', 'CPUExecutionProvider']
- Environment size: 329M (Compared to 5.5G of the original training `.venv`)

## Verification
| Test | Result | Evidence |
|---|---|---|
| pip check | PASS | No broken requirements found in `.venv-edge-test`. |
| single OpenCV package | PASS | Only `opencv-contrib-python-headless` installed. |
| cv2 import | PASS | Import successful without GUI dependencies. |
| ArUco availability | PASS | `hasattr(cv2, "aruco")` returns True. |
| marker smoke test | PASS | `test_aruco_wrong_id.py` successfully detects and rejects markers. |
| replay headless | FAIL | `run_replay_test.py` calls `cv2.imshow()`, causing a crash on the headless package. Requires source code update to support `--headless`. |
| ONNX model load | PASS | `smoke_test_model_load.py` successfully loads the ONNX session. |
| ONNX inference | LIMITATION | `smoke_test_model_load.py` only initializes the session but does not perform inference. |
| YAML config load | PASS | `p1_b_tracking_v1.yaml` successfully parsed. |
| direct demo | FAIL | `run_perception.py` fails due to missing `configs/perception.yaml` and likely `cv2.imshow` usage. |

## Limitations
- No Jetson validation unless tested on Jetson.
- No Raspberry Pi validation unless tested on Raspberry Pi.
- No real-UAV deployment claim.
- The `run_replay_test.py` and `run_perception.py` scripts do not natively support headless mode and will crash in an actual headless Edge CPU environment. They need to be updated to support `--headless` or `--no-display` flags.
- The `smoke_test_model_load.py` script only tests loading the model into memory, it does not perform a dummy inference to verify metadata input/output shapes.

## Decision for Current .venv
- CLEANUP_VALIDATED
