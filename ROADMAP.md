
# Roadmap 30 ngày — Production-Oriented, Mission-Driven, Evidence-Based

## Edge Vision Precision Landing + AI Ground-Vehicle Tracking + Gimbal Video Stabilization

> **Document status:** Final consolidated roadmap v1.0  
> **Workspace root:** `~/Projects/edge-vision-precision-landing/`  
> **Current progress at consolidation:** `DAY_05 in progress` — must be verified from source, tests, logs, experiment registry, and daily logs before changing day status.  
> **Source of truth:** This `ROADMAP.md` supersedes standalone roadmap patches after their requirements have been merged and verified.  
> **Claim policy:** The roadmap targets a production-oriented portfolio. The phrase `production-ready` may only be used for a specific deployment profile after its evidence gate passes.

---

## 0. Non-negotiable project identity

The workspace contains **two portfolio projects** and **one supporting ML workspace**:

```text
~/Projects/edge-vision-precision-landing/
├── edge-vision-uav-landing/                 # Project 1
├── edge-ai-training/                        # Shared ML model factory, not Project 3
└── gimbal-video-stabilization-analyzer/     # Project 2
```

### Project 1

**Edge Vision Precision Landing & AI Target Tracking for UAV SITL**

Folder:

```text
edge-vision-uav-landing/
```

### Project 2

**Gimbal-Aware Video Stabilization & Tracking Quality Analyzer**

Folder:

```text
gimbal-video-stabilization-analyzer/
```

### Supporting workspace

```text
edge-ai-training/
```

Its role is dataset engineering, training, evaluation, export, optimization, model packaging, and artifact handoff. It is **not** presented as an independent portfolio project.

The deprecated name below must not be used:

```text
precision-landing-uav-sitl
```

---

# 1. Goal of the 30-day roadmap

Build two measurable and reproducible portfolio products on a laptop and a PC GPU without requiring a real UAV.

The portfolio must demonstrate five capability groups:

1. **AI / Computer Vision**
   - OpenCV
   - ArUco detection
   - camera calibration
   - pose estimation
   - YOLO vehicle detection
   - single-target tracking
   - tracking and failure metrics

2. **Edge AI**
   - ONNX Runtime
   - optional OpenVINO
   - batch-size-1 benchmarking
   - P50/P95 latency
   - FPS
   - startup time
   - CPU/RAM/VRAM
   - model-size and accuracy trade-offs
   - constrained-resource testing

3. **UAV / Robotics**
   - PX4 SITL
   - Gazebo
   - downward-facing camera concept
   - visual centering
   - landing state machine
   - MAVLink-compatible command design
   - failsafe behavior

4. **C++ / Embedded-style systems**
   - C++17
   - CMake
   - PID controller
   - failsafe manager
   - fixed-rate control loop
   - stale-message rejection
   - process communication
   - timing and jitter measurement

5. **Product engineering**
   - mission contracts
   - requirements
   - versioned configuration
   - interface schemas
   - unit/component/integration/regression testing
   - deployment scripts
   - Docker
   - clean-clone verification
   - evidence-backed claims
   - reports, limitations, and demo assets

The final result is not “an application that runs once.” It must be understandable and reproducible by a reviewer who did not build it.

---

# 2. Execution strategy and machine roles

## Machine A — Laptop: System Engineer and deployment target

Primary responsibilities:

- Project 1 architecture and integration
- replay/webcam/Gazebo input adapters
- ArUco detection and pose estimation
- PID and landing state machine
- PX4/Gazebo/SITL
- C++ control path
- Python-to-C++ IPC
- MAVLink-compatible bridge
- robustness testing
- CPU deployment benchmark
- Docker and clean-clone testing
- final documentation and demo

The laptop is the primary evidence source for CPU edge deployment. A benchmark on the PC GPU alone is not sufficient evidence for laptop deployment.

## Machine B — PC GPU: ML Engineer

Primary responsibilities:

- official UAV-domain dataset setup
- dataset manifests and auditing
- YOLO training
- sequence-aware split validation
- failure analysis
- custom/synthetic adaptation data
- ablation experiments
- model export
- ONNX/OpenVINO sanity tests
- batch evaluation
- training and benchmark charts
- versioned model packages

## Parallel-work rule

Machine A and Machine B may operate in parallel, but ML experiments must not block the required system deliverables:

```text
marker landing
→ PID
→ replay robustness
→ state machine
→ C++ control
→ IPC
→ SITL/hybrid integration
```

Project 2 implementation begins only when its scheduled phase is reached.

---

# 3. Production mission contracts

Every implemented feature must map to one of the following mission IDs:

```text
P1-A   Fixed Fiducial Precision Landing
P1-B   Single Ground-Vehicle Tracking
P2-A   UAV Video Stabilization and Tracking Impact Analysis
ML     Dataset / experiment / model lifecycle
INFRA  Shared configuration, logging, testing, deployment, documentation
```

No task may be added solely because it looks technically impressive. It must serve a mission, a quality gate, or a measured risk.

---

## 3.1 Mission P1-A — Fixed Fiducial Precision Landing

### 3.1.1 Problem statement

A simulated quadrotor must use a downward-facing camera to locate, align with, and land near the center of a fixed landing pad marked by a known fiducial marker.

### 3.1.2 Primary operator

```text
SITL operator / technical reviewer
```

### 3.1.3 Locked target contract v1

```yaml
mission_id: P1_A_FIXED_ARUCO_LANDING
marker_type: aruco
marker_dictionary: DICT_4X4_50
marker_id: 0
marker_size_m: 0.20
landing_pad_size_m: 0.60
landing_pad_motion: fixed
camera_orientation: downward_facing
gazebo_model_name: landing_pad_aruco_id0
world_frame: world
```

The exact pad world position must be configured, not hidden in code:

```yaml
landing_pad_position_m:
  x: 0.0
  y: 0.0
  z: 0.0
```

The UAV must use visual observations for final alignment. A demo that simply commands the known pad coordinate without using vision does not satisfy the mission.

### 3.1.4 Required input profiles

#### Profile A — Replay

Input:

- MP4/AVI video
- image sequence
- versioned replay manifest

Purpose:

- deterministic perception testing
- PID-input testing
- fault injection
- regression testing
- demo without SITL dependency

#### Profile B — Webcam bench demo

Input:

- live webcam, default index 0
- a printed ArUco `DICT_4X4_50`, ID 0

Purpose:

- prove that the perception path can accept a real camera
- not a claim of real UAV flight or real landing

#### Profile C — Gazebo SITL

Input:

- image stream from the simulated downward-facing camera
- vehicle state from PX4/Gazebo
- mission configuration

Purpose:

- closed-loop simulated landing or centering
- final evidence for the SITL profile

All source adapters must produce the same downstream observation schema.

### 3.1.5 Perception observation contract

The versioned observation sent to the controller must contain at least:

```json
{
  "schema_version": "1.0",
  "mission_id": "P1_A_FIXED_ARUCO_LANDING",
  "timestamp_capture_ns": 0,
  "timestamp_publish_ns": 0,
  "sequence_id": 0,
  "frame_id": 0,
  "source_type": "replay|webcam|gazebo",
  "target_found": true,
  "marker_dictionary": "DICT_4X4_50",
  "marker_id": 0,
  "center_px": {"x": 0.0, "y": 0.0},
  "error_px": {"x": 0.0, "y": 0.0},
  "normalized_error": {"x": 0.0, "y": 0.0},
  "pose_valid": true,
  "translation_camera_m": {"x": 0.0, "y": 0.0, "z": 0.0},
  "rotation_rvec": [0.0, 0.0, 0.0],
  "detection_latency_ms": 0.0
}
```

Contract rules:

- `timestamp_capture_ns` is the time associated with frame acquisition.
- `timestamp_publish_ns` is the time the observation leaves perception.
- `error_px.x > 0` means the marker center is to the right of the image center.
- `error_px.y > 0` means the marker center is below the image center.
- `normalized_error.x` and `.y` must use a documented normalization, preferably half-width and half-height, resulting approximately in `[-1, 1]`.
- Pose fields are invalid unless `pose_valid=true`.
- The controller must reject malformed, unsupported, out-of-order, or stale observations.
- The stale threshold is configuration-controlled; initial engineering target: `200 ms`.

### 3.1.6 Coordinate conventions

The project must document and test all transformations:

```text
Image frame:
+x right
+y down

OpenCV optical frame:
+x right
+y down
+z forward from camera

PX4 local NED:
+x North
+y East
+z Down

Vehicle body frame:
documented according to the selected PX4/MAVLink convention
```

The mapping must be explicit:

```text
image error
→ camera-relative correction
→ body/local-frame command
→ velocity or LANDING_TARGET-compatible message
```

A unit/integration test must detect sign mistakes such as commanding the UAV away from the marker.

### 3.1.7 Control output contract

```json
{
  "schema_version": "1.0",
  "mission_id": "P1_A_FIXED_ARUCO_LANDING",
  "timestamp_ns": 0,
  "source_sequence_id": 0,
  "controller_state": "INIT|SEARCH|ACQUIRE|ALIGN|HOLD_ALIGNMENT|DESCEND|FINAL_APPROACH|LAND|FAILSAFE",
  "vx_mps": 0.0,
  "vy_mps": 0.0,
  "vz_mps": 0.0,
  "yaw_rate_rps": 0.0,
  "command_valid": true,
  "failsafe_reason": "NONE"
}
```

Potential integration modes:

1. **LANDING_TARGET mode**
   - perception behaves as an external landing target sensor
   - sends target direction/position information to autopilot

2. **SET_POSITION_TARGET_LOCAL_NED mode**
   - external C++ controller computes bounded velocity setpoints
   - sends `vx`, `vy`, `vz`, and optionally yaw-rate

A message builder or field mapping is not evidence that a complete MAVLink flight loop has been achieved. Claims must match what was actually tested.

### 3.1.8 Landing state machine

Required states:

```text
INIT
→ SEARCH
→ ACQUIRE
→ ALIGN
→ HOLD_ALIGNMENT
→ DESCEND
→ FINAL_APPROACH
→ LAND
```

Error states and events:

```text
TARGET_LOST
STALE_OBSERVATION
WRONG_MARKER_ID
INVALID_POSE
IPC_TIMEOUT
CONTROL_SATURATION
LOW_LOOP_RATE
MALFORMED_PACKET
EMERGENCY_STOP
FAILSAFE
```

Minimum policy:

- never descend on stale or invalid observations
- require consecutive valid observations before acquisition
- require alignment to remain within a threshold for a hold period before descent
- continue horizontal correction during descent only within safe bounds
- reset or freeze PID integral on target loss according to configuration
- command zero/hold/abort behavior when observations time out
- log every state transition and its reason

Required transition table fields:

| State | Entry condition | Exit condition | Timeout | Command policy | Failure policy |
|---|---|---|---|---|---|

### 3.1.9 Official demo scenarios

#### DEMO_P1_A_01 — Nominal fixed-pad landing

- PX4 + Gazebo SITL
- downward-facing simulated camera
- ArUco `DICT_4X4_50`, ID 0
- initial horizontal offsets:
  - 0.5 m
  - 1.0 m
  - 2.0 m
  - diagonal offset
