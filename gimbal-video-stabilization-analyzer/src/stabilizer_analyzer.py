import cv2
import numpy as np
import os
import argparse
import csv

def moving_average(curve, radius):
    window_size = 2 * radius + 1
    f = np.ones(window_size) / window_size
    curve_pad = np.pad(curve, (radius, radius), 'edge')
    curve_smoothed = np.convolve(curve_pad, f, mode='same')
    curve_smoothed = curve_smoothed[radius:-radius]
    return curve_smoothed

def smooth_trajectory(trajectory, radius):
    smoothed_trajectory = np.copy(trajectory)
    for i in range(3):
        smoothed_trajectory[:, i] = moving_average(trajectory[:, i], radius)
    return smoothed_trajectory

def fix_border(frame):
    s = frame.shape
    T = cv2.getRotationMatrix2D((s[1]/2, s[0]/2), 0, 1.04)
    frame = cv2.warpAffine(frame, T, (s[1], s[0]))
    return frame

def run_stabilization(input_video, output_dir, radius=30):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(input_video)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    out_video = os.path.join(output_dir, 'stabilized.mp4')
    out = cv2.VideoWriter(out_video, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

    _, prev = cap.read()
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    
    transforms = np.zeros((n_frames-1, 3), np.float32) 
    
    print("Step 1: Estimating camera motion...")
    for i in range(n_frames-2):
        prev_pts = cv2.goodFeaturesToTrack(prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=30, blockSize=3)
        success, curr = cap.read()
        if not success: break
        curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)
        curr_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None)
        
        idx = np.where(status==1)[0]
        prev_pts = prev_pts[idx]
        curr_pts = curr_pts[idx]
        
        # Affine transform
        m, _ = cv2.estimateAffinePartial2D(prev_pts, curr_pts)
        if m is not None:
            dx = m[0, 2]
            dy = m[1, 2]
            da = np.arctan2(m[1, 0], m[0, 0])
        else:
            dx, dy, da = 0, 0, 0
            
        transforms[i] = [dx,dy,da]
        prev_gray = curr_gray
        
    trajectory = np.cumsum(transforms, axis=0)
    smoothed_trajectory = smooth_trajectory(trajectory, radius)
    difference = smoothed_trajectory - trajectory
    transforms_smooth = transforms + difference
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    print("Step 2: Applying stabilization and calculating jitter...")
    
    jitter_values = []
    with open(os.path.join(output_dir, 'camera_motion.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['frame', 'dx', 'dy', 'da'])
        
        for i in range(n_frames-2):
            success, frame = cap.read()
            if not success: break
            
            dx = transforms_smooth[i,0]
            dy = transforms_smooth[i,1]
            da = transforms_smooth[i,2]
            
            m = np.zeros((2,3), np.float32)
            m[0,0] = np.cos(da)
            m[0,1] = -np.sin(da)
            m[1,0] = np.sin(da)
            m[1,1] = np.cos(da)
            m[0,2] = dx
            m[1,2] = dy
            
            frame_stabilized = cv2.warpAffine(frame, m, (w,h))
            frame_stabilized = fix_border(frame_stabilized) 
            
            # Tính Jitter cục bộ (độ lệch)
            jitter = np.sqrt(dx**2 + dy**2)
            jitter_values.append(jitter)
            writer.writerow([i, dx, dy, da])
            
            out.write(frame_stabilized)
    
    cap.release()
    out.release()
    
    avg_jitter = np.mean(jitter_values) if jitter_values else 0
    print(f"Stabilization complete. Output saved to {output_dir}")
    print(f"Average Trajectory Jitter: {avg_jitter:.2f} pixels")
    return avg_jitter

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True, help='Path to input video')
    parser.add_argument('--outdir', type=str, required=True, help='Output directory')
    args = parser.parse_args()
    run_stabilization(args.input, args.outdir)
