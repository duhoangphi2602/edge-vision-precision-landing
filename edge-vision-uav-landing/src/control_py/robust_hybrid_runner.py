import yaml
import time
import csv
import sys
import os
import argparse
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.control_py.pid_controller import PIDController
from src.control_py.landing_state_machine import LandingStateMachine, LandingState
from src.ipc.udp_receiver import UDPReceiver
from src.ipc.udp_sender import UDPSender

def run_robust_scenario(scenario, output_dir):
    sid = scenario['id']
    init_x = scenario['initial_offset_x']
    init_y = scenario['initial_offset_y']
    net_delay = scenario.get('network_delay_sec', 0.0)
    frame_drop = scenario.get('frame_drop_rate', 0.0)
    cpu_hz = scenario.get('cpu_restriction_hz', 30.0)
    
    print(f"Running scenario: {sid}")
    
    sender = UDPSender(port=5006)
    receiver = UDPReceiver(port=5006)
    
    pid_x = PIDController(kp=1.0, ki=0.01, kd=0.1, v_max=1.0)
    pid_y = PIDController(kp=1.0, ki=0.01, kd=0.1, v_max=1.0)
    sm = LandingStateMachine(stale_timeout=0.2)
    
    x, y, z = init_x, init_y, 5.0
    current_time = 0.0
    dt = 1.0 / cpu_hz
    
    log_data = []
    
    for step in range(int(10.0 / dt)): # 10 seconds max
        target_found = True
            
        # Inject Frame Drop (mất gói tin)
        if random.random() >= frame_drop:
            obs_payload = {
                "target_found": target_found,
                "error_x": x,
                "error_y": y,
                "timestamp_publish_ns": time.time_ns()
            }
            sender.send_observation(obs_payload)
            
        # Inject Network Delay
        time.sleep(net_delay)
        
        # Nhận UDP
        obs, status = receiver.get_latest_observation()
        
        # Inject CPU Throttle (Chạy chậm)
        time.sleep(dt)
        current_time += dt
        
        # Cập nhật State Machine
        state = sm.update(current_time, obs if status == "VALID" else None)
        
        cmd_vx, cmd_vy, cmd_vz = 0.0, 0.0, 0.0
        if state in [LandingState.ALIGN, LandingState.HOLD_ALIGNMENT, LandingState.DESCEND]:
            cmd_vx = -pid_x.compute(x, dt)
            cmd_vy = -pid_y.compute(y, dt)
        if state == LandingState.DESCEND:
            cmd_vz = 0.5 
            
        x += cmd_vx * dt
        y += cmd_vy * dt
        z -= cmd_vz * dt
        
        log_data.append({
            "timestamp_ns": time.time_ns(),
            "time_sec": round(current_time, 3),
            "state": state.name,
            "error_x": round(x, 4),
            "error_y": round(y, 4),
            "cmd_vx": round(cmd_vx, 4),
            "cmd_vy": round(cmd_vy, 4),
            "cmd_vz": round(cmd_vz, 4),
            "altitude": round(z, 4)
        })
        
        if z <= 0:
            print("Landed!")
            break

    csv_file = os.path.join(output_dir, f"robustness_run_{sid}.csv")
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=log_data[0].keys())
        writer.writeheader()
        writer.writerows(log_data)
    print(f"Saved {csv_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
        
    out_dir = "edge-vision-uav-landing/runs/day12"
    os.makedirs(out_dir, exist_ok=True)
    
    for scenario in config['scenarios']:
        run_robust_scenario(scenario, out_dir)