- output:
  - annotated video
  - state overlay
  - target error
  - control command
  - vehicle state
  - run metrics and CSV logs

#### DEMO_P1_A_02 — Temporary occlusion

Marker is hidden for a configured duration. The system must stop unsafe descent, enter the correct state, and recover or abort according to policy.

#### DEMO_P1_A_03 — Artificial delay

Injected perception/IPC delay tests stale-data rejection and failsafe reaction.

#### DEMO_P1_A_04 — Frame drop

Tests behavior under dropped observations and irregular timing.

#### DEMO_P1_A_05 — Wrong marker ID

A marker with another ID appears. It must never be accepted as the landing target.

### 3.1.10 Engineering targets

These are initial targets, not achieved results:

| Metric | Initial target |
|---|---:|
| Marker-mode vision loop | ≥ 15 FPS where hardware permits |
| Observation stale threshold | ≤ 200 ms |
| C++ control loop | stable 30–50 Hz |
| Final horizontal error in SITL | ≤ 0.50 m |
| Pixel-only final error fallback | ≤ 30 px |
| Overshoot | ≤ 25% |
| Settling time | ≤ 5–8 s |
| Recovery after 1 s occlusion | ≤ 2 s |
| Landing success | ≥ 8/10 across defined initial offsets |
| Unsafe descent after target invalidation | 0 events |
| Wrong-marker acceptance | 0 in the regression suite |

If a target is changed after measurement, the change must be recorded in a decision log with evidence.

### 3.1.11 Non-goals v1

- no landing on people, animals, or arbitrary objects
- no landing on a moving vehicle
- no moving landing pad
- no claim of outdoor robustness
- no claim of real UAV flight readiness
- no safety certification claim
- no claim of metric real-world accuracy without verified calibration
- no autonomous pursuit behavior

---

## 3.2 Mission P1-B — Single Ground-Vehicle Tracking

### 3.2.1 Problem statement

Detect, select, and maintain the identity of one ground vehicle in an aerial or UAV-like video while measuring lock, loss, recovery, jitter, and runtime behavior.

### 3.2.2 Mission scope

```yaml
mission_id: P1_B_SINGLE_VEHICLE_TRACKING
mission_superclass: vehicle
primary_demo_class: car
detector_classes:
  - car
  - van
  - truck
  - bus
```

The public VisDrone baseline may preserve all original classes for benchmark comparability. Mission filtering and mission metrics must use the documented vehicle class mapping. Remapping all vehicle classes into one class is a separate experiment and must not be mixed with original-class metrics.

### 3.2.3 Input profiles

#### Profile A — Held-out UAV-domain video

- UAVDT or VisDrone-VID sequence
- sequence not used for training or tuning
- easy/medium/hard challenge classification
- versioned sequence manifest

#### Profile B — Project adaptation video

- licensed UAV video
- Gazebo/synthetic video
- controlled high-angle custom capture with domain-gap note

#### Profile C — Replay/live adapter

- replay video is required
- webcam or Gazebo stream is optional
- RTSP is a future adapter, not a blocker

### 3.2.4 Processing pipeline

```text
Input adapter
→ detector
→ mission-class filter
→ target selector
→ tracker
→ lost/reacquisition policy
→ target-relative error
→ evaluator and artifact writer
```

The detector, target selector, and tracker must remain separate interfaces.

### 3.2.5 Default target-selection policy

```yaml
selection_policy: nearest_to_frame_center
primary_class: car
confidence_threshold: 0.40
lost_timeout_ms: 1000
manual_roi_supported: true
```

Acquisition:

1. retain mission-valid classes
2. apply confidence threshold
3. prefer the configured primary demo class
4. choose the candidate nearest the frame center
5. lock the selected target ID

After lock:

- do not switch targets solely because another detection has higher confidence
- preserve the selected identity through the tracker
- log every target switch

### 3.2.6 Reacquisition policy

A reacquisition candidate should satisfy configured constraints:

```yaml
reacquisition:
  same_class_required: true
  max_center_distance_px: configurable
  min_iou_with_prediction: configurable
  max_lost_duration_ms: 1000
  appearance_matching: optional
  automatic_target_switch_after_timeout: false
```

Required event log:

```text
timestamp
old_target_id
new_target_id
reason
candidate_count
lost_duration_ms
```

Manual ROI selection must be available for demonstrations where the operator wants to specify exactly which vehicle to track.

### 3.2.7 Tracking output contract

```json
{
  "schema_version": "1.0",
  "mission_id": "P1_B_SINGLE_VEHICLE_TRACKING",
  "timestamp_capture_ns": 0,
  "timestamp_publish_ns": 0,
  "frame_id": 0,
  "target_selected": true,
  "target_class": "car",
  "target_id": 0,
  "bbox_xyxy": [0.0, 0.0, 0.0, 0.0],
  "center_px": {"x": 0.0, "y": 0.0},
  "normalized_error": {"x": 0.0, "y": 0.0},
  "confidence": 0.0,
  "tracking_state": "ACQUIRING|LOCKED|OCCLUDED|LOST|REACQUIRED",
  "lost_duration_ms": 0,
  "inference_latency_ms": 0.0,
  "tracking_latency_ms": 0.0,
  "end_to_end_latency_ms": 0.0
}
```

### 3.2.8 Official demo scenarios

#### DEMO_P1_B_01 — Nominal single-car lock

- a held-out aerial sequence with multiple vehicles
- acquire the `car` nearest the frame center or use manual ROI
- display:
  - selected target
  - persistent ID
  - tracking state
  - normalized error
  - confidence
  - FPS
  - P50/P95 latency
  - switch count

#### Challenge scenarios

```text
DEMO_P1_B_02 partial occlusion
DEMO_P1_B_03 tiny target / high altitude
DEMO_P1_B_04 crowded traffic
DEMO_P1_B_05 motion blur / camera motion
DEMO_P1_B_06 target leaves and re-enters frame
DEMO_P1_B_07 negative sequence with no mission-valid target
```

### 3.2.9 Required metrics

- detector precision, recall, mAP50, mAP50-95
- AP/recall for small or tiny targets
- vehicle recall
- target-lock rate
- lost-frame rate
- target-switch count
- track fragmentation
- recovery time
- center jitter
- confidence distribution
- inference latency P50/P95
- end-to-end latency P50/P95
- FPS
- startup time
- CPU/RAM and GPU/VRAM where applicable
- failure-category report

Initial runtime targets:

| Metric | Target |
|---|---:|
| ONNX CPU FPS | minimum ≥ 10; stretch ≥ 15 |
| P95 inference latency | ≤ 100–150 ms |
| Batch size | 1 |
| Target-switch count | minimized and always reported |

Tracking quality thresholds must be finalized from the first evaluation baseline and stored in the mission configuration. They may not be invented after viewing the final test result.

### 3.2.10 Non-goals v1

- no person tracking
- no dog/cat or generic-object tracking
- no identity recognition
- no autonomous pursuit claim
- no landing on the tracked vehicle
- no test-set tuning
- no claim of real-world deployment from replay-only testing

---

## 3.3 Mission P2-A — UAV Video Stabilization and Tracking Impact Analysis

### 3.3.1 Problem statement

Given a shaky UAV or gimbal-like video, estimate camera motion, generate a stabilized version, and measure whether stabilization improves or harms tracking of the same vehicle target.

### 3.3.2 Primary question

```text
Does stabilization reduce camera-motion and target-center jitter enough
to justify its latency, crop, border artifacts, and failure modes?
```

### 3.3.3 Primary target

```text
car
```

The same detector, tracker, thresholds, target-selection policy, hardware, and source sequence must be used in before/after comparisons.

### 3.3.4 Input contract

Required input:

- MP4 video
- metadata file

Minimum metadata:

```yaml
video_id:
source:
license:
resolution:
fps:
duration_s:
camera_motion_level:
target_class: car
ground_truth_available:
split_role:
checksum:
```

### 3.3.5 Processing modes

```text
analyze-only
stabilize-only
compare-before-after
```

Pipeline:

```text
input video
→ feature detection
→ feature matching
→ transform estimation
→ trajectory generation
→ trajectory smoothing
→ warp/crop
→ stabilized video
→ tracking on original
→ tracking on stabilized
→ metric comparison
```

### 3.3.6 Run artifact contract

```text
runs/<RUN_ID>/
├── resolved_config.yaml
├── command.txt
├── environment.txt
├── input_manifest.yaml
├── camera_motion.csv
├── stabilization_transforms.csv
├── tracking_original.csv
├── tracking_stabilized.csv
├── metrics_original.json
├── metrics_stabilized.json
├── comparison.csv
├── original_overlay.mp4
├── stabilized_overlay.mp4
├── side_by_side.mp4
├── plots/
└── notes.md
```

### 3.3.7 Required metrics

Stabilization:

- camera trajectory jitter
- inter-frame transform variance
- residual motion
- crop ratio
- invalid-border ratio
- motion-estimation failure count
- processing FPS
- P50/P95 latency

Tracking:

- target-lock rate
- lost-frame rate
- recovery time
- target-center jitter
- bounding-box size jitter
- ID/target switches
- confidence distribution
- end-to-end FPS and latency

Initial engineering targets:

```text
jitter reduction ≥ 30%
tracking lost-rate reduction ≥ 20%
```

These are hypotheses/targets, not claims. A sequence where stabilization makes tracking worse must be preserved and explained.

### 3.3.8 Demo scenarios

```text
DEMO_P2_A_01 nominal shaky aerial vehicle video
DEMO_P2_A_02 motion blur
DEMO_P2_A_03 low-texture background
DEMO_P2_A_04 large camera rotation
DEMO_P2_A_05 target near image border
DEMO_P2_A_06 stabilization failure case
```

### 3.3.9 Non-goals

- no claim that software replaces a physical gimbal
- no hiding crop or border artifacts
- no claim that every video improves
- no claim of real-time operation without benchmark evidence
- no direct source-code coupling to Project 1
- no subjective visual-only conclusion

---

# 4. ML lifecycle contract for `edge-ai-training/`

## 4.1 Dataset tiers

### Tier 0 — Smoke test

Allowed:

```text
coco8.yaml
```

Rules:

- 1–3 epochs
- experiment prefix `SMOKE_`
- only validates environment and pipeline
- never used as a portfolio baseline
- metrics never presented as project performance

### Tier 1 — Public UAV-domain baseline

Preferred:

- VisDrone2019-DET for detection
- UAVDT or VisDrone-VID for video tracking evaluation

Rules:

- use official split where possible
- if resources require a subset, generate it reproducibly
- do not cherry-pick samples manually

### Tier 2 — Project-specific adaptation set

Target:

- 300–800 frames
- at least 5–10 distinct sequences
- sequence-aware split
- source and license recorded
- annotation guideline
- review pass
- separate held-out sequences

Sources in priority order:

1. official benchmark data
2. open-license video/image sources
3. Gazebo/synthetic data
4. custom capture
5. controlled crawling with license records

### Tier 3 — Held-out challenge set

Never used to train or tune.

Must include as available:

- high altitude / tiny target
- oblique camera
- motion blur
- partial occlusion
- crowded traffic
- low contrast
- camera motion
- target leaving and re-entering
- negative sequence

## 4.2 Dataset quality gate

A dataset version is not official until it has:

