#!/usr/bin/env python3
import cv2
import numpy as np
import argparse
import hashlib
import sys
import os
import json
import time

def inject_faults(input_path, output_path, fault_type, severity, seed):
    np.random.seed(seed)
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open {input_path}")
        sys.exit(1)
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # We use mp4v for headless, user can convert to h264 if needed
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        if fault_type == 'blur':
            k = 5 if severity == 'low' else 15 if severity == 'medium' else 25
            frame = cv2.GaussianBlur(frame, (k, k), 0)
        elif fault_type == 'noise':
            var = 10 if severity == 'low' else 30 if severity == 'medium' else 50
            noise = np.random.normal(0, var, frame.shape).astype(np.int16)
            frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        elif fault_type == 'brightness':
            gamma = 0.8 if severity == 'low' else 0.5 if severity == 'medium' else 0.2
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
            frame = cv2.LUT(frame, table)
            
        out.write(frame)
        
    cap.release()
    out.release()
    print(f"[INFO] Generated corrupted video: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--fault", required=True, choices=['blur', 'noise', 'brightness'])
    parser.add_argument("--severity", required=True, choices=['low', 'medium', 'high'])
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    
    inject_faults(args.input, args.output, args.fault, args.severity, args.seed)
