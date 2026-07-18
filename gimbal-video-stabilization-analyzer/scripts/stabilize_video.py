import cv2
import numpy as np
import os
import time
import argparse
import sys
import yaml
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
import sys; from pathlib import Path; sys.path.append(str(Path(__file__).parent.parent.parent / "edge-vision-uav-landing")); from scripts.utils.run_manager import (
    add_standard_args, create_run_dir, save_run_metadata, 
    get_frame_limit, export_viewable_copy
)

def main():
    parser = argparse.ArgumentParser()
    parser = add_standard_args(parser)
    args = parser.parse_args()
    
    input_path = args.input # For stabilize_video, input is usually the shaky video generated previously.
    if not input_path:
        print("Error: --input is required (should be the shaky video from generate_shaky_sample.py)")
        sys.exit(1)
        
    config_path = args.config or "configs/motion/p2a_shaky_generation.yaml"
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        sys.exit(1)
        
    run_dir, run_id = create_run_dir(args, "P2-A")
    
    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            
    command = " ".join(sys.argv)
    save_run_metadata(run_dir, args, config_data, command)

    cap = cv2.VideoCapture(input_path)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    
    frame_limit = min(get_frame_limit(args, fps), n_frames)
    
    stab_path = os.path.join(run_dir, "stabilized_raw.mp4")
    sbs_path = os.path.join(run_dir, "side_by_side_raw.mp4")
    
    out_stab = cv2.VideoWriter(stab_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    out_sbs = cv2.VideoWriter(sbs_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w*2, h))

    ret, prev = cap.read()
    if not ret:
        print("Error reading first frame")
        sys.exit(1)
        
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    transforms = []
    print("Step 1: Estimating trajectory...")
    start_t = time.time()
    
    for i in range(int(frame_limit) - 1):
        ret, curr = cap.read()
        if not ret: break
        curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)
        
        prev_pts = cv2.goodFeaturesToTrack(prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=30, blockSize=3)
        
        if prev_pts is not None and len(prev_pts) > 0:
            curr_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None)
            idx = np.where(status==1)[0]
            prev_pts, curr_pts = prev_pts[idx], curr_pts[idx]
            
            if len(prev_pts) >= 3:
                M, inliers = cv2.estimateAffinePartial2D(prev_pts, curr_pts)
            else:
                M = None
        else:
            M = None
            
        if M is None:
            transforms.append([0.0, 0.0, 0.0])
        else:
            dx = M[0, 2]
            dy = M[1, 2]
            da = np.arctan2(M[1, 0], M[0, 0])
            transforms.append([dx, dy, da])
        
        prev_gray = curr_gray

    if not transforms:
        print("No transforms calculated.")
        sys.exit(0)
        
    transforms = np.array(transforms)
    trajectory = np.cumsum(transforms, axis=0)

    SMOOTHING_RADIUS = config_data.get('motion', {}).get('smoothing', {}).get('window_size', 5)
    smoothed_trajectory = np.copy(trajectory)
    for i in range(3):
        box = np.ones(SMOOTHING_RADIUS)/SMOOTHING_RADIUS
        smoothed_trajectory[:, i] = np.convolve(trajectory[:, i], box, mode='same')

    difference = smoothed_trajectory - trajectory
    transforms_smooth = transforms + difference

    print("Step 2: Applying stabilization...")
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    metrics_path = os.path.join(run_dir, "metrics.csv")
    with open(metrics_path, 'w') as f:
        f.write("frame,dx,dy,da,dx_smooth,dy_smooth,da_smooth\n")
        
        for i in range(len(transforms_smooth)):
            ret, frame = cap.read()
            if not ret: break
            
            dx, dy, da = transforms[i]
            dx_s, dy_s, da_s = transforms_smooth[i]
            
            f.write(f"{i},{dx},{dy},{da},{dx_s},{dy_s},{da_s}\n")
            
            M = np.zeros((2,3), np.float32)
            M[0,0] = np.cos(da_s); M[0,1] = -np.sin(da_s); M[1,0] = np.sin(da_s); M[1,1] = np.cos(da_s)
            M[0,2] = dx_s; M[1,2] = dy_s
            
            stabilized = cv2.warpAffine(frame, M, (w,h))
            out_stab.write(stabilized)
            
            sbs = np.hstack((frame, stabilized))
            cv2.putText(sbs, 'Original', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            cv2.putText(sbs, 'Stabilized', (w+10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            out_sbs.write(sbs)

    cap.release()
    out_stab.release()
    out_sbs.release()
    
    print(f"Stabilization complete in {time.time()-start_t:.2f}s. Saved to {run_dir}.")
    
    if args.export_viewable:
        export_viewable_copy(stab_path)
        export_viewable_copy(sbs_path)

if __name__ == "__main__":
    main()