- source URL and license note
- citation where required
- immutable raw-data policy
- image/label pairing validation
- box-boundary and class-ID validation
- sample visualization
- annotation guideline
- sequence-aware split
- duplicate/near-duplicate check
- cross-split leakage check
- class distribution
- box-size distribution
- sequence count
- known limitations
- manifest and checksum

## 4.3 Required workspace structure

```text
edge-ai-training/
├── datasets/
│   ├── raw/
│   │   ├── visdrone/
│   │   ├── uavdt/
│   │   └── custom_sources/
│   ├── interim/
│   ├── processed/
│   │   └── uav_vehicle_v1/
│   └── manifests/
│       ├── DATASET_SOURCES.md
│       ├── DATASET_MANIFEST.json
│       ├── CLASS_MAPPING.md
│       ├── ANNOTATION_GUIDELINES.md
│       └── SPLIT_MANIFEST.csv
├── experiments/
│   ├── EXPERIMENT_REGISTRY.csv
│   ├── EXPERIMENT_TEMPLATE.md
│   └── EXP_*/
├── scripts/
│   ├── download_dataset.py
│   ├── extract_video_frames.py
│   ├── convert_annotations.py
│   ├── remap_vehicle_classes.py
│   ├── split_by_sequence.py
│   ├── audit_dataset.py
│   ├── detect_duplicates.py
│   └── visualize_labels.py
├── reports/
│   ├── error_analysis/
│   ├── dataset_audit_before_cleaning.md
│   ├── dataset_audit_after_cleaning.md
│   ├── dataset_cleaning_delta.csv
│   ├── runtime_benchmark.csv
│   ├── model_selection_matrix.csv
│   └── model_selection_decision.md
└── models/
```

## 4.4 Experiment registry fields

Every experiment must record:

```text
experiment_id
date
mission_id
purpose
parent_experiment
dataset_version
train_split
val_split
test_split
model
pretrained_weights
image_size
epochs
patience
batch
optimizer
learning_rate
augmentation_profile
seed
runtime
precision
status
best_epoch
mAP50
mAP50_95
precision_metric
recall_metric
vehicle_recall
AP_small
target_lock_rate
FPS
latency_p50_ms
latency_p95_ms
peak_ram_mb
peak_vram_mb
model_size_mb
artifact_path
decision
notes
```

## 4.5 Ablation rules

- change one major factor group per experiment
- preserve split and benchmark protocol
- identify the parent/baseline
- record failed experiments
- do not choose a model from one metric alone
- do not tune on the held-out test set
- do not call a one-seed result final
- do not run INT8 without a representative calibration set

Recommended sequence:

| ID | Main change | Purpose |
|---|---|---|
| EXP_001 | YOLO nano, 640, public UAV data | baseline |
| EXP_002 | higher image size | small-target recall |
| EXP_003 | augmentation profile | robustness |
| EXP_004 | larger model | capacity trade-off |
| EXP_005 | public → custom fine-tune | domain adaptation |
| EXP_006 | ONNX FP32 | runtime baseline |
| EXP_007 | FP16 where supported | runtime/precision trade-off |
| EXP_008 | INT8 if justified | edge optimization |
| EXP_009 | hard-negative mining | false-positive reduction |
| EXP_010 | hard-example fine-tuning | mission failure reduction |

Not every experiment is mandatory. A branch can be stopped with a documented decision and evidence.

## 4.6 Model promotion lifecycle

```text
SMOKE
→ BASELINE
→ CANDIDATE
→ VALIDATED_CANDIDATE
→ DEPLOYABLE
→ RETIRED
```

Promotion to `VALIDATED_CANDIDATE` requires:

- official dataset/split version
- held-out evaluation
- runtime benchmark
- failure analysis
- export smoke test
- baseline comparison
- no hard deployment constraint violation

Promotion to `DEPLOYABLE` requires:

- versioned model package
- Project 1 loading test
- preprocessing/postprocessing contract
- integrity checksum
- deployment benchmark
- model card
- clean handoff command

## 4.7 Deployable model package

```text
model.onnx
model_metadata.json
preprocessing.yaml
postprocessing.yaml
class_mapping.yaml
thresholds.yaml
benchmark_results.csv
MODEL_CARD.md
DATASET_VERSION.txt
export_command.txt
environment.txt
SHA256SUMS
```

Example filename:

```text
vehicle_yolo26n_visdrone_v1_640_onnx_fp32_v0.1.0.onnx
```

Do not use ambiguous release names such as:

```text
best.onnx
final.onnx
latest.onnx
```

## 4.8 Model selection

A model must pass hard constraints before ranking.

Initial hard constraints:

- batch size 1
- ONNX Runtime support
- CPU FPS ≥ 10
- P95 inference latency ≤ 150 ms
- no starvation of control/failsafe
- memory fits deployment hardware

Among passing candidates, rank:

1. mission vehicle recall
2. small-object performance
3. target-lock rate
4. P95 latency
5. memory and model size
6. mAP50-95

The decision must be stored in:

```text
reports/model_selection_matrix.csv
reports/model_selection_decision.md
```

---

# 5. Shared system architecture

```text
Replay / Webcam / Gazebo camera / UAV video
                    |
                    v
Python Perception Process
ArUco / pose / YOLO / target selector / tracker
                    |
                    | UDP target_observation v1
                    v
C++ Control Process
PID / state machine / failsafe / timing
                    |
                    | MAVLink-compatible command or command log
                    v
PX4 SITL / Gazebo / Hybrid SITL
                    |
                    v
Evaluation, artifacts, reports, demo
```

## 5.1 Default transport contract

Default v1:

```yaml
transport: udp
serialization: json_utf8
bind_address: 127.0.0.1
perception_to_control_port: 5600
control_status_port: 5601
heartbeat_hz: 10
observation_timeout_ms: 200
max_packet_size_bytes: 4096
```

Required behaviors:

- schema version validation
- sequence ID
- duplicate detection
- out-of-order rejection
- malformed-packet handling
- heartbeat timeout
- graceful shutdown
- bounded queue or latest-observation policy
- clear log codes

The roadmap may later replace JSON with a binary format, but v1 must remain inspectable and testable.

## 5.2 Configuration management

No production logic may hard-code:

- marker ID
- dictionary
- marker size
- camera index
- input path
- model path
- thresholds
- ports
- stale timeout
- PID gains
- output directory

Configuration requirements:

- YAML schema/version
- validation before execution
- resolved configuration saved per run
- unknown-field handling
- explicit defaults
- migration note when schema changes

## 5.3 Run artifact structure

Each meaningful run must create:

```text
runs/<MISSION_ID>/<RUN_ID>/
├── resolved_config.yaml
├── command.txt
├── environment.txt
├── git_commit.txt
├── input_manifest.yaml
├── events.log
├── metrics.json
├── frame_metrics.csv
├── outputs/
├── plots/
└── notes.md
```

Output directories must not be silently overwritten.

## 5.4 Logging fields

Logs should contain where applicable:

```text
timestamp
run_id
mission_id
schema_version
model_version
config_version
frame_id
sequence_id
pipeline_stage
state
latency
warning_code
error_code
```

## 5.5 Required error handling

- missing or corrupted input
- camera unavailable
- model load failure
- invalid config
- unsupported schema
- IPC disconnect
- stale observation
- out-of-order packet
- frame timeout
- failed pose estimation
- wrong marker ID
- disk write failure
- output-directory collision

---

# 6. Deployment profiles

| Profile | P1-A | P1-B | P2-A | Required evidence |
|---|---|---|---|---|
| Development source mode | Required | Required | Required | local command, logs, tests |
| Replay demo mode | Required | Required | Required | versioned input/config/output |
| Webcam bench mode | Required | Optional | Optional | disconnect handling; no flight claim |
| SITL integration mode | Required | Optional future | N/A | PX4/Gazebo or documented hybrid fallback |
| Containerized CPU replay | Required | Required | Required | Docker smoke test and mounted artifacts |

A profile is only called deployment-ready after its specific gate passes.

---

# 7. CLI and one-command demo contract

Representative Python commands:

```bash
python scripts/run_perception.py \
  --mission marker_landing \
  --source replay \
  --input videos/inputs/aruco_landing_replay.mp4 \
  --config configs/missions/fixed_aruco_landing_v1.yaml
```

```bash
python scripts/run_perception.py \
  --mission marker_landing \
  --source webcam \
  --camera-index 0 \
  --config configs/missions/fixed_aruco_landing_v1.yaml
```

```bash
python scripts/run_perception.py \
  --mission vehicle_tracking \
  --source replay \
  --input videos/inputs/uav_vehicle_tracking_01.mp4 \
  --config configs/missions/single_vehicle_tracking_v1.yaml
```

```bash
python scripts/run_analysis.py \
  --mode compare-before-after \
  --input videos/inputs/uav_shaky_vehicle_01.mp4 \
  --config configs/stabilization_v1.yaml
```

Final wrapper scripts:

```bash
bash scripts/run_demo_landing_replay.sh
bash scripts/run_demo_landing_sitl.sh
bash scripts/run_demo_vehicle_tracking.sh
bash scripts/run_demo_stabilization_comparison.sh
bash scripts/run_all_tests.sh
```

CLI requirements:

- `--help`
- meaningful exit codes
- config validation
- missing-input/model messages
- resolved-config capture
- command capture
- no absolute-path dependency
- no silent output overwrite

---

# 8. Expected repository outputs

## 8.1 Project 1

```text
edge-vision-uav-landing/
├── README.md
├── PROBLEM.md
├── REQUIREMENTS.md
├── TECHNICAL_DESIGN.md
├── MISSION_CONTRACTS.md
├── INTERFACE_CONTRACTS.md
├── DEPLOYMENT.md
├── TEST_PLAN.md
├── RESULTS.md
├── LIMITATIONS.md
├── MODEL_CARD.md
├── DATASET_MANIFEST.md
├── CLEAN_CLONE_TEST.md
├── PORTFOLIO_SUMMARY.md
├── Dockerfile
├── docker-compose.yml
├── configs/
│   ├── missions/
│   ├── schemas/
│   └── runtime/
├── src/
│   ├── perception/
│   ├── estimation/
│   ├── ipc/
│   ├── control_py/
│   ├── control_cpp/
│   ├── interface_cpp/
│   ├── edge/
│   ├── evaluation/
│   └── utils/
├── tests/
│   ├── python/
│   ├── cpp/
│   ├── contracts/
│   ├── replay/
│   └── integration/
├── scripts/
├── reports/
├── runs/
├── logs/
├── models/
└── videos/
```

## 8.2 Project 2

```text
gimbal-video-stabilization-analyzer/
├── README.md
├── PROBLEM.md
├── METHOD.md
├── MISSION_CONTRACT.md
├── DEPLOYMENT.md
├── TEST_PLAN.md
├── RESULTS.md
├── LIMITATIONS.md
├── configs/
├── src/
│   ├── stabilize.py
│   ├── motion_estimator.py
│   ├── trajectory_smoother.py
│   ├── track_quality.py
│   └── metrics.py
├── tests/
├── scripts/
├── runs/
├── reports/
└── videos/
```

---

# 9. Daily operating rules

Every day must produce:

1. at least one meaningful artifact
2. a verification result
3. a daily log
4. a decision for the next day
5. a truthful status of incomplete or failed work

