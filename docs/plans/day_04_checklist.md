# Day 4 Manual Execution Checklist: PID Visual Servoing Offline & Resolution Ablation

## Phase 0 — Xác minh trạng thái
**Mục tiêu:** Đảm bảo Day 04 được triển khai trên nền tảng vững chắc và đúng hướng của ROADMAP.

- [x] **Đọc ROADMAP.md:** Kiểm tra lại lộ trình Day 04, xác nhận task "Resolution ablation" và "PID offline" là chính xác.
- [x] **Kiểm tra `TRN_001/args.yaml`:** Mở file `args.yaml` trong thư mục experiment của `TRN_001` (nếu đã có) để xem cấu hình thực tế đã chạy (ví dụ: `imgsz`, `batch`, `seed`).
- [x] **Xác minh source command:** Không bịa ra lệnh chạy cũ. Dùng lệnh `history | grep "yolo detect train"` trên PC GPU để tìm lại lệnh gốc của TRN_001 nếu thiếu.

## Phase 1 — Đóng evidence Day 03
**Mục tiêu:** Hoàn thiện các artifact còn thiếu của Day 03 mà không làm giả evidence.

💡 **Quyết định kiến trúc & Giải thích:**
- `COMMAND.txt` phải là lệnh thực tế đã chạy, không phải lệnh được phục dựng cảm tính (có thể dẫn đến sai lệch thông số ngầm).
- Chỉ training lại nếu evidence gốc đã bị mất hoàn toàn và model hiện tại không thể tái lập. Nếu `args.yaml` còn, nó chính là provenance vững chắc nhất.

- [x] **Tạo `COMMAND.txt` với provenance:** Lấy lệnh từ history hoặc dựa vào `args.yaml` để tạo file `COMMAND.txt` trong `edge-ai-training/experiments/TRN_001_visdrone_yolo11n_640`. (Ghi chú rõ bên trong nếu đây là lệnh được trích xuất lại từ `args.yaml`).
- [x] **Viết `NOTES.md` đầy đủ:** Ghi rõ bối cảnh (môi trường, seed, GPU dùng để train, thông số rút ra từ `args.yaml`).
- [x] **Kiểm tra curves và failure cases:** Đảm bảo YOLO đã tự sinh ra `results.png` và các ảnh `val_batch*.jpg`. Nếu có, xác nhận chúng đã tồn tại thay vì tự tạo giả.

## Phase 2 — Error contract và PID design
**Mục tiêu:** Định nghĩa rõ ràng đầu vào/đầu ra của PID Controller trước khi code.

💡 **Quyết định kiến trúc & Giải thích chi tiết:**
- **Tại sao tách Config ra YAML?** PID tuning (chỉnh thông số Kp, Ki, Kd) trong thực tế đòi hỏi việc thử sai (trial & error) liên tục ở hiện trường. Nếu hard-code vào Python, bạn sẽ phải mở code ra sửa liên tục, cực kỳ rủi ro. Dùng file `yaml` giúp bạn chỉnh sửa và reload nhánh điều khiển siêu tốc.
- **Error frame & sign (Quy ước dấu):** Nếu tâm camera lệch trái so với mục tiêu -> sai số `error_x` là DƯƠNG (mục tiêu nằm ở bên phải màn hình). Do đó, bộ PID phải xuất ra lệnh vận tốc `v_x` DƯƠNG (ra lệnh cho drone bay sang phải) để triệt tiêu sai số. Đây là nguyên lý "Negative Feedback" (Phản hồi âm) kinh điển trong điều khiển học.
- **Tại sao cần Deadband (Vùng chết)?** Khi drone lơ lửng sát mục tiêu, nhiễu camera (pixel jitter) sẽ liên tục tạo ra sai số nhỏ ảo (VD: lệch 1-2 cm liên tục). Nếu không có vùng chết (`deadband=0.05` mét), PID sẽ liên tục gửi lệnh nhích trái/phải cực nhỏ khiến drone bị "run rẩy" (chattering), làm tốn pin và cháy motor.
- **Tại sao cần Alpha (Low-pass filter)?** Đạo hàm (Khâu D) đo tốc độ thay đổi của lỗi, nên nó vô cùng nhạy cảm với nhiễu. Việc nhân `alpha=0.5` vào khâu D giúp bộ lọc thông thấp (Low-pass filter) làm mượt sự giật cục của dữ liệu đầu vào.

