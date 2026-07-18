import os
import subprocess
import json
import csv
import sys
import numpy as np
from pathlib import Path
import argparse
import yaml

sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent / "edge-vision-uav-landing")); from scripts.utils.run_manager import (
    add_standard_args, create_run_dir, save_run_metadata,
)

def run_tracking(video_path, run_dir, name, ref_bbox):
    out_dir = os.path.join(run_dir, name)
    os.makedirs(out_dir, exist_ok=True)
    
    cmd = [
        sys.executable, "edge-vision-uav-landing/src/perception/vehicle_tracking_demo.py",
        "--input", video_path,
        "--output-root", run_dir,
        "--run-id", name,
        "--export-viewable",
        "--overwrite"
    ]
    if ref_bbox:
        cmd.extend(["--reference-bbox", ref_bbox])
        
    print(f"Running tracking for {name}...")
    subprocess.run(cmd, check=True)
    return out_dir

def load_csv(path):
    data = []
    if not os.path.exists(path):
        return data
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def calculate_metrics(data, evaluable_frames=150):
    total = len(data)
    locked = 0
    switches = 0
    prev_id = None
    
    centers_x = []
    centers_y = []
    areas = []
    latencies = []
    inference_latencies = []
    e2e_latencies = []
    
    for i, row in enumerate(data):
        if row['target_found'] == 'True':
            locked += 1
            cx = float(row['center_x'])
            cy = float(row['center_y'])
            area = float(row['bbox_area'])
            centers_x.append(cx)
            centers_y.append(cy)
            areas.append(area)
            
            curr_id = row['target_id']
            if prev_id is not None and curr_id != prev_id:
                switches += 1
            prev_id = curr_id
            
        lat_val = row.get('tracking_latency_ms', '')
        lat = float(lat_val) if lat_val else 0
        if lat > 0: latencies.append(lat)
        
        inf_val = row.get('inference_latency_ms', '')
        inf = float(inf_val) if inf_val else 0
        if inf > 0: inference_latencies.append(inf)
        
        e2e_val = row.get('e2e_latency_ms', '')
        e2e = float(e2e_val) if e2e_val else 0
        if e2e > 0: e2e_latencies.append(e2e)
            
    # target-present lock rate
    lock_rate = locked / max(1, evaluable_frames)
    
    # Detrended jitter
    if len(centers_x) >= 5:
        window = 5
        cx_s = np.convolve(centers_x, np.ones(window)/window, mode='valid')
        cy_s = np.convolve(centers_y, np.ones(window)/window, mode='valid')
        jitter = float(np.mean(np.sqrt((centers_x[2:-2] - cx_s)**2 + (centers_y[2:-2] - cy_s)**2)))
        
        area_s = np.convolve(areas, np.ones(window)/window, mode='valid')
        area_jitter = float(np.mean(np.abs(areas[2:-2] - area_s) / np.maximum(area_s, 1)))
    else:
        jitter = None
        area_jitter = None
        
    p50_lat = float(np.percentile(latencies, 50)) if latencies else None
    p95_lat = float(np.percentile(latencies, 95)) if latencies else None
    
    p50_inf = float(np.percentile(inference_latencies, 50)) if inference_latencies else None
    p95_inf = float(np.percentile(inference_latencies, 95)) if inference_latencies else None
    
    p50_e2e = float(np.percentile(e2e_latencies, 50)) if e2e_latencies else None
    p95_e2e = float(np.percentile(e2e_latencies, 95)) if e2e_latencies else None

    return {
        "target_present_lock_rate": round(lock_rate, 3) if lock_rate is not None else None,
        "global_lock_rate": round(locked / max(1, total), 3) if total > 0 else None,
        "target_switches": switches if len(centers_x) >= 5 else None,
        "detrended_center_jitter": round(jitter, 2) if jitter is not None else None,
        "bbox_area_jitter_ratio": round(area_jitter, 3) if area_jitter is not None else None,
        "tracking_p50_ms": round(p50_lat, 2) if p50_lat is not None else None,
        "tracking_p95_ms": round(p95_lat, 2) if p95_lat is not None else None,
        "inference_p50_ms": round(p50_inf, 2) if p50_inf is not None else None,
        "inference_p95_ms": round(p95_inf, 2) if p95_inf is not None else None,
        "e2e_p50_ms": round(p50_e2e, 2) if p50_e2e is not None else None,
        "e2e_p95_ms": round(p95_e2e, 2) if p95_e2e is not None else None,
        "valid_sample_count": len(centers_x)
    }

def safe_diff(a, b, rnd=2):
    if a is None or b is None:
        return None
    return round(a - b, rnd)

