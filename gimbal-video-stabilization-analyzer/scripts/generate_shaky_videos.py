import cv2
import numpy as np
import os
import glob
import math
import argparse

def generate_shaky_video(img_dir, out_path, shake_intensity):
    images = sorted(glob.glob(os.path.join(img_dir, "*.jpg")))
    if not images:
        print(f"No images found in {img_dir}")
        return
        
    frame = cv2.imread(images[0])
    h, w = frame.shape[:2]
    
    out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (w, h))
    
    dx, dy, da = 0.0, 0.0, 0.0
    
    # Render first 100 frames for speed
    for img_path in images[:100]:
        frame = cv2.imread(img_path)
        
        # Smooth random walk to simulate drone drift
        dx += np.random.normal(0, shake_intensity)
        dy += np.random.normal(0, shake_intensity)
        da += np.random.normal(0, shake_intensity * 0.002)
        
        # Keep it somewhat bounded
        dx = np.clip(dx, -w*0.1, w*0.1)
        dy = np.clip(dy, -h*0.1, h*0.1)
        
        M = np.float32([[math.cos(da), -math.sin(da), dx],
                        [math.sin(da),  math.cos(da), dy]])
                        
        shaky_frame = cv2.warpAffine(frame, M, (w, h))
        out.write(shaky_frame)
        
    out.release()
    print(f"Saved {out_path} with intensity {shake_intensity}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seq', type=str, required=True, help='Path to VisDrone sequence dir')
    parser.add_argument('--outdir', type=str, required=True, help='Output directory')
    args = parser.parse_args()
    
    os.makedirs(args.outdir, exist_ok=True)
    np.random.seed(42) # Reproducibility
    
    generate_shaky_video(args.seq, f"{args.outdir}/seq_original.mp4", 0.0)
    generate_shaky_video(args.seq, f"{args.outdir}/seq_low.mp4", 0.5)
    generate_shaky_video(args.seq, f"{args.outdir}/seq_med.mp4", 2.0)
    generate_shaky_video(args.seq, f"{args.outdir}/seq_high.mp4", 5.0)