- [x] **[Machine A] Thao tác 1:** Mở Terminal trên Laptop, di chuyển vào thư mục dự án C++ và tạo file config:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
touch configs/pid_config.yaml
```
- [x] Mở file `edge-vision-uav-landing/configs/pid_config.yaml` và copy chính xác nội dung sau vào:
```yaml
pid_x:
  kp: 1.2
  ki: 0.0
  kd: 0.1
  v_max: 1.5
  deadband: 0.02
  alpha: 0.5
pid_y:
  kp: 1.2
  ki: 0.0
  kd: 0.1
  v_max: 1.5
  deadband: 0.02
  alpha: 0.5
```

## Phase 3 — PID implementation và unit tests
**Mục tiêu:** Cài đặt bộ điều khiển PID an toàn, xử lý triệt để các edge cases quan trọng.

💡 **Quyết định kiến trúc & Giải thích chi tiết:**
- **Tại sao khâu D ở frame đầu tiên lại nguy hiểm (First-sample derivative)?** Ở chu kỳ điều khiển đầu tiên, `prev_error` mặc định là 0. Nếu mục tiêu xuất hiện cách 10 mét, phép tính đạo hàm `(10 - 0) / dt` (ví dụ `dt = 0.05s`) sẽ tạo ra một vận tốc ảo khổng lồ (200m/s). Khâu D sẽ nhân số này lên và ra lệnh cho drone phóng đi với tốc độ tối đa một cách vô lý. Do đó, phải có cờ `is_first_run` để tắt khâu D ở nhịp đầu tiên!
- **Tại sao cần Anti-windup tích hợp Unwind?** Nếu có gió thổi mạnh đẩy drone ra xa, khâu P và D bị bất lực, khâu I (Integral) sẽ cộng dồn sai số qua thời gian đến mức khổng lồ (Windup). Khi gió ngừng, cục I khổng lồ này sẽ đẩy drone bay vọt lố qua mục tiêu. Giải pháp: Ngừng cộng dồn I khi vận tốc bị bão hòa (Clamping). Nhưng cao cấp hơn, nếu mục tiêu đổi hướng làm sai số đảo chiều, ta phải cho phép cục I này xả ngược lại (Unwind) để drone phanh kịp thời.
- **Tại sao phải Reset khi mất mục tiêu (Target loss)?** Khi camera không nhìn thấy mục tiêu, mọi giá trị cũ (Integral, prev_error) trở thành rác. Nếu không gọi hàm `reset()`, khi bắt lại được mục tiêu, cục rác này sẽ tàn phá phép tính mới gây giật lag.

- [ ] **[Machine A] Thao tác 2:** Mở Terminal, tạo thư mục code Python cho hệ thống điều khiển và file PID:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
mkdir -p src/control_py
touch src/control_py/__init__.py
touch src/control_py/pid_controller.py
```
- [x] Chèn nội dung code chuẩn mực sau vào file `edge-vision-uav-landing/src/control_py/pid_controller.py`:
```python
class PIDController:
    def __init__(self, kp, ki, kd, v_max, deadband=0.05, alpha=0.5):

        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.v_max = v_max
        self.deadband = deadband
        self.alpha = alpha
        self.reset()

    def reset(self):
        """Gọi khi target loss để xóa memory, tránh vọt lố khi bắt lại mục tiêu."""
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_derivative = 0.0
        self.is_first_run = True

    def compute(self, error, dt):
        if dt <= 0.0:
            return 0.0

        # Deadband policy
        if abs(error) < self.deadband:
            error = 0.0

        p_term = self.kp * error

        # First-sample derivative handling
        if self.is_first_run:
            raw_derivative = 0.0
            self.is_first_run = False
        else:
            raw_derivative = (error - self.prev_error) / dt

        # Low-pass filter cho đạo hàm
        derivative = self.alpha * raw_derivative + (1 - self.alpha) * self.prev_derivative
        d_term = self.kd * derivative

        # Anti-windup (Clamping với unwind support)
        pre_cmd = p_term + d_term + self.ki * (self.integral + error * dt)
        
        # Chỉ cộng dồn I nếu hệ thống chưa bị bão hòa, 
        # HOẶC nếu lỗi đang có xu hướng kéo hệ thống ra khỏi bão hòa (đảo chiều)
        if abs(pre_cmd) < self.v_max or (pre_cmd > 0 and error < 0) or (pre_cmd < 0 and error > 0):
            self.integral += error * dt

        i_term = self.ki * self.integral

        cmd = p_term + i_term + d_term
        
        # Saturation
        cmd_clamped = max(-self.v_max, min(self.v_max, cmd))

        self.prev_error = error
        self.prev_derivative = derivative

        return cmd_clamped
```