def main():
    parser = argparse.ArgumentParser()
    parser = add_standard_args(parser)
    args = parser.parse_args()
    
    run_dir, run_id = create_run_dir(args, "P2-A")
    contract_path = "gimbal-video-stabilization-analyzer/configs/evaluation_synthetic_regression.yaml"
    with open(contract_path, 'r') as f:
        contract = yaml.safe_load(f).get('evaluation_contract', {})
        
    asset_id = contract.get('asset_id', 'car_detection_base')
    if asset_id == 'synthetic_car_tracking':
        orig_vid = "assets/videos/base/p1b_vehicle_tracking/synthetic_car_tracking.mp4"
    else:
        orig_vid = "assets/videos/base/p1b_vehicle_tracking/car_detection_base.mp4"
        
    evaluable_frames = contract.get('evaluable_frames', 150)
    
    # Generate shaky and stabilized
    print("Generating shaky sample...")
    subprocess.run([
        sys.executable, "gimbal-video-stabilization-analyzer/scripts/generate_shaky_sample.py",
        "--input", orig_vid,
        "--output-root", run_dir,
        "--run-id", "shaky_gen",
        "--export-viewable"
    ], check=True)
    
    shaky_dir = os.path.join(run_dir, "shaky_gen")
    shaky_vid = os.path.join(shaky_dir, "shaky_output.mp4")
    
    print("Generating stabilized sample...")
    subprocess.run([
        sys.executable, "gimbal-video-stabilization-analyzer/scripts/stabilize_video.py",
        "--input", shaky_vid,
        "--output-root", run_dir,
        "--run-id", "stab_gen",
        "--export-viewable"
    ], check=True)
    
    stab_dir = os.path.join(run_dir, "stab_gen")
    stab_vid = os.path.join(stab_dir, "stabilized_raw.mp4")
    
    # Analyze stabilization metrics
    stab_metrics_path = os.path.join(stab_dir, "metrics.csv")
    crop_ratios = []
    if os.path.exists(stab_metrics_path):
        w, h = 768, 432
        with open(stab_metrics_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dx = abs(float(row['dx_smooth']))
                dy = abs(float(row['dy_smooth']))
                crop_ratios.append((dx/w) + (dy/h))
    
    crop_mean = np.mean(crop_ratios) if crop_ratios else None
    crop_p95 = np.percentile(crop_ratios, 95) if crop_ratios else None
    
    # Contract setup
    ref_bbox = None
    if 'reference_frame' in contract and 'reference_bbox_xyxy' in contract:
        idx = contract['reference_frame']
        box = contract['reference_bbox_xyxy']
        ref_bbox = f"{idx}:{box}"
        
    orig_dir = run_tracking(orig_vid, run_dir, "original", ref_bbox)
    shaky_dir = run_tracking(shaky_vid, run_dir, "shaky", ref_bbox)
    stab_dir = run_tracking(stab_vid, run_dir, "stabilized", ref_bbox)
    
    # Analyze Tracking
    orig_dir = os.path.join(run_dir, "original")
    shaky_track_dir = os.path.join(run_dir, "shaky")
    stab_track_dir = os.path.join(run_dir, "stabilized")
    
    orig_data = load_csv(os.path.join(orig_dir, "tracking_frames.csv"))
    shaky_data = load_csv(os.path.join(shaky_track_dir, "tracking_frames.csv"))
    stab_data = load_csv(os.path.join(stab_track_dir, "tracking_frames.csv"))
    
    m_orig = calculate_metrics(orig_data, evaluable_frames)
    m_shaky = calculate_metrics(shaky_data, evaluable_frames)
    m_stab = calculate_metrics(stab_data, evaluable_frames)
    
    # Compare
    comparison = {
        "tracking": {
            "target_present_lock_rate": {
                "original": m_orig["target_present_lock_rate"],
                "shaky": m_shaky["target_present_lock_rate"],
                "stabilized": m_stab["target_present_lock_rate"],
                "shaky_degradation": safe_diff(m_shaky["target_present_lock_rate"], m_orig["target_present_lock_rate"], 3),
                "stabilized_recovery": safe_diff(m_stab["target_present_lock_rate"], m_shaky["target_present_lock_rate"], 3)
            },
            "detrended_center_jitter": {
                "original": m_orig["detrended_center_jitter"],
                "shaky": m_shaky["detrended_center_jitter"],
                "stabilized": m_stab["detrended_center_jitter"],
                "shaky_degradation": safe_diff(m_shaky["detrended_center_jitter"], m_orig["detrended_center_jitter"], 2),
                "stabilized_recovery": safe_diff(m_shaky["detrended_center_jitter"], m_stab["detrended_center_jitter"], 2) # positive is good
            },
            "e2e_p50_ms": {
                "original": m_orig["e2e_p50_ms"],
                "shaky": m_shaky["e2e_p50_ms"],
                "stabilized": m_stab["e2e_p50_ms"],
            },
            "valid_sample_count": {
                "original": m_orig["valid_sample_count"],
                "shaky": m_shaky["valid_sample_count"],
                "stabilized": m_stab["valid_sample_count"],
            }
        },
        "stabilization": {
            "crop_ratio_mean": round(crop_mean, 3) if crop_mean is not None else None,
            "crop_ratio_p95": round(crop_p95, 3) if crop_p95 is not None else None,
        }
    }
    
    with open(os.path.join(run_dir, "summary_metrics.json"), 'w') as f:
        json.dump(comparison, f, indent=2)
        
    print("Comparison complete! Results saved to", run_dir)
    print(json.dumps(comparison, indent=2))

if __name__ == "__main__":
    main()
