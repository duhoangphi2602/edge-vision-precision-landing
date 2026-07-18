import cv2
import numpy as np
import os
import argparse
import sys
import yaml
from pathlib import Path

# Thêm đường dẫn gốc để import scripts.utils
sys.path.append(str(Path(__file__).parent.parent.parent))
import sys; from pathlib import Path; sys.path.append(str(Path(__file__).parent.parent.parent / "edge-vision-uav-landing")); from scripts.utils.run_manager import (
    add_standard_args, create_run_dir, save_run_metadata, 
    get_frame_limit, export_viewable_copy
)

def main():
    parser = argparse.ArgumentParser()
    parser = add_standard_args(parser)
    args = parser.parse_args()
    
    input_path = args.input or "assets/videos/base/p1b_vehicle_tracking/car_detection_base.mp4"
    config_path = args.config or "configs/motion/p2a_shaky_generation.yaml"
    
    if not os.path.exists(input_path):
        print(f"Error: Input video {input_path} not found.")
        sys.exit(1)
        
    run_dir, run_id = create_run_dir(args, "P2-A")
    
    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            
    seed = config_data.get('seed', 42)
    np.random.seed(seed)
    
    motion_cfg = config_data.get('motion', {}).get('translation', {})
    amp_x = motion_cfg.get('amplitude_x', [10, 30])
    amp_y = motion_cfg.get('amplitude_y', [5, 20])
    
    command = " ".join(sys.argv)
    save_run_metadata(run_dir, args, config_data, command)

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Cannot open {input_path}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    frame_limit = get_frame_limit(args, fps)
    
    output_path = os.path.join(run_dir, "shaky_output.mp4")
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

    frame_count = 0
    print("Generating artificial shaky video...")
    
    # Save camera motion transforms
    transforms_log = os.path.join(run_dir, "metrics.csv") # We use metrics.csv to log transforms
    with open(transforms_log, 'w') as f:
        f.write("frame,dx,dy\n")
        
        while frame_count < frame_limit:
            ret, frame = cap.read()
            if not ret: break
            
            # Random jitter based on config
            shake_x = int(np.random.normal(0, (amp_x[1]+amp_x[0])/2))
            shake_y = int(np.random.normal(0, (amp_y[1]+amp_y[0])/2))
            
            f.write(f"{frame_count},{shake_x},{shake_y}\n")
            
            M = np.float32([[1, 0, shake_x], [0, 1, shake_y]])
            shaken = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
            
            out.write(shaken)
            frame_count += 1

    cap.release()
    out.release()
    
    if args.export_viewable:
        export_viewable_copy(output_path)
        
    print(f"Run completed. Artifacts saved in {run_dir}")

if __name__ == "__main__":
    main()