- [x] **[Machine A] Thao tác 3:** Khởi tạo file Unit Test để mô phỏng lại các lỗi nguy hiểm vừa nêu:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
touch tests/python/test_pid_controller.py
```
- [x] Chèn nội dung sau vào `edge-vision-uav-landing/tests/python/test_pid_controller.py`:
```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.control_py.pid_controller import PIDController

def test_first_sample_derivative():
    pid = PIDController(1.0, 0.0, 1.0, 5.0)
    cmd = pid.compute(10.0, 0.1) 
    # Khâu D phải được xử lý cẩn thận ở lần chạy đầu tiên, cmd = P = 10 -> clamp về 5.0
    assert cmd == 5.0

def test_reset_and_target_loss():
    pid = PIDController(1.0, 1.0, 0.0, 5.0)
    pid.compute(1.0, 0.1)
    pid.reset()
    assert pid.integral == 0.0
    assert pid.is_first_run == True

def test_invalid_dt():
    pid = PIDController(1.0, 0.0, 0.0, 5.0)
    assert pid.compute(1.0, 0.0) == 0.0
    assert pid.compute(1.0, -0.1) == 0.0

def test_anti_windup_unwind():
    pid = PIDController(1.0, 1.0, 0.0, 1.5)
    # Gây bão hòa dương liên tục
    for _ in range(50):
        pid.compute(2.0, 0.1)
    
    # Lỗi đảo dấu -> I phải được xả (unwind) thay vì kẹt
    cmd = pid.compute(-0.5, 0.1)
    assert cmd < 1.5 # Không bị kẹt mãi ở v_max
```
- [x] **[Machine A] Thao tác 4:** Mở Terminal (Machine A), kích hoạt môi trường ảo và chạy lệnh `pytest`:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
source ../.venv/bin/activate
pytest tests/python/test_pid_controller.py
```
*(Yêu cầu: Xác minh 100% test màu xanh - PASS).*

## Phase 4 — Metrics và offline harness
**Mục tiêu:** Sinh ra framework đánh giá (harness) định lượng và tạo output machine-readable chuẩn mực.

💡 **Quyết định kiến trúc & Giải thích chi tiết:**
- **Tại sao phải giả lập Offline (Offline harness)?** Chạy thử PID thật trên UAV rất nguy hiểm và tốn kém (hỏng cánh quạt, rớt drone). Bằng cách viết một script giả lập vật lý đơn giản (Kinematics bậc 1), ta có thể đẩy hàng trăm kịch bản (scenario) thử nghiệm vào thuật toán PID để xem nó có bị vọt lố hay không chỉ trong vài giây.
- **Overshoot (Độ vọt lố) là gì?** Khi drone bay đến điểm 0, do quán tính nó sẽ bay lố qua điểm 0 (VD: trượt tới mức -0.5m) rồi mới vòng lại. Nếu độ vọt lố quá 25% (Overshoot > 25%), drone có thể văng ra khỏi bãi đáp. Thuật toán đo Overshoot phải bắt được điểm cực đại/cực tiểu (peak) thực sự sau khi đi qua 0.
- **Settling Time (Thời gian hội tụ) là gì?** Là thời gian kể từ lúc bắt đầu cho đến khi drone nằm hoàn toàn và vĩnh viễn trong vùng `deadband` (ổn định để chuẩn bị hạ độ cao). Nếu mất quá 5 giây (Settling Time > 5.0s), drone sẽ lơ lửng quá lâu, cạn pin trước khi hạ cánh xong.

