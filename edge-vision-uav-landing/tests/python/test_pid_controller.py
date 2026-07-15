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