Daily log template:

```md
# Day XX

## Mission served
- P1-A / P1-B / P2-A / ML / INFRA

## Done
- ...

## Evidence
- Commands:
- Files:
- Tests:
- Runs:

## Metrics
- FPS:
- P50/P95 latency:
- Error:
- CPU/RAM:
- Test pass/fail:

## Problems
- ...

## Decision
- Keep / cut / replace / fallback:

## Tomorrow
- Machine A:
- Machine B:
```

Rules:

- a checkbox is not sufficient evidence
- file existence is not sufficient evidence
- `best.pt` is not a complete experiment
- no metric means no measured claim
- failed runs are retained with a decision
- no empty commits
- no `git add .` for datasets/checkpoints
- no day transition when the gate is not satisfied or explicitly deferred

---

# 10. Day 5 production alignment

The roadmap consolidation occurs while Day 5 is reported as in progress. Work is preserved and aligned; it is not reset.

## 10.1 Preserve after evidence verification

Likely reusable artifacts:

- repository structure
- `VideoReader`
- ArUco detector
- camera calibration
- pose estimator
- Python PID
- control metrics
- replay source
- fault injection
- VisDrone training infrastructure
- experiment registry
- error analysis
- dataset audit

Only mark these confirmed after source/tests/logs/artifacts are verified.

## 10.2 Amend

- lock ArUco dictionary and ID
- add mission YAML
- add observation schema
- add control schema
- add coordinate convention
- choose UDP v1 transport
- add config validation
- normalize run artifacts
- align README demo scenario
- package/version model artifacts
- reconcile existing field names with schema v1

## 10.3 Catch-up tasks

### ALIGN_001 — Mission configuration

Create and validate:

```text
configs/missions/fixed_aruco_landing_v1.yaml
configs/missions/single_vehicle_tracking_v1.yaml
configs/schemas/
```

### ALIGN_002 — Interface and coordinate contracts

Create:

```text
MISSION_CONTRACTS.md
INTERFACE_CONTRACTS.md
src/ipc/target_observation_schema.md
```

### ALIGN_003 — Evidence reconciliation

Audit Day 1–5 artifacts and classify:

```text
confirmed
implemented but evidence incomplete
pending
blocked
superseded
```

### ALIGN_004 — Demo/readme scenario contract

Document exactly:

- landing target
- tracking target
- input command
- output artifacts
- engineering success criteria
- non-goals

### ALIGN_005 — ML package/version alignment

Ensure baseline and candidate artifacts have:

- experiment ID
- dataset version
- command
- config
- environment
- metrics
- model package name
- registry link

These tasks should be completed at the end of Day 5 or at the beginning of Day 6 before new cross-process tracking/control integration.

---

# 11. Detailed 30-day execution roadmap

## Day 01 — Scope, repository, requirements, and evidence rules

**Mission served:** `INFRA, P1-A, P1-B, ML`

### Machine A — Goal

Create the product skeleton and lock the original problem, requirements, risks, and proof strategy.

### Machine A — Deep-dive tasks

- Create/verify the workspace and Project 1 directory structure.
- Create `PROBLEM.md`, `REQUIREMENTS.md`, `TEST_PLAN.md`, `LIMITATIONS.md`, and the initial `TECHNICAL_DESIGN.md`.
- Record functional requirements for frame input, marker detection, target error, control, failsafe, logging, vehicle tracking, and runtime export.
- Record non-functional engineering targets for vision rate, control rate, stale-data behavior, reproducibility, and resource limits.
- Define the two separate Project 1 missions and prohibit landing on a moving tracked vehicle.
- Create the daily-log structure and initial risk register.

### Machine B — Goal

Create the ML workspace and document dataset/experiment provenance before training.

### Machine B — Deep-dive tasks

- Create/verify `edge-ai-training/` folders.
- Record GPU, driver, CUDA, PyTorch, Ultralytics, OS, CPU, and RAM.
- Create `DATASET_SOURCES.md`, `EXPERIMENT_TEMPLATE.md`, and `EXPERIMENT_REGISTRY.csv`.
- Define the mission class mapping and the Tier 0–3 dataset strategy.
- Do not start a portfolio baseline until dataset source, split, license, and experiment ID are documented.

### Inputs

Existing workspace, environment information, project objectives.

### Expected outputs

Repository skeleton, initial product documents, ML manifests and experiment registry.

### Acceptance criteria

Project names and folders are correct; requirements distinguish P1-A and P1-B; no unsupported production claim; daily evidence policy exists.

### Required evidence

File tree, Git diff/commit, environment record, Day 1 log.

### Fallback / blocker policy

If the existing repository already contains these files, update gaps rather than recreate duplicates.

---


## Day 02 — Video input adapters and ArUco detection

**Mission served:** `P1-A, INFRA, ML`

### Machine A — Goal

Build a reusable frame-source interface and detect the locked landing marker.

### Machine A — Deep-dive tasks

- Implement/verify `VideoReader` for file and webcam.
- Implement/verify `ArUcoDetector` using `DICT_4X4_50`.
- Accept the marker ID and dictionary from config; default mission target is ID 0.
- Draw corners, center, ID, image center, pixel error, detection state, latency, and source information.
- Log frame-level output with capture and publish timestamps.
- Add tests for correct ID, wrong ID, no marker, malformed frame, and end-of-video.
- Ensure downstream output can be adapted to observation schema v1.

### Machine B — Goal

Verify the ML environment and discover official UAV-domain data.

### Machine B — Deep-dive tasks

- Verify CUDA/PyTorch/Ultralytics.
- Document VisDrone and UAVDT sources, class lists, formats, official splits, and license/usage notes.
- Run only an optional `SMOKE_` experiment if environment validation is needed.
- Create the first dataset acquisition and audit plan.

### Inputs

Webcam/video and printed or synthetic ArUco examples; official dataset documentation.

### Expected outputs

Marker overlay video, detection CSV, source manifest, ML environment report.

### Acceptance criteria

Correct target ID is detected; wrong IDs are rejected; file/webcam adapters share an interface; smoke metrics are not labeled baseline.

### Required evidence

Test output, sample video, CSV, manifest, Day 2 log.

### Fallback / blocker policy

If webcam is unavailable, use a versioned replay input.

---


## Day 03 — Camera calibration, pose estimation, and UAV-domain baseline

**Mission served:** `P1-A, ML`

### Machine A — Goal

Add metric pose where valid and document calibration limitations.

### Machine A — Deep-dive tasks

- Implement/verify camera calibration using real checkerboard/Charuco data or clearly labeled synthetic intrinsics.
- Store camera matrix and distortion coefficients in `configs/camera.yaml`.
- Implement marker pose estimation and return `rvec`, `tvec`, and `pose_valid`.
- Compare pixel error and metric camera-frame displacement.
- Document the coordinate frame and the limitation of synthetic calibration.
- Add tests for missing calibration, invalid marker size, and pose failure.

### Machine B — Goal

Create the first reproducible portfolio detector baseline on UAV-domain data.

### Machine B — Deep-dive tasks

- Prepare or verify the VisDrone baseline experiment.
- Use `yolo26n` and an explicitly recorded image size, default 640.
- Preserve official splits or a reproducibly generated subset.
- Save command, resolved config, seed, environment, results, curves, checkpoint, and notes.
- Register `TRN_001` or the established baseline ID.
- Begin controlled comparison experiments only when parent/baseline relationships are recorded.

### Inputs

Calibration images/intrinsics, marker size, VisDrone dataset/version.

### Expected outputs

Calibration report, pose estimator, baseline experiment artifacts.

### Acceptance criteria

Pose is only reported as valid when calibration and estimation succeed; baseline is registered and reproducible; no `best.pt`-only completion.

### Required evidence

Calibration artifacts, pose tests, experiment registry, training run folder, Day 3 log.

### Fallback / blocker policy

Keep pixel-loop landing as a valid fallback while metric pose remains an engineering candidate.

---


## Day 04 — PID visual servoing offline and controlled ML comparisons

**Mission served:** `P1-A, ML`

### Machine A — Goal

Create a testable visual-centering controller before SITL integration.

### Machine A — Deep-dive tasks

- Implement/verify a two-axis Python PID controller.
- Required features: deadband, saturation, integral clamp/anti-windup, derivative filtering, first-sample derivative protection, `dt <= 0` handling, reset on target loss.
- Generate deterministic scenarios with step errors, disturbances, and target loss.
- Compute overshoot, settling time, steady-state error, saturation ratio, and update-time statistics.
- Add unit tests for sign, reset, saturation, anti-windup, and derivative behavior.

### Machine B — Goal

Compare controlled model or input-size candidates without changing multiple variables.

### Machine B — Deep-dive tasks

- Complete registered controlled comparisons such as image size or augmentation.
- Preserve the same split and benchmark protocol.
- Record accuracy, small-object performance, model size, and runtime where available.
- Do not call any candidate optimized or final.

### Inputs

Synthetic error trajectories, PID config, registered ML baseline.

### Expected outputs

PID module/tests/plots, controlled experiment logs.

### Acceptance criteria

PID tests pass; signs are documented; metrics are generated from known scenarios; ML comparisons identify exactly one main changed factor.

### Required evidence

Test report, plots/CSV, experiment registry, Day 4 log.

### Fallback / blocker policy

Use P-only or PI-safe settings as a diagnostic baseline when full PID tuning is unstable.

---


## Day 05 — Replay pipeline, fault injection, error analysis, and production alignment

**Mission served:** `P1-A, ML, INFRA`

### Machine A — Goal

Make the perception-control input reproducible under controlled faults and align prior work to mission contracts.

### Machine A — Deep-dive tasks

- Implement/verify replay source and fault injection.
- Supported faults: Gaussian noise, motion blur, occlusion, frame drop, artificial delay.
- Record fault configuration and seed.
- Log detection, latency, target validity, and injected-fault state.
- Complete `ALIGN_001` through `ALIGN_004` as evidence permits.
- Do not rewrite valid Day 1–4 modules solely because the schema was clarified; adapt with compatibility layers where practical.

### Machine B — Goal

Perform dataset audit and model failure analysis instead of blindly training.

### Machine B — Deep-dive tasks

- Create/verify before/after dataset-audit reports and cleaning delta.
- Categorize false positives/negatives, tiny targets, occlusion, blur, crowded scenes, domain gap, and negative sequences.
- Preserve the held-out test set.
- Do not move test failures directly into training; find or create equivalent train-pool examples.
- Complete `ALIGN_005` for experiment/model package provenance.

### Inputs

Versioned replay, fault config, current baseline outputs, dataset manifests.

### Expected outputs

Replay regression runs, fault logs, error-analysis report, audit delta, alignment documents.

### Acceptance criteria

Replay is config-driven; faults are reproducible; stale/invalid observations can be represented; Day 1–5 status is evidence-based.

### Required evidence

Run folder, fault config, audit reports, alignment plan/review, Day 5 log.

### Fallback / blocker policy

If Day 5 artifacts are incomplete, keep status `in progress` and carry only specific catch-up tasks into Day 6 preflight.

---


## Day 06 — Mission preflight, PX4/Gazebo setup, and adaptation-data pilot

**Mission served:** `P1-A, ML, INFRA`

### Machine A — Goal

