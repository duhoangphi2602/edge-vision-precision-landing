import yaml
import time
import csv
import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.control_py.pid_controller import PIDController
from src.control_py.landing_state_machine import LandingStateMachine, LandingState
from src.ipc.udp_receiver import UDPReceiver
from src.ipc.udp_sender import UDPSender

def run_hybrid_scenario(scenario, output_dir):
    sid = scenario['id']
    init_x = scenario['initial_offset_x']
    init_y = scenario['initial_offset_y']
    loss_sec = scenario.get('marker_loss_injection_sec', 0.0)
    
    print(f"Running scenario: {sid}")
    
    sender = UDPSender(port=5005)
    receiver = UDPReceiver(port=5005)
    
    pid_x = PIDController(kp=1.0, ki=0.01, kd=0.1, v_max=1.0)
    pid_y = PIDController(kp=1.0, ki=0.01, kd=0.1, v_max=1.0)
    sm = LandingStateMachine(stale_timeout=0.2)
    
    x, y, z = init_x, init_y, 5.0
    current_time = 0.0
    dt = 0.033 # ~30Hz
    
    log_data = []
    
    for step in range(300): # 10 seconds max
        # 1. Simulate perception sending over UDP
        target_found = True
        if loss_sec > 0 and current_time >= loss_sec:
            target_found = False
            
        obs_payload = {
            "target_found": target_found,
            "error_x": x,
            "error_y": y,
            "timestamp_publish_ns": time.time_ns()
        }
        sender.send_observation(obs_payload)
        time.sleep(0.001) # Small delay for UDP delivery
        
        # 2. Control process receives UDP
        obs, status = receiver.get_latest_observation()
        
        # 3. Update State Machine
        state = sm.update(current_time, obs if status == "VALID" else None)
        
        # 4. Compute PID
        cmd_vx, cmd_vy, cmd_vz = 0.0, 0.0, 0.0
        if state in [LandingState.ALIGN, LandingState.HOLD_ALIGNMENT, LandingState.DESCEND]:
            cmd_vx = -pid_x.compute(x, dt)
            cmd_vy = -pid_y.compute(y, dt)
        
        if state == LandingState.DESCEND:
            cmd_vz = 0.5 # Positive is down
        else:
            cmd_vz = 0.0
            
        # 5. Physics update (Mock UAV response)
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
        
        current_time += dt
        
        if z <= 0:
            print("Landed!")
            break

    # Save CSV
    csv_file = os.path.join(output_dir, f"landing_run_{sid}.csv")
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
        
    out_dir = "edge-vision-uav-landing/runs/day11"
    os.makedirs(out_dir, exist_ok=True)
    
    for scenario in config['scenarios']:
        run_hybrid_scenario(scenario, out_dir)
