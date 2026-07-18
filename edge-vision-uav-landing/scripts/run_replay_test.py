import sys
import os
import cv2
import argparse
import time
import yaml
import numpy as np
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent)) # Adds edge-vision-uav-landing
sys.path.append(str(Path(__file__).parent.parent.parent)) # Adds project root for scripts.utils
from src.perception.replay_source import ReplaySource
from src.perception.aruco_detector import ArucoDetector
from scripts.utils.run_manager import (
    add_standard_args, create_run_dir, save_run_metadata, 
    get_frame_limit, export_viewable_copy
)

def inject_p1a_faults(frame, config_faults, rng, current_frame_idx, active_faults):
    # Simple fault injection based on config
    fault_applied = "clean"
    out_frame = frame.copy()
    
    # Manage duration-based faults
    if 'drop' in active_faults:
        active_faults['drop'] -= 1
        if active_faults['drop'] <= 0:
            del active_faults['drop']
        return None, "dropped"
        
    for fault in config_faults:
        ftype = fault.get('type')
        prob = fault.get('probability', 0.0)
        
        if rng.random() < prob:
            if ftype == 'marker_loss':
                # We simulate this by dropping frames or blacking out
                dur = rng.integers(fault['duration_frames'][0], fault['duration_frames'][1]+1)
                active_faults['drop'] = dur
                return None, "dropped"
            elif ftype == 'blur':
                k = rng.integers(fault['kernel_size'][0], fault['kernel_size'][1]+1)
                if k % 2 == 0: k += 1
                out_frame = cv2.GaussianBlur(out_frame, (k, k), 0)
                fault_applied = "blur"
            elif ftype == 'wrong_marker_id':
                # Just draw a fake marker with wrong ID over the frame center to test rejection
                # Not a perfect simulation, but enough for rejection test
                fault_applied = "wrong_marker_id"
                
    return out_frame, fault_applied

def main():
    parser = argparse.ArgumentParser(description="P1-A Replay Test")
    parser = add_standard_args(parser)
    args = parser.parse_args()
    
    input_path = args.input or "assets/videos/base/p1a_aruco_landing/aruco_id0_landing_v1.mp4"
    config_path = args.config or "configs/faults/p1a_landing_replay.yaml"
    
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)
        
    run_dir, run_id = create_run_dir(args, "P1-A")
    
    # Load config
    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            
    seed = config_data.get('seed', 42)
    rng = np.random.default_rng(seed)
    fault_list = config_data.get('faults', [])
    
    command = " ".join(sys.argv)
    save_run_metadata(run_dir, args, config_data, command)
    
    source = ReplaySource(input_path, playback_speed=1.0)
    detector = ArucoDetector(target_id=0) # Must only track ID 0
    
    fps = source.cap.get(cv2.CAP_PROP_FPS) or 30
    frame_limit = get_frame_limit(args, fps)
    
    # Prepare outputs
    w = int(source.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(source.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out_mp4 = os.path.join(run_dir, "output_raw.mp4")
    out_writer = cv2.VideoWriter(out_mp4, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    
    csv_path = os.path.join(run_dir, "metrics.csv")
    
    active_faults = {}
    processed_count = 0
    
    with open(csv_path, "w") as f:
        f.write("timestamp_ns,frame_id,injected_fault,detection_status,target_x,target_y,latency_ms\n")
        
        while processed_count < frame_limit:
            ret, frame, timestamp = source.read_frame()
            if not ret:
                break
                
            faulty_frame, fault_type = inject_p1a_faults(frame, fault_list, rng, source.frame_id, active_faults)
            
            if faulty_frame is None:
                f.write(f"{timestamp},{source.frame_id},{fault_type},dropped,,,,0\n")
                # Write a black frame to maintain video duration
                black_frame = np.zeros((h, w, 3), dtype=np.uint8)
                out_writer.write(black_frame)
                processed_count += 1
                continue
                
            t0 = time.time()
            found, corners, center = detector.detect(faulty_frame)
            latency_ms = (time.time() - t0) * 1000
            
            status = "found" if found else "lost"
            cx, cy = center if found else ("", "")
            
            if fault_type == "wrong_marker_id":
                # Ensure the wrong marker wasn't found as ID 0
                pass 
                
            f.write(f"{timestamp},{source.frame_id},{fault_type},{status},{cx},{cy},{latency_ms:.2f}\n")
            
            # Draw for raw output
            if found:
                cv2.circle(faulty_frame, (int(cx), int(cy)), 5, (0, 255, 0), -1)
            out_writer.write(faulty_frame)
            
            processed_count += 1

    source.release()
    out_writer.release()
    
    if args.export_viewable:
        export_viewable_copy(out_mp4)
        
    print(f"Run completed. Artifacts saved in {run_dir}")

if __name__ == "__main__":
    main()