Establish the SITL environment and finish mission/interface preflight before deeper integration.

### Machine A — Deep-dive tasks

- Complete remaining alignment tasks.
- Install/verify the compatible PX4 and Gazebo environment for the actual Ubuntu host.
- Start a quadrotor model and capture commands/logs proving SITL startup.
- Add or locate a downward-facing camera and the `landing_pad_aruco_id0` model if feasible.
- Create `SITL_SETUP.md` and `run_px4_sitl.sh`.
- Record camera topic/frame names and world/pad configuration.
- Validate coordinate and UDP contracts with schema tests.

### Machine B — Goal

Create a small, reviewed pilot adaptation set.

### Machine B — Deep-dive tasks

- Choose licensed/custom/synthetic source sequences.
- Extract 50–100 pilot frames using a reproducible command.
- Draft annotation guidelines and label the pilot.
- Review labels and revise rules.
- Create initial hard-negative and hard-example pools.

### Inputs

PX4/Gazebo environment, mission config, source videos.

### Expected outputs

SITL startup evidence, interface preflight tests, pilot annotations.

### Acceptance criteria

Gate A mission definition artifacts exist; SITL runs or a documented hybrid fallback is activated; pilot labels pass review.

### Required evidence

Setup document, command logs/screenshots, schema tests, pilot manifest, Day 6 log.

### Fallback / blocker policy

Use Hybrid SITL: replay vision plus PX4 state/offboard concept and MAVLink-compatible command log.

---


## Day 07 — Gate 1 foundation review and dataset v0.1 plan

**Mission served:** `P1-A, P1-B, ML, INFRA`

### Machine A — Goal

Prove the Week 1 foundation and remove ambiguity before closed-loop work.

### Machine A — Deep-dive tasks

- Create Week 1 report and a 30–60 second marker/PID/replay demo.
- Review marker detection, pixel error, pose behavior, PID, replay faults, mission config, schemas, and SITL/fallback.
- Add an early README quick start.
- Record every unmet item rather than force a pass.

### Machine B — Goal

Finalize annotation rules and the first adaptation-data version plan.

### Machine B — Deep-dive tasks

- Continue or complete the custom/synthetic adaptation set toward the planned size.
- Use sequence-based train/val/held-out splits.
- Audit the pilot/full set.
- Select only a provisional public baseline candidate.
- Do not call it final and do not skip later runtime validation.

### Inputs

Week 1 artifacts and test evidence.

### Expected outputs

`WEEK1_REPORT.md`, week-1 demo, gate checklist, dataset v0.1 plan/manifest.

### Acceptance criteria

Gate 1 passes or has explicit blocked/deferred items; wrong-marker and fault replay tests exist; public UAV baseline has reproducible evidence.

### Required evidence

Report, video, tests, registry, manifest, Day 7 log.

### Fallback / blocker policy

Proceed only with tasks whose dependencies are satisfied; do not hide gate failures.

---


## Day 08 — MAVLink design, landing state machine, and adaptation dataset freeze

**Mission served:** `P1-A, ML`

### Machine A — Goal

Turn landing behavior into a formal, testable state machine and MAVLink design.

### Machine A — Deep-dive tasks

- Create `MAVLINK_DESIGN.md`.
- Document LANDING_TARGET and SET_POSITION_TARGET_LOCAL_NED modes, fields, frames, rate requirements, and claim boundaries.
- Implement the Python reference state machine with the required production states.
- Create transition-table tests for valid acquisition, wrong ID, target loss, stale observation, hold-before-descent, and abort.
- Define descent gates and PID reset/freeze policy.

### Machine B — Goal

Freeze and audit the first project adaptation dataset version if ready.

### Machine B — Deep-dive tasks

- Complete the targeted 300–800 frame set when feasible.
- Freeze `uav_vehicle_custom_v0_1`.
- Store sequence-aware split, manifest, checksums, class and box-size distributions.
- If not ready, record a realistic completion state and do not fabricate the version.

### Inputs

Mission/interface contracts, pilot data.

### Expected outputs

MAVLink design, state-machine implementation/tests, dataset v0.1 artifacts.

### Acceptance criteria

No descent can occur on stale/invalid data in tests; each transition has a reason; dataset version is only declared when audit passes.

### Required evidence

State tests, design docs, dataset manifest/audit, Day 8 log.

### Fallback / blocker policy

Keep MAVLink as field mapping and command-log design if live send is not yet integrated.

---


## Day 09 — Closed-loop 2D landing simulation and domain-adaptation comparison

**Mission served:** `P1-A, ML`

### Machine A — Goal

Validate controller/state behavior in a deterministic closed-loop simulation before SITL landing.

### Machine A — Deep-dive tasks

- Build a 2D landing/centering simulator with configurable initial offsets, noise, delay, and disturbances.
- Run 0.5 m, 1.0 m, 2.0 m, and diagonal scenarios.
- Log target error, commands, state, saturation, overshoot, settling time, and final error.
- Validate coordinate signs and descent gates.
- Write `closed_loop_2d_v0.md`.

### Machine B — Goal

Compare public-only and public-to-custom candidates where the custom set is ready.

### Machine B — Deep-dive tasks

- Run/register a public baseline and a public→custom fine-tune.
- Do not train custom-only if the dataset is too small.
- Compare mission recall, small-object performance, and failure categories.
- Preserve the held-out test set.

### Inputs

PID/state config, simulation model, dataset versions.

### Expected outputs

Closed-loop simulation report and plots, domain-adaptation experiment comparison.

### Acceptance criteria

Controller converges in nominal cases without sign error; failures are categorized; ML comparison uses the same protocol.

### Required evidence

Simulation runs, report, experiment registry and artifacts, Day 9 log.

### Fallback / blocker policy

Use pixel-domain 2D control when pose-domain simulation is not reliable.

---


## Day 10 — UDP IPC schema, receiver prototype, and tracking evaluation harness

**Mission served:** `P1-A, P1-B, INFRA`

### Machine A — Goal

Make perception-to-control communication explicit and testable.

### Machine A — Deep-dive tasks

- Implement a Python UDP sender and reference receiver using observation schema v1.
- Add sequence, capture/publish timestamps, schema version, and heartbeat.
- Test malformed, duplicate, out-of-order, stale, delayed, and dropped packets.
- Define latest-observation or bounded-queue behavior.
- Measure local IPC latency P50/P95.
- Store the contract in `INTERFACE_CONTRACTS.md`.

### Machine B — Goal

Build the held-out multi-sequence tracking evaluation harness.

### Machine B — Deep-dive tasks

- Prepare at least 3 easy, 3 medium, and 3 hard sequences where available.
- Implement logs for target continuity, switches, fragmentation, lock, loss, recovery, center jitter, FPS, and P95 latency.
- Preserve both successful and failed videos.

### Inputs

Observation schema, UDP config, held-out sequences.

### Expected outputs

IPC sender/receiver tests and benchmark; tracking evaluation harness/manifests.

### Acceptance criteria

Receiver rejects stale and unsupported packets; IPC metrics are measured; tracking evaluation is sequence-aware.

### Required evidence

Contract tests, benchmark CSV, sequence manifest, Day 10 log.

### Fallback / blocker policy

Use loopback only for v1, but keep the transport configurable.

---


## Day 11 — Landing simulation v0.1 in SITL or Hybrid SITL

**Mission served:** `P1-A`

### Machine A — Goal

Connect marker observations and control behavior to the simulation environment.

### Machine A — Deep-dive tasks

- Run the landing/centering loop using the Gazebo camera if available.
- Otherwise run replay vision with PX4 state/offboard command logging in Hybrid SITL.
- Implement the pad model/config and the official initial-offset scenarios.
- Record state transitions, vehicle position, target error, and commands.
- Test marker loss during descent.
- Clearly distinguish full closed-loop SITL from hybrid evidence.

### Machine B — Goal

Evaluate active detector candidates on mission-specific validation/challenge data.

### Machine B — Deep-dive tasks

- Run batch inference on held-out and negative sequences.
- Update error analysis.
- Generate candidate comparison inputs for model selection.
- Do not promote a model solely from detector mAP.

### Inputs

SITL/hybrid setup, marker mission, detector candidates.

### Expected outputs

Landing simulation v0.1 video/run logs; candidate evaluation tables.

### Acceptance criteria

At least one honest landing/centering path runs; target loss inhibits unsafe descent; claim wording matches actual integration.

### Required evidence

Run artifacts, video, state/vehicle CSV, evaluation report, Day 11 log.

### Fallback / blocker policy

Keep Hybrid SITL and mark full camera bridge as future work.

---


## Day 12 — Robustness v0.1 and constrained-runtime baseline

**Mission served:** `P1-A, P1-B, ML`

### Machine A — Goal

Measure system degradation and failsafe behavior under faults and CPU limits.

### Machine A — Deep-dive tasks

- Run replay and SITL/hybrid tests with noise, blur, occlusion, delay, frame drop, and CPU restriction.
- Measure detection rate, P50/P95 latency, control rate, jitter, stale rejections, failsafe reaction, and recovery.
- Run concurrent perception/control to prove the controller remains alive.
- Create `robustness_v0_1.md`.

### Machine B — Goal

Benchmark runtime candidates under controlled conditions.

### Machine B — Deep-dive tasks

- Benchmark PyTorch and ONNX Runtime FP32 at batch size 1.
- Record machine, threads, precision, input size, startup time, FPS, P50/P95, RAM, and VRAM.
- Optionally benchmark OpenVINO when appropriate.
- Never use GPU training speed as the laptop edge-deployment result.

### Inputs

Fault profiles, CPU limit configuration, model candidates.

### Expected outputs

Robustness report, constrained-system logs, runtime benchmark.

### Acceptance criteria

Control/failsafe remains responsive; benchmark protocol is repeatable; all hardware/runtime fields are recorded.

### Required evidence

CSV/JSON metrics, plots, commands, Day 12 log.

### Fallback / blocker policy

If a runtime fails, preserve the failed attempt and continue with ONNX Runtime as the required baseline.

---


## Day 13 — Vehicle tracking mode, ONNX integration, and challenge evaluation

**Mission served:** `P1-B, ML`

### Machine A — Goal

Integrate a versioned detector package with target selection and tracking.

### Machine A — Deep-dive tasks

- Implement/verify YOLO/ONNX detector interface.
- Implement mission-class filtering and default target selection.
- Add manual ROI selection.
- Integrate a selected tracker candidate behind a stable interface.
- Implement lost/reacquisition policy and target-switch events.
- Produce a tracking demo video and end-to-end metrics.

### Machine B — Goal

Complete challenge evaluation and the first model-selection matrix.

### Machine B — Deep-dive tasks

- Evaluate public-only and adaptation candidates on easy/medium/hard sequences.
- Include negative sequences.
- Populate accuracy, mission recall, small-object, lock/recovery, runtime, memory, and size metrics.
- Draft model-selection decision; no final promotion before Gate 2.

### Inputs

Deployable-candidate model package, held-out videos.

### Expected outputs

`vehicle_tracking` mode, ONNX benchmark integration, tracking videos/metrics, selection matrix.

### Acceptance criteria

A single selected car remains locked according to policy; switches and failures are reported; model loads from versioned metadata/config.

### Required evidence

Run folders, videos, comparison tables, Day 13 log.