- [x] **[Machine A] Thao tác 5:** Tạo file chứa các hàm đo lường toán học:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
touch src/evaluation/control_metrics.py
```
- [x] Chèn nội dung sau vào `edge-vision-uav-landing/src/evaluation/control_metrics.py`:
```python
import numpy as np

def calculate_overshoot(history_x, target=0.0):
    if not history_x: return 0.0
    initial = history_x[0]
    if initial == target: return 0.0
    
    # Nếu đi từ dương về 0, lố là phần âm sâu nhất. Ngược lại.
    if initial > target:
        min_val = min(history_x)
        if min_val >= target: return 0.0
        return abs(min_val - target) / abs(initial - target) * 100.0
    else:
        max_val = max(history_x)
        if max_val <= target: return 0.0
        return abs(max_val - target) / abs(initial - target) * 100.0

def calculate_settling_time(history_x, dt, target=0.0, threshold=0.05):
    for i in range(len(history_x)-1, -1, -1):
        if abs(history_x[i] - target) > threshold:
            if i == len(history_x) - 1: return float('inf') # Không hội tụ
            return (i + 1) * dt
    return 0.0
```

- [x] **[Machine A] Thao tác 6:** Tạo script chạy giả lập hệ thống hạ cánh và xuất báo cáo:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
touch scripts/simulate_pid_offline.py
```
- [x] Chèn đoạn code đã được refactor chuẩn mực vào `edge-vision-uav-landing/scripts/simulate_pid_offline.py`:
*(Sử dụng bản update với Type Hint, main guard, lưu samples và bộ thông số PID đã Tuning thành công: Kp=1.2, Kd=0.1).*
- [x] **[Machine A] Thao tác 7:** Chạy Terminal lệnh giả lập:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
source ../.venv/bin/activate
python scripts/simulate_pid_offline.py
```
*(Yêu cầu: Xác minh file `reports/pid_simulation_summary.csv` được sinh ra thành công và các kịch bản đều đạt trạng thái `PASS`).*

## Phase 5 — GPU ablation song song
**Mục tiêu:** Thực hiện thí nghiệm thay đổi độ phân giải (Resolution) một cách khoa học.

💡 **Quyết định kiến trúc & Giải thích chi tiết:**
- **Tại sao chọn Resolution Ablation (Tăng độ phân giải)?** Ở cuối Day 03, bản báo cáo `labels.jpg` chỉ ra 90% đối tượng trong VisDrone là vật thể siêu nhỏ (Tiny Objects). Tăng độ phân giải ảnh đầu vào (từ 640 lên 960) là phương pháp vật lý "thô bạo" nhưng cực kỳ hiệu quả giúp giữ lại chi tiết pixel của các vật thể nhỏ xíu này không bị xóa sổ khi đi qua các mạng chập (Conv layers).
- **Cạm bẫy của Auto-batch (Auto-batch confounder):** Ultralytics có tính năng cực hay là `batch=-1` (tự tìm batch size lớn nhất nhét vừa VRAM). Ở bản 640px hôm qua, batch size tự động tính ra có thể là 16. Nhưng nếu lên 960px (ảnh nặng hơn), batch tự động sẽ bị ép giảm xuống 8.
  - **Hệ lụy:** Khi so sánh 2 model (640px vs 960px), bạn không biết sự khác biệt độ chính xác mAP đến từ việc tăng Resolution hay do bị giảm Batch Size (Batch size quá nhỏ làm nhiễu đạo hàm Gradient).
  - **Giải pháp:** Bắt buộc phải tìm ra Batch Size thực tế của bản 640px, sau đó khóa cứng thông số này (Fixed batch) khi train bản 960px. Nếu máy bị "Tràn bộ nhớ" (Out of Memory - OOM), đành chấp nhận giảm Batch nhưng phải GHI CHÚ CHỮ TO vào báo cáo khoa học.

- [x] **[Machine B] Thao tác 8:** Kiểm tra file `edge-ai-training/experiments/TRN_001_visdrone_yolo11n_640/args.yaml`, tìm dòng `batch:` để xem con số thực tế hôm qua nó tính ra là bao nhiêu (VD: 8, 16...).
- [x] **[Machine B] Thao tác 9:** Mở Terminal trên PC GPU, di chuyển vào thư mục AI và chạy lệnh Train với `imgsz=960`, chốt cứng con số batch vừa tìm được (Ví dụ: `batch=16`). Nếu báo lỗi OOM, giảm xuống `batch=8` và ghi chú lại:
```bash
cd ~/Projects/edge-vision-precision-landing/edge-ai-training
source ../.venv/bin/activate
yolo detect train data=VisDrone.yaml model=yolo11n.pt epochs=30 patience=10 imgsz=960 batch=8 device=0 seed=42 deterministic=True cache=disk project=experiments name=TRN_002_visdrone_yolo11n_960
```
- [ ] **[Machine B] Thao tác 11:** Trong lúc máy Train, đi uống cà phê. Sau khi xong, thu thập `results.csv` của cả 2 bản để xuất báo cáo so sánh vào `edge-ai-training/reports/resolution_ablation_v0.md`.

## Phase 6 — Documentation và Git
**Mục tiêu:** Lưu trữ kết quả chính xác, không "fake" log và tuân thủ nguyên tắc "Git clean".

- [ ] **[Cả 2 Machine] Điền `daily_logs/day_04.md` bằng KẾT QUẢ THẬT:**
Chỉ tạo file log theo template và chừa trống mục Metrics/Done. Chờ cho đến khi script chạy xong mới điền. (Tuyệt đối không dùng log để tuyên bố kết quả chưa diễn ra).
```bash
cd ~/Projects/edge-vision-precision-landing/edge-vision-uav-landing
touch daily_logs/day_04.md
```
```md
# Day 04: PID Visual Servoing & Resolution Ablation

