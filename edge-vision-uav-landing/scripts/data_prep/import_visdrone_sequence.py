#!/usr/bin/env python3
import os
import argparse
import sys
import subprocess
import json
import json
import shutil

def run_cmd(cmd, dry_run=False):
    print(f"[CMD] {' '.join(cmd)}")
    if not dry_run:
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"[ERROR] Command failed with exit code {result.returncode}")
            sys.exit(result.returncode)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to raw sequence directory or video")
    parser.add_argument("--annotation", required=True, help="Path to raw txt")
    parser.add_argument("--sequence-id", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", default="false")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("[INFO] DRY RUN MODE: No files will be changed.")
        
    if not os.path.exists(args.input):
        print(f"[ERROR] Input video not found: {args.input}")
        sys.exit(1)
        
    if not os.path.exists(args.annotation):
        print(f"[ERROR] Annotation not found: {args.annotation}")
        sys.exit(1)
        
    # 1. Parse annotations
    parsed_csv = os.path.join(args.output_dir, f"{args.sequence_id}_parsed.csv")
    parse_cmd = [
        "python3", "edge-vision-uav-landing/scripts/data_prep/visdrone_mot_parser.py",
        "--input", args.annotation,
        "--output", parsed_csv
    ]
    run_cmd(parse_cmd, args.dry_run)
    
    # 2. Select Target
    target_csv = os.path.join(args.output_dir, f"{args.sequence_id}_target.csv")
    select_cmd = [
        "python3", "edge-vision-uav-landing/scripts/data_prep/select_tracking_target.py",
        "--input", parsed_csv,
        "--output", target_csv
    ]
    run_cmd(select_cmd, args.dry_run)
    
    print("[INFO] Import sequence completed successfully.")
    
    # 3. Output Metadata
    metadata_path = os.path.join(args.output_dir, f"{args.sequence_id}_metadata.json")
    metadata = {
        "asset_id": f"visdrone2019_mot_val_{args.sequence_id}",
        "sequence_id": args.sequence_id,
        "selection_policy": "nearest_valid_car_to_center",
        "target_csv": target_csv
    }
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"[INFO] Metadata saved to {metadata_path}")

if __name__ == "__main__":
    main()
