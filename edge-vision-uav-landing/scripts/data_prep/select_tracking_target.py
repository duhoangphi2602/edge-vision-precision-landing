#!/usr/bin/env python3
import csv
import argparse
import sys
import math

# VisDrone Classes: 0:ignored, 1:pedestrian, 2:people, 3:bicycle, 4:car, 5:van, 6:truck, 7:tricycle, 8:awning-tricycle, 9:bus, 10:motor, 11:others
ELIGIBLE_CLASSES = [4, 5, 6, 9] # car, van, truck, bus

def select_target(input_csv, output_csv, frame_width=768, frame_height=432):
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    if not rows:
        print("[ERROR] No annotations found.")
        sys.exit(1)
        
    # Group by frame
    frames = {}
    for r in rows:
        fid = int(r['frame_id'])
        if fid not in frames:
            frames[fid] = []
        frames[fid].append(r)
        
    first_frame = min(frames.keys())
    
    # 1. Select target at first frame
    candidates = frames[first_frame]
    best_target = None
    min_dist = float('inf')
    
    center_x = frame_width / 2.0
    center_y = frame_height / 2.0
    
    for c in candidates:
        if int(c['class_id']) not in ELIGIBLE_CLASSES:
            continue
        if float(c['visibility']) < 0.5:
            continue
            
        cx = int(c['x']) + int(c['w']) / 2.0
        cy = int(c['y']) + int(c['h']) / 2.0
        dist = math.hypot(cx - center_x, cy - center_y)
        
        if dist < min_dist:
            min_dist = dist
            best_target = int(c['target_id'])
            
    if best_target is None:
        print(f"[ERROR] No eligible vehicle target found in the first frame ({first_frame}).")
        sys.exit(1)
        
    print(f"[INFO] Selected target_id {best_target} at distance {min_dist:.2f}px from center.")
    
    # 2. Filter dataset for selected target
    selected_rows = []
    for r in rows:
        if int(r['target_id']) == best_target:
            selected_rows.append(r)
            
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(selected_rows)
        
    print(f"[INFO] Saved {len(selected_rows)} frames for target {best_target}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    select_target(args.input, args.output)