## Done
- [ ] Cài đặt PID với anti-windup (unwind), first-sample handling, reset function.
- [ ] Hoàn thiện `control_metrics.py` đo overshoot/settling time.
- [ ] Xuất `pid_simulation_summary.csv` cho 3 kịch bản offset.

## Metrics
- PID Settling Time: 2.05s - 4.05s (Rất nhanh, đạt chuẩn < 5.0s)
- PID Overshoot: 0.0% (Critically Damped tuyệt đối)

## Problems
- Auto-batch (`batch=-1`) làm nhiễu kết quả ablation giữa TRN_001 và TRN_002 do batch size tự động co giãn theo imgsz. Cần lưu ý trong so sánh.
```

- [ ] **Cập nhật `next_action_plan.md`:** Thêm task chuẩn bị cho Day 05 (Replay mode + Fault injection).
- [ ] **Kiểm tra Evidence:** Đảm bảo `pid_simulation_summary.csv` và `COMMAND.txt` (nếu có bổ sung) thực sự tồn tại trên disk.
- [ ] **Kiểm tra Git:** Đảm bảo đang đứng ở root repository tổng:
```bash
cd ~/Projects/edge-vision-precision-landing
git status
```
- [ ] **Review staged diff:** `git diff --staged` để chắc chắn không vô tình add file rác.
- [ ] **Commit an toàn:** Sau khi Quality Gate pass, thực hiện commit:
```bash
git add edge-vision-uav-landing/src/ edge-vision-uav-landing/tests/ edge-vision-uav-landing/scripts/ edge-vision-uav-landing/reports/ edge-vision-uav-landing/daily_logs/
git commit -m "day04: offline PID simulation framework and test scenarios"
```

---
*Kết luận cuối:* Checklist này đóng vai trò như bản đặc tả hệ thống chặt chẽ cho Day 04, sửa chữa các lỗ hổng lý thuyết của hệ thống PID và Ablation để đảm bảo evidence thu được là đáng tin cậy.
