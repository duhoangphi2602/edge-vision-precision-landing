import time
import numpy as np
import csv
import os
import argparse
from ultralytics import YOLO
import torch

def benchmark_model(model_path, iterations=100):
    print(f"Loading {model_path}...")
    model = YOLO(model_path, task='detect')
    dummy_input = torch.zeros(1, 3, 640, 640)
    
    # Warmup
    for _ in range(10):
        model(dummy_input, verbose=False)
        
    latencies = []
    print("Running benchmark...")
    for _ in range(iterations):
        start = time.time()
        model(dummy_input, verbose=False)
        end = time.time()
        latencies.append((end - start) * 1000.0) # convert to ms
        
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    
    return round(p50, 2), round(p95, 2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    models_to_test = [
        "edge-ai-training/experiments/TRN_001_visdrone_yolo26n_640/weights/best.pt",
        "edge-ai-training/models/optimized/yolo26n_640.onnx",
        "edge-ai-training/experiments/TRN_003_visdrone_yolo26s_640/weights/best.pt",
        "edge-ai-training/models/optimized/yolo26s_640.onnx"
    ]
    
    results = []
    for path in models_to_test:
        if os.path.exists(path):
            p50, p95 = benchmark_model(path)
            model_name = os.path.basename(path)
            model_type = "ONNX" if path.endswith(".onnx") else "PyTorch"
            size = "YOLO26s" if "26s" in path else "YOLO26n"
            results.append({
                "Model": size,
                "Format": model_type,
                "P50_Latency_ms": p50,
                "P95_Latency_ms": p95
            })
            print(f"{size} ({model_type}): P50={p50}ms, P95={p95}ms")
            
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Model", "Format", "P50_Latency_ms", "P95_Latency_ms"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved benchmark to {args.out}")