### Fallback / blocker policy

Use a simple tracker or detector-assisted nearest-prediction baseline if advanced tracking is unstable, while documenting limitations.

---


## Day 14 — Gate 2 integration review and validated candidate freeze

**Mission served:** `P1-A, P1-B, ML, INFRA`

### Machine A — Goal

Review closed-loop, state, robustness, IPC, tracking, and runtime evidence.

### Machine A — Deep-dive tasks

- Create `WEEK2_REPORT.md`.
- Produce week-2 landing/centering and vehicle-tracking videos.
- Verify the mission contracts, CLI plans, schemas, and current deployment matrix.
- Record missing evidence rather than forcing a pass.

### Machine B — Goal

Freeze a validated model candidate only if evidence permits.

### Machine B — Deep-dive tasks

- Complete model-selection matrix and decision.
- Export/package ONNX candidate.
- Save metadata, preprocessing, postprocessing, class mapping, thresholds, benchmark, model card draft, and checksums.
- Promote only to the lifecycle stage justified by evidence.

### Inputs

Week 2 reports/runs, model comparison.

### Expected outputs

Gate 2 review, videos, validated candidate package or explicit non-promotion decision.

### Acceptance criteria

Closed-loop simulation/hybrid path, state machine, robustness v0.1, IPC prototype, tracking mode, and ONNX benchmark are evidenced.

### Required evidence

Week report, gate checklist, package directory, registry, Day 14 log.

### Fallback / blocker policy

If the detector candidate is not validated, keep a baseline package and continue system work without falsely labeling it deployable.

---


## Day 15 — Architecture refactor, CMake skeleton, and model handoff

**Mission served:** `P1-A, P1-B, INFRA, ML`

### Machine A — Goal

Prepare the production-oriented Python/C++ split without breaking working behavior.

### Machine A — Deep-dive tasks

- Refactor perception, IPC, evaluation, and Python-reference control into stable modules.
- Create the C++17/CMake project structure.
- Add skeletons for PID, failsafe, receiver, control loop, and MAVLink message builder.
- Add contract fixtures shared by Python and C++ tests.
- Preserve compatibility wrappers where needed.

### Machine B — Goal

Perform the versioned model handoff to Project 1.

### Machine B — Deep-dive tasks

- Run integrity checks on the selected package.
- Install/copy it into `edge-vision-uav-landing/models/` through a documented script.
- Update the Project 1 model registry/config to an exact version.
- Run a Project 1 model-load smoke test.

### Inputs

Working Python modules, schema fixtures, model package.

### Expected outputs

Refactored architecture, CMake build, model handoff evidence.

### Acceptance criteria

C++ skeleton compiles; Python regression tests remain passing; model version is explicit and integrity-checked.

### Required evidence

Build log, tests, package checksum, Day 15 log.

### Fallback / blocker policy

Refactor incrementally and avoid a large rewrite that destroys verified Day 1–14 behavior.

---


## Day 16 — C++ PID controller and parity tests

**Mission served:** `P1-A`

### Machine A — Goal

Implement the required controller in C++ and compare it with the Python reference.

### Machine A — Deep-dive tasks

- Implement PID config and controller in C++.
- Include deadband, limits, anti-windup, derivative filtering, first-update handling, reset, and invalid-dt handling.
- Add unit tests for sign, zero error, saturation, anti-windup, reset, derivative behavior, and deterministic scenarios.
- Add Python-versus-C++ parity tests using shared CSV fixtures and tolerances.
- Benchmark update time per call.

### Machine B — Goal

Finalize detector metric tables and support chart generation.

### Machine B — Deep-dive tasks

- Consolidate accuracy/runtime results.
- Do not retrain unless a documented blocker requires it.
- Prepare charts for the Week 3 and final reports.

### Inputs

Python controller fixtures and C++ skeleton.

### Expected outputs

C++ PID library/tests/parity report.

### Acceptance criteria

All C++ tests pass; parity remains inside documented tolerance; update time supports the target control rate.

### Required evidence

CTest output, parity CSV/report, benchmark, Day 16 log.

### Fallback / blocker policy

If exact parity is impossible due to filtering/numeric differences, document a justified tolerance and behavior-level equivalence.

---


## Day 17 — C++ failsafe manager and landing state machine

**Mission served:** `P1-A`

### Machine A — Goal

Move safety-critical observation validation and state transitions into C++.

### Machine A — Deep-dive tasks

- Implement observation age checks, target-validity checks, wrong-ID handling, heartbeat timeout, and fail-safe reasons.
- Implement or port the required landing state machine.
- Define bounded outputs for each state.
- Test stale data, packet loss, target loss during descent, malformed values, saturation, and recovery.
- Measure failsafe reaction latency.

### Machine B — Goal

Support failure-case curation and report preparation.

### Machine B — Deep-dive tasks

- Organize representative failure examples without altering the held-out set.
- Update error categories and model limitations.

### Inputs

Interface contracts, state transition table, C++ PID.

### Expected outputs

C++ failsafe/state machine, tests, reaction-time report.

### Acceptance criteria

No stale observation produces a valid descent command; every failsafe event has a reason; reaction time is measured.

### Required evidence

CTest output, fault fixtures, reaction metrics, Day 17 log.

### Fallback / blocker policy

Use a conservative zero-velocity/abort policy when a recovery policy is not yet safely validated.

---


## Day 18 — C++ MAVLink-compatible bridge and message tests

**Mission served:** `P1-A`

### Machine A — Goal

Create testable LANDING_TARGET and velocity-setpoint message construction.

### Machine A — Deep-dive tasks

- Implement message data structures/builders for LANDING_TARGET and SET_POSITION_TARGET_LOCAL_NED modes.
- Document field mapping, coordinate frame, type masks, rates, and validity.
- Add serialization/field tests and golden fixtures.
- Add a command-log mode that works without live MAVLink transmission.
- Attempt SITL transmission only if dependencies and time permit.

### Machine B — Goal

Freeze ML artifacts unless a critical integration defect exists.

### Machine B — Deep-dive tasks

- Verify package metadata and checksums.
- Support only reproducible bug fixes, not exploratory scope expansion.

### Inputs

MAVLink design, control output contract.

### Expected outputs

C++ bridge/message builder, tests, command logs.

### Acceptance criteria

Field mappings are verified; mode differences are clear; live-send claim is only made if tested.

### Required evidence

Tests, command logs, design update, Day 18 log.

### Fallback / blocker policy

Retain message builder and command-log evidence if live MAVLink send is incomplete.

---


## Day 19 — Python perception to C++ control integration

**Mission served:** `P1-A, INFRA`

### Machine A — Goal

Run the required cross-process architecture end to end.

### Machine A — Deep-dive tasks

- Implement the C++ UDP receiver.
- Validate JSON/schema version and reject bad packets.
- Feed observations into C++ failsafe/state/PID.
- Emit control outputs and optional MAVLink-compatible messages.
- Add heartbeat, graceful shutdown, and process-launch scripts.
- Run replay success, delay, frame-drop, wrong-ID, and process-disconnect tests.
- Measure IPC and end-to-end timing.

### Machine B — Goal

Provide fixed test media and versioned model/config artifacts.

### Machine B — Deep-dive tasks

- Ensure integration inputs are checksum/versioned.
- Do not change model or thresholds between comparison runs without recording the change.

### Inputs

Python sender, C++ receiver/controller, replay inputs.

### Expected outputs

Hybrid Python+C++ pipeline, integration tests, timing report.

### Acceptance criteria

The C++ control process never trusts stale data; replay can drive end-to-end output; process failure causes a safe state.

### Required evidence

Integration logs, metrics, launch scripts, Day 19 log.

### Fallback / blocker policy

Use loopback UDP with command logging if SITL transmission is not available.

---


## Day 20 — CPU-limited hybrid stress test and A/B architecture benchmark

**Mission served:** `P1-A, P1-B, INFRA`

### Machine A — Goal

Prove the decoupled architecture remains safer under resource pressure.

### Machine A — Deep-dive tasks

- Compare Python-only reference and Python-perception+C++-control architectures.
- Apply CPU limits, artificial perception stalls, burst delay, and high logging load.
- Measure control rate, jitter P95, stale commands, failsafe reaction, perception FPS, end-to-end latency, CPU, and RAM.
- Verify control remains alive when perception slows.
- Write the A/B stress report.

### Machine B — Goal

Provide any batch inference required for fixed benchmark inputs.

### Machine B — Deep-dive tasks

- Reuse the frozen model/config.
- Generate charts but do not alter experiment conditions post hoc.

### Inputs

Both architectures, CPU-limit profiles.

### Expected outputs

A/B benchmark and stress-test report.

### Acceptance criteria

Hybrid control/failsafe behavior is measured and no unsupported superiority claim is made; failures are retained.

### Required evidence

Benchmark CSV, plots, commands, Day 20 log.

### Fallback / blocker policy

If the hybrid path performs worse, keep the result and identify queueing/logging/serialization bottlenecks.

---


## Day 21 — Project 2 stabilization v0.1 and Gate 3

**Mission served:** `P2-A, P1-A, INFRA`

### Machine A — Goal

Begin Project 2 without weakening the Project 1 C++ gate.

### Machine A — Deep-dive tasks

- Create the Project 2 repository skeleton and mission contract.
- Implement feature detection/matching, transform estimation, trajectory smoothing, warp/crop, and an initial side-by-side output.
- Run a small before/after tracking comparison using the same detector/tracker/config.
- Review Gate 3: C++ PID, failsafe, message builder, IPC, stress test, and Project 2 v0.1.

### Machine B — Goal

Batch-process initial Project 2 sequences and generate plots.

### Machine B — Deep-dive tasks

- Use versioned shaky video inputs with license metadata.
- Produce original/stabilized tracking metrics with identical model settings.

### Inputs

Project 2 input videos, frozen tracker/model, Project 1 Week 3 evidence.

### Expected outputs

Stabilization v0.1, first comparison, Gate 3 report.

### Acceptance criteria

Project 1 is no longer Python-only; Project 2 creates both video and metrics; comparison conditions are fair.

### Required evidence

Gate report, side-by-side video, run artifacts, Day 21 log.

### Fallback / blocker policy

If feature-based stabilization fails, preserve the failure and use a simpler affine baseline before adding complexity.

---


## Day 22 — Robustness test suite v1, regression corpus, and hard mining

**Mission served:** `P1-A, P1-B, P2-A, ML`

### Machine A — Goal

Turn ad-hoc tests into a repeatable cross-mission regression suite.

### Machine A — Deep-dive tasks

- Create automated replay cases for noise, blur, occlusion, frame drop, delay, wrong marker, stale packet, IPC loss, and target loss during descent.
- Add vehicle-tracking cases for occlusion, crowding, tiny target, re-entry, and no-target video.
- Add Project 2 cases for low texture, rotation, blur, and border/crop artifacts.
- Define pass/fail thresholds in config rather than code.

### Machine B — Goal

Perform controlled hard-negative and hard-example mining.

### Machine B — Deep-dive tasks

- Record source sequence, frame, failure category, model version, prediction, ground truth, and training decision.
- Add analogous examples from the train/custom pool rather than contaminating the held-out set.
- Register any follow-up experiment before running it.

### Inputs

