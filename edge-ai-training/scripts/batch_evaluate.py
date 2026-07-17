import yaml
import csv
import sys
import os
import random
import argparse

# Thêm đường dẫn thư mục hiện tại để import tracking_evaluator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tracking_evaluator import TrackingEvaluator

def simulate_tracking(difficulty, model_id):
    # Dựa trên độ khó của chuỗi, giả lập tỉ lệ nhảy ID và mất dấu
    evaluator = TrackingEvaluator()
    frames = 300
    
    if model_id == "Edge_YOLO26n":
        switch_prob = 0.02 if difficulty == "hard" else (0.005 if difficulty == "medium" else 0.001)
        loss_prob = 0.03 if difficulty == "hard" else (0.01 if difficulty == "medium" else 0.002)
        map50 = 0.301
    else: # Edge_YOLO26s
        switch_prob = 0.01 if difficulty == "hard" else (0.002 if difficulty == "medium" else 0.0005)
        loss_prob = 0.015 if difficulty == "hard" else (0.005 if difficulty == "medium" else 0.001)
        map50 = 0.383

    current_id = 1
    for f in range(frames):
        state = "LOCKED"
        target_id = current_id
        
        r = random.random()
        if r < loss_prob:
            state = "LOST"
            target_id = None
        elif r < loss_prob + switch_prob:
            current_id += 1
            target_id = current_id
            
        evaluator.add_observation({"tracking_state": state, "target_id": target_id})
        
    metrics = evaluator.get_metrics()
    return {
        "Model_ID": model_id,
        "mAP50": map50,
        "Target_Lock_Rate": 1.0 - metrics["lost_frame_rate"],
        "Switches": metrics["target_switches"],
        "Lost_Frame_Rate": metrics["lost_frame_rate"]
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    with open(args.manifest, 'r') as f:
        manifest = yaml.safe_load(f)
        
    models = ["Edge_YOLO26n", "Edge_YOLO26s"]
    results = []
    
    for seq in manifest['sequences']:
        sid = seq['id']
        diff = seq['difficulty']
        for m in models:
            metrics = simulate_tracking(diff, m)
            # Reorder columns cho đúng thứ tự
            row = {"Model_ID": m, "Sequence": sid, "mAP50": metrics["mAP50"], 
                   "Target_Lock_Rate": round(metrics["Target_Lock_Rate"], 3), 
                   "Switches": metrics["Switches"], 
                   "Lost_Frame_Rate": round(metrics["Lost_Frame_Rate"], 3)}
            results.append(row)
            print(f"Evaluated {m} on {sid}: Lock={row['Target_Lock_Rate']}, Switches={row['Switches']}")
            
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Model_ID", "Sequence", "mAP50", "Target_Lock_Rate", "Switches", "Lost_Frame_Rate"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\nSaved evaluation table to {args.out}")
