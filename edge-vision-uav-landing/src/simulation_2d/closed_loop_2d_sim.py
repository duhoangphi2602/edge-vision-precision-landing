import time
import csv
import sys
import os

# Thêm đường dẫn để import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.control_py.pid_controller import PIDController
from src.control_py.landing_state_machine import LandingStateMachine, LandingState

def run_simulation(initial_x, initial_y, duration=10.0, dt=0.033):
    pid_x = PIDController(kp=1.0, ki=0.01, kd=0.1, v_max=1.0)
    pid_y = PIDController(kp=1.0, ki=0.01, kd=0.1, v_max=1.0)
    sm = LandingStateMachine(stale_timeout=0.2)
    
    x, y = initial_x, initial_y
    current_time = 0.0
    
    log_data = []
    
    while current_time < duration:
        # Giả lập perception (quan sát thấy mục tiêu)
        obs = {
            "target_found": True,
            "error_x": x, # Trong thực tế, error là độ lệch tọa độ
            "error_y": y
        }
        
        # Cập nhật State Machine
        state = sm.update(current_time, obs)
        
        # PID Tính toán (Chỉ di chuyển khi state cho phép)
        vx, vy = 0.0, 0.0
        if state in [LandingState.ALIGN, LandingState.HOLD_ALIGNMENT, LandingState.DESCEND]:
            # Điều khiển triệt tiêu error
            vx = -pid_x.compute(x, dt)
            vy = -pid_y.compute(y, dt)
            
        # Cập nhật tọa độ (Vận tốc = quãng đường / thời gian => dx = vx * dt)
        x += vx * dt
        y += vy * dt
        
        log_data.append({
            "time": round(current_time, 3),
            "x": round(x, 4),
            "y": round(y, 4),
            "vx": round(vx, 4),
            "vy": round(vy, 4),
            "state": state.name
        })
        
        current_time += dt
        
    return log_data

def save_csv(filename, data):
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["time", "x", "y", "vx", "vy", "state"])
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    os.makedirs("edge-vision-uav-landing/reports/", exist_ok=True)
    
    scenarios = [
        ("0.5m", 0.5, 0.0),
        ("1.0m", 1.0, 0.0),
        ("2.0m", 2.0, 0.0),
        ("diagonal", 1.5, 1.5)
    ]
    
    for name, initial_x, initial_y in scenarios:
        data = run_simulation(initial_x, initial_y)
        save_csv(f"edge-vision-uav-landing/reports/sim_2d_{name}.csv", data)
        print(f"Scenario {name} completed. Final Error: x={data[-1]['x']}, y={data[-1]['y']}, state={data[-1]['state']}")