Regression inputs, failure reports.

### Expected outputs

Robustness suite v1, regression manifests, hard-example manifests.

### Acceptance criteria

Tests can be rerun from commands/configs; challenge-set integrity remains intact; failures are visible.

### Required evidence

Test summary, manifests, artifacts, Day 22 log.

### Fallback / blocker policy

Prioritize required mission faults; defer exotic scenarios rather than making the suite unreliable.

---


## Day 23 — Technical design, contracts, and architecture evidence

**Mission served:** `INFRA, P1-A, P1-B, P2-A`

### Machine A — Goal

Document the system so a reviewer can understand every input, output, process, and claim boundary.

### Machine A — Deep-dive tasks

- Complete `TECHNICAL_DESIGN.md`.
- Complete `MISSION_CONTRACTS.md` and `INTERFACE_CONTRACTS.md`.
- Include architecture, sequence diagrams, schemas, coordinate transforms, state machine, deployment profiles, logging, errors, and fallback modes.
- Document the difference between full SITL, Hybrid SITL, replay, and webcam evidence.
- Link exact tests/runs to each major design claim.

### Machine B — Goal

Generate final architecture and benchmark figures.

### Machine B — Deep-dive tasks

- Create model comparison, latency, FPS, accuracy, memory, and failure-category charts.
- Ensure charts identify the machine/runtime/protocol.

### Inputs

Current implementation and reports.

### Expected outputs

Near-final technical documents and figures.

### Acceptance criteria

A new reviewer can answer what lands where, what is tracked, how data flows, and what was actually tested.

### Required evidence

Documents, diagrams, figure source data, Day 23 log.

### Fallback / blocker policy

Use text diagrams when polished graphics would delay evidence completion.

---


## Day 24 — Results report, model card, dataset manifest, and limitations

**Mission served:** `P1-A, P1-B, P2-A, ML`

### Machine A — Goal

Convert measured runs into an honest, traceable results report.

### Machine A — Deep-dive tasks

- Write `RESULTS.md` with environment, protocol, landing/control, robustness, architecture A/B, tracking, edge runtime, Project 2, errors, and limitations.
- Include tables for final error, overshoot, settling/recovery, latency, control jitter, target lock/loss/switches, runtime/memory, and stabilization trade-offs.
- Link every table to run artifacts/configs.
- Separate engineering targets from measured results.

### Machine B — Goal

Complete `MODEL_CARD.md` and `DATASET_MANIFEST.md`.

### Machine B — Deep-dive tasks

- Record intended use, classes, datasets, split, limitations, runtime, model version, and failure behavior.
- Ensure dataset version in the model card matches the registry/package.
- Include public-only versus adaptation comparison and test-set rules.

### Inputs

Measured reports and registries.

### Expected outputs

Results, model card, dataset manifest, limitation updates.

### Acceptance criteria

No value is invented; claims have evidence; failed cases are included; dataset/model versions are consistent.

### Required evidence

Documents, linked run IDs, Day 24 log.

### Fallback / blocker policy

Leave cells explicitly `not measured` rather than estimate.

---


## Day 25 — Docker, setup scripts, and reproducibility

**Mission served:** `INFRA, P1-A, P1-B, P2-A`

### Machine A — Goal

Make required replay profiles runnable without IDE-specific state.

### Machine A — Deep-dive tasks

- Create/update `Dockerfile`, `docker-compose.yml`, `setup.sh`, mission run scripts, and `run_all_tests.sh`.
- Support mounted input, config, model, and output directories.
- Validate CPU-only replay for P1-A, P1-B, and P2-A.
- Store environment and resolved config.
- Add deterministic/tolerance-based reproduction criteria.

### Machine B — Goal

Verify release-model paths and assemble release assets.

### Machine B — Deep-dive tasks

- Verify package checksums and model references.
- Prepare release folders for models, reports, configs, and sample inputs.

### Inputs

Stable commands, model packages, tests.

### Expected outputs

Docker/local setup, one-command tests, release asset structure.

### Acceptance criteria

No absolute path is required; missing assets produce clear errors; repeated runs are functionally equivalent within documented tolerances.

### Required evidence

Docker build/run logs, test summary, Day 25 log.

### Fallback / blocker policy

If full multi-service Docker blocks progress, deliver a reliable CPU replay container and a documented native SITL setup.

---


## Day 26 — Project 2 completion and multi-sequence comparison

**Mission served:** `P2-A`

### Machine A — Goal

Complete the stabilization analyzer as an independent measured product.

### Machine A — Deep-dive tasks

- Finalize motion estimator, smoothing, warp/crop, metric calculation, CLI, error handling, tests, README, METHOD, RESULTS, and LIMITATIONS.
- Report motion-estimation failures, crop, invalid borders, latency, FPS, and tracking changes.
- Ensure run artifact structure is complete.

### Machine B — Goal

Batch-evaluate 3–5 representative sequences.

### Machine B — Deep-dive tasks

- Include nominal and failure cases.
- Use the same detector/tracker/config before and after stabilization.
- Produce comparison CSV, plots, and side-by-side videos.

### Inputs

Versioned shaky videos and fixed tracking package.

### Expected outputs

Project 2 release candidate, reports and videos.

### Acceptance criteria

Conclusions include both benefits and costs; no hardware-gimbal replacement claim; failure cases are retained.

### Required evidence

Run folders, comparison report, videos, Day 26 log.

### Fallback / blocker policy

Release a truthful affine baseline with measured limitations rather than an unstable advanced method.

---


## Day 27 — Final one-command demos and demo script

**Mission served:** `P1-A, P1-B, P2-A, INFRA`

### Machine A — Goal

Create a reviewer-facing demonstration that shows products, evidence, and limitations.

### Machine A — Deep-dive tasks

- Finalize four wrapper scripts: landing replay, landing SITL/hybrid, vehicle tracking, stabilization comparison.
- Write `DEMO_SCRIPT.md` for a 3–5 minute video.
- Include problem, architecture, target definitions, inputs, state/failsafe, C++ path, runtime, Project 2, results, and limitations.
- Make success and failure cases visible.

### Machine B — Goal

Render final charts and media assets.

### Machine B — Deep-dive tasks

- Export README/demo images from measured data.
- Verify no chart mixes incompatible protocols.

### Inputs

Stable release-candidate builds and reports.

### Expected outputs

One-command demos, demo script, final media draft.

### Acceptance criteria

A reviewer can run or watch each mission without guessing the target/input; outputs and run IDs are visible.

### Required evidence

Script execution logs, demo draft, Day 27 log.

### Fallback / blocker policy

Use recorded deterministic demos when live SITL is too fragile, while labeling the profile honestly.

---


## Day 28 — README, deployment guide, and interview notes

**Mission served:** `INFRA, P1-A, P1-B, P2-A`

### Machine A — Goal

Make the portfolio understandable within minutes and defensible in an interview.

### Machine A — Deep-dive tasks

- Finalize Project 1 and Project 2 READMEs.
- Answer explicitly: where the drone lands, marker ID/size, what vehicle is tracked, how it is selected, where input comes from, how to run, what is measured, and what is not proven.
- Complete `DEPLOYMENT.md`.
- Create `INTERVIEW_NOTES.md` explaining design decisions and trade-offs.
- Link architecture, model card, results, limitations, and videos.

### Machine B — Goal

Review ML facts and charts for consistency.

### Machine B — Deep-dive tasks

- Check dataset/model version references.
- Stop training; only correct evidence/report inconsistencies.

### Inputs

Final docs and artifacts.

### Expected outputs

Near-final READMEs, deployment guide, interview notes.

### Acceptance criteria

No generic mission wording remains; commands are copyable; claims match evidence.

### Required evidence

Documentation review checklist, Day 28 log.

### Fallback / blocker policy

Prefer clear text and tables over decorative content.

---


## Day 29 — Clean-clone and external-review simulation

**Mission served:** `INFRA, P1-A, P1-B, P2-A`

### Machine A — Goal

Test the portfolio as a stranger with no local workspace state.

### Machine A — Deep-dive tasks

- Clone into a clean temporary location.
- Run setup, unit tests, contract tests, replay demos, and Docker CPU profiles.
- Verify config/model/input paths, download instructions, output structure, and failure messages.
- Test missing model/input/config behavior.
- Complete `CLEAN_CLONE_TEST.md`.

### Machine B — Goal

Verify checksums and release artifacts independently.

### Machine B — Deep-dive tasks

- Confirm model and dataset metadata.
- Back up the release package.
- Ensure large assets use an explicit download/release mechanism rather than hidden local paths.

### Inputs

Release candidate repository.

### Expected outputs

Clean-clone report and resolved defects.

### Acceptance criteria

Required replay demos and tests run from documented commands; no absolute paths or undeclared dependencies remain.

### Required evidence

Clean-clone logs, report, Day 29 log.

### Fallback / blocker policy

Document a reproducible native setup if Docker cannot cover SITL.

---


## Day 30 — Final release and evidence gate

**Mission served:** `P1-A, P1-B, P2-A, ML, INFRA`

### Machine A — Goal

Release two honest, measurable portfolio products.

### Machine A — Deep-dive tasks

- Finalize README, technical design, results, limitations, deployment, tests, and demo video.
- Create `PORTFOLIO_SUMMARY.md`.
- Tag `v1.0-portfolio` only after the final gate passes.
- List exact deployment-profile statuses: prototype, deployment candidate, or passed profile.
- Archive success and failure evidence.

### Machine B — Goal

Finalize model, experiment, dataset, benchmark, and checksum archives.

### Machine B — Deep-dive tasks

- Freeze the model registry and selected package.
- Preserve training logs and decisions.
- Export final chart sources and reports.

### Inputs

All gate evidence.

### Expected outputs

Final tagged release, portfolio summary, videos, reports, two project packages.

### Acceptance criteria

Clean clone passes; mission demos run; measured metrics and limitations are complete; unsupported production/real-flight claims are absent.

### Required evidence

Release checklist, tag/commit, artifact manifest, final Day 30 log.

### Fallback / blocker policy

Release as `production-oriented prototype v1.0` with explicit incomplete profile status rather than overclaim.

---

# 12. Quality gates

Gate status values:

```text
NOT_STARTED
IN_PROGRESS
BLOCKED
PASS
FAIL
PASS_WITH_DOCUMENTED_LIMITATION
```

## Gate A — Mission Definition and Alignment Gate

Target timing: end of Day 5 / Day 6 preflight.

Pass requirements:

- [ ] P1-A target is ArUco `DICT_4X4_50`, ID 0.
- [ ] Marker and pad dimensions are configured.
- [ ] P1-B primary demo target is `car`.
- [ ] Vehicle class mapping is documented.
- [ ] P2-A comparison mission is documented.
- [ ] Input profiles are defined.
- [ ] Observation and control schemas exist.
- [ ] Coordinate conventions exist.
- [ ] UDP v1 contract exists.
- [ ] Demo command contracts exist.
- [ ] Non-goals and claim boundaries exist.
- [ ] Day 1–5 evidence is reconciled.

## Gate 1 — Day 7: Foundation and replay product gate

System:

- [ ] marker detection
- [ ] correct/wrong ID tests
- [ ] pixel error
- [ ] pose estimator functional test
- [ ] Python PID tests
- [ ] replay and configured fault injection
- [ ] mission/config/schema alignment
- [ ] PX4/Gazebo startup or documented fallback

