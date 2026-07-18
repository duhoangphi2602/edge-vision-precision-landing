#!/usr/bin/env python3
import os
import csv
import sys
import argparse

def parse_visdrone_mot(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"[ERROR] Annotation file {input_path} does not exist.")
        sys.exit(1)
        
    parsed_data = []
    
    with open(input_path, 'r') as f:
        reader = csv.reader(f)
        for line_idx, row in enumerate(reader):
            if not row or len(row) < 10:
                print(f"[ERROR] Malformed row at line {line_idx+1}: {row}")
                sys.exit(1)
                
            try:
                frame_id = int(row[0])
                target_id = int(row[1])
                x = int(row[2])
                y = int(row[3])
                w = int(row[4])
                h = int(row[5])
                score = float(row[6])
                class_id = int(row[7])
                truncation = int(row[8])
                occlusion = int(row[9])
                
                # Bbox must have positive width/height
                if w <= 0 or h <= 0:
                    print(f"[ERROR] Invalid bbox at line {line_idx+1}: w={w}, h={h}")
                    sys.exit(1)
                    
                visibility = 1.0 - (occlusion / 2.0) # Simplistic visibility metric for VisDrone
                
                parsed_data.append({
                    'sequence_id': 'unknown',
                    'frame_id': frame_id,
                    'target_id': target_id,
                    'class_id': class_id,
                    'x': x,
                    'y': y,
                    'w': w,
                    'h': h,
                    'occlusion': occlusion,
                    'truncation': truncation,
                    'visibility': visibility
                })
            except ValueError as e:
                print(f"[ERROR] Type casting error at line {line_idx+1}: {e}")
                sys.exit(1)
                
    # Detect duplicates
    seen = set()
    for row in parsed_data:
        key = (row['frame_id'], row['target_id'])
        if key in seen:
            print(f"[ERROR] Duplicate target_id {row['target_id']} at frame {row['frame_id']}")
            sys.exit(1)
        seen.add(key)
        
    # Write output
    with open(output_path, 'w', newline='') as f:
        fieldnames = ['sequence_id', 'frame_id', 'target_id', 'class_id', 'x', 'y', 'w', 'h', 'occlusion', 'truncation', 'visibility']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(parsed_data)
        
    print(f"[INFO] Successfully parsed {len(parsed_data)} annotations to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    parse_visdrone_mot(args.input, args.output)