ML:

- [ ] no COCO8 portfolio baseline
- [ ] UAV-domain baseline
- [ ] experiment registry
- [ ] dataset source/license
- [ ] split integrity evidence
- [ ] metrics and failure examples
- [ ] custom/adaptation data plan

## Gate 2 — Day 14: Closed-loop, tracking, and ML deployment gate

- [ ] landing/centering simulation or honest Hybrid SITL
- [ ] landing state machine
- [ ] stale-data and target-loss behavior
- [ ] MAVLink design
- [ ] Python IPC prototype
- [ ] robustness v0.1
- [ ] CPU-limited baseline
- [ ] vehicle tracking on multiple held-out sequences
- [ ] lock/loss/recovery/switch metrics
- [ ] ONNX benchmark
- [ ] versioned candidate package
- [ ] public-only versus adaptation comparison where adaptation data is ready
- [ ] domain-gap limitations

## Gate 3 — Day 21: C++ and system integration gate

- [ ] C++ PID
- [ ] C++ failsafe/state machine
- [ ] C++ MAVLink-compatible message builder
- [ ] C++ UDP receiver
- [ ] Python perception → C++ control
- [ ] stale-message rejection
- [ ] CPU-limited stress test
- [ ] Python-only versus hybrid A/B metrics
- [ ] Project 2 stabilization v0.1 with metrics

## Gate 4 / Gate E — Day 30: Portfolio and deployment evidence gate

- [ ] clean clone
- [ ] documented replay commands
- [ ] one-command demos
- [ ] reports and measured metrics
- [ ] success and failure media
- [ ] limitations
- [ ] Docker CPU replay profile
- [ ] model package and registry
- [ ] dataset manifest and leakage checks
- [ ] two independent project packages
- [ ] no unsupported real-world or production claims

---

# 13. Optimization and evidence protocol

Before each optimization experiment, record:

```text
mission objective
baseline
single main changed factor
fixed factors
dataset/split version
hardware/runtime
hard constraints
expected metric
stop condition
```

Required quality metrics:

- mAP50
- mAP50-95
- precision
- recall
- mission vehicle recall
- per-class AP
- AP/sensitivity for small targets
- false positives on negative sequences
- false negatives on hard sequences
- target-lock rate
- recovery time

Required deployment metrics:

- batch size 1
- FPS
- mean/P50/P95 latency
- peak RAM and VRAM
- CPU utilization
- model size
- startup time
- concurrent control-loop jitter

Required before/after evidence:

```text
baseline
candidate
delta
constraint pass/fail
protocol
artifact paths
decision
```

A model or system is not “optimized” without a controlled baseline comparison.

Multi-seed validation is required before calling an ML candidate repeatable/final where training variance materially affects the decision.

---

# 14. Reproducibility definition

Do not require bit-for-bit “100% identical” output for GPU, simulation timing, codecs, or floating-point pipelines.

Required standard:

```text
same input + same config + same model + same documented environment
→ functionally equivalent output within defined tolerances
→ same acceptance pass/fail result
→ same artifact structure
```

Each report/demo must identify:

- command
- config version
- input version/checksum
- model version
- dataset version
- runtime/hardware
- seed where applicable
- Git commit
- output/run ID

---

# 15. Fallback plan

## PX4/Gazebo camera stream is not completed

Use Hybrid SITL:

- PX4/Gazebo proves vehicle environment/offboard concept
- replay vision produces observations
- C++ control produces MAVLink-compatible commands/logs
- report labels the limitation
- full camera bridge remains future work

## Live MAVLink transmission is incomplete

Keep:

- C++ message builder
- field mapping
- coordinate/frame design
- rate policy
- command logs
- tests

Do not claim live closed-loop PX4 flight.

## YOLO accuracy is weak

Keep:

- reproducible UAV-domain baseline
- public-to-custom comparison if valid
- failure analysis
- ONNX runtime evidence
- model-selection decision
- honest dataset/domain limitations

Do not compensate by using a smoke-test model.

## OpenVINO is unavailable

Keep:

- PyTorch and ONNX Runtime benchmark
- record OpenVINO attempt/failure
- do not allow it to block the project

## C++ MAVLink work threatens the schedule

Priority:

1. C++ PID
2. C++ failsafe/state machine
3. C++ timing/control loop
4. C++ UDP integration
5. MAVLink message mapping/log
6. live transmission only if time permits

## Project 2 advanced stabilization fails

Release a measured affine/feature-based baseline with failure cases rather than an unstable advanced method.

---

# 16. Priority classification

## Must-have

1. locked mission contracts
2. ArUco ID 0 marker landing perception
3. replay and fault injection
4. PID visual servoing
5. landing state machine and failsafe
6. 2D and SITL/Hybrid SITL centering/landing evidence
7. UAV-domain YOLO detector baseline
8. single-vehicle target selection/tracking
9. multi-sequence tracking metrics
10. ONNX CPU benchmark
11. C++ PID/failsafe/IPC path
12. technical design, results, limitations
13. one-command replay demos
14. clean clone
15. independent Project 2 with measured before/after output

## Should-have

1. full Gazebo camera bridge
2. live MAVLink send in SITL
3. OpenVINO benchmark
4. Docker Compose multi-service architecture
5. GitHub Actions
6. DVC or Git LFS workflow
7. MLflow experiment tracking
8. manual ROI target selection
9. multiple tracker comparison
10. Project 2 batch evaluation on 3–5 videos

## Could-have

1. LQR controller
2. ROS 2 full node/launch system
3. advanced multi-object tracking
4. INT8 quantization
5. web dashboard
6. advanced synthetic-data generation
7. moving landing pad
8. gimbal hardware integration

Must-have items cannot be displaced by could-have items.

---

# 17. PC GPU overnight protocol

Before starting an overnight run:

- select an existing registered experiment
- record experiment ID
- verify dataset and split version
- save command/resolved config
- verify disk space and output path
- record expected completion and stop condition

Next morning:

- inspect status/logs
- preserve failure information
- update registry
- store metrics and curves
- decide keep/drop/retry
- do not launch another run until the decision is documented

Recommended naming:

```text
EXP_001_yolo26n_visdrone_640_baseline
EXP_002_yolo26n_visdrone_highres
EXP_003_yolo26n_aug_profile
EXP_004_yolo26s_capacity
EXP_005_public_to_custom_v0_1
EXP_006_onnx_fp32_cpu
EXP_007_openvino_fp32_fp16
EXP_008_int8_only_if_justified
EXP_009_hard_negative
EXP_010_hard_example
```

Each experiment folder:

```text
experiments/EXP_XXX/
├── config.yaml
├── resolved_config.yaml
├── command.txt
├── environment.txt
├── results.csv
├── metrics.json
├── curves/
├── checkpoints/
├── exports/
└── notes.md
```

---

# 18. Claim-to-evidence rules

Do not use these claims without the corresponding evidence:

| Claim | Minimum evidence |
|---|---|
| production-ready | validated deployment profile, config/error handling, tests, deployment docs, clean clone |
| deployment-ready | exact runnable profile, versioned artifacts, benchmark, smoke/regression test |
| precision landing | fixed target, multiple initial offsets, final metric error, success rate, failure handling |
| stable tracking | lock/loss/recovery/switch/jitter metrics on multiple sequences |
| optimized model | controlled baseline/candidate comparison under the same protocol |
| real-time | measured P50/P95/FPS and control timing on named hardware |
| robust | challenge/fault tests and failure analysis |
| reproducible | command, config, environment, input/model/dataset version, artifact |
| stabilization improves tracking | identical before/after protocol plus latency/crop/artifact costs |
| final model | model-selection decision, runtime/system validation, package and registry |

Until those gates pass, use:

```text
production-oriented prototype
engineering target
deployment candidate
validated candidate
planned capability
```

---

# 19. Final portfolio evidence package

## Project 1 reviewer questions that README must answer

1. Where does the drone land?
2. Which marker dictionary, ID, and size are used?
3. Is the pad fixed or moving?
4. What object is tracked?
5. How is one vehicle selected when many exist?
6. What inputs are supported?
7. What command runs each demo?
8. What does the system output?
9. How are landing and tracking success measured?
10. What happens on target loss or stale data?
11. Which parts run in Python and C++?
12. Was full SITL, Hybrid SITL, replay, or webcam actually tested?
13. What is not proven?

## Project 2 reviewer questions

1. What video is accepted?
2. What type of shake is analyzed?
3. What target is tracked?
4. What stabilization method is used?
5. How is before/after comparison kept fair?
6. What are the crop, latency, and artifact costs?
7. When does stabilization fail?
8. What command reproduces the result?

## Final release deliverables

- two repositories/folders ready for review
- one 3–5 minute portfolio demo
- mission and interface contracts
- technical design
- results and robustness reports
- model card and dataset manifest
- versioned model package
- success and failure examples
- Docker/local setup
- clean-clone report
- portfolio summary
- honest limitation statement

---

# 20. Condensed timeline

```text
Day 01  Scope, repo, requirements, ML provenance
Day 02  Video reader, locked ArUco detection, dataset discovery
Day 03  Calibration, pose, UAV-domain baseline
Day 04  PID offline, controlled ML comparison
Day 05  Replay, fault injection, audit, production alignment
Day 06  Mission preflight, PX4/Gazebo, adaptation pilot
Day 07  Gate 1
Day 08  MAVLink design, state machine, dataset freeze
Day 09  Closed-loop 2D, domain adaptation
Day 10  UDP schema, receiver prototype, tracking evaluator
Day 11  SITL/Hybrid landing v0.1
Day 12  Robustness and CPU/runtime baseline
Day 13  Vehicle tracking and ONNX integration
Day 14  Gate 2 and candidate package
Day 15  Refactor, CMake, model handoff
Day 16  C++ PID
Day 17  C++ failsafe/state machine
Day 18  C++ MAVLink-compatible bridge
Day 19  Python-to-C++ IPC
Day 20  CPU stress and architecture A/B
Day 21  Project 2 v0.1 and Gate 3
Day 22  Robustness suite and hard mining
Day 23  Technical design and contracts
Day 24  Results, model card, dataset manifest
Day 25  Docker and reproducibility
Day 26  Project 2 completion
Day 27  One-command demos
Day 28  README, deployment, interview notes
Day 29  Clean clone
Day 30  Final release and evidence gate
```

---

# 21. Final destination

At Day 30, the portfolio should truthfully demonstrate:

```text
A simulated UAV can visually locate a fixed ArUco landing pad,
compute target-relative error, run a tested Python/C++ control path,
reject stale or invalid observations, and produce measurable
landing/centering evidence in SITL or a clearly documented Hybrid SITL profile.
```

```text
A versioned UAV-domain detector and tracker can select one car,
maintain and recover its target state across held-out aerial sequences,
and report accuracy, target-lock, failure, latency, and resource metrics.
```

```text
An independent stabilization analyzer can compare the same tracking pipeline
before and after video stabilization and report both improvements and costs.
```

The final portfolio is strong because it connects:

```text
data
→ perception
→ target selection
→ control
→ C++ systems
→ simulation
→ edge deployment
→ testing
→ evidence
→ honest limitations
```