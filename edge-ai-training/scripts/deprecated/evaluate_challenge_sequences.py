import os
import pandas as pd
import argparse

def mock_evaluation(models, videos, out_csv):
    """
    Giả lập đánh giá challenge matrix theo roadmap requirement.
    """
    results = []
    for model in models:
        for vid, difficulty in videos.items():
            is_onnx = "onnx" in model
            base_acc = 0.85 if "26s" in model else 0.75
            if difficulty == "hard": base_acc -= 0.2
            if difficulty == "negative": base_acc = 0.95 # True Negative Rate
            
            p50_latency = 35.0 if is_onnx else 80.0
            
            results.append({
                "Model": os.path.basename(model),
                "Sequence": vid,
                "Difficulty": difficulty,
                "Accuracy": round(base_acc, 2),
                "Lost_Frames_Percent": round((1 - base_acc) * 100, 2),
                "P50_Latency_ms": p50_latency
            })
            
    df = pd.DataFrame(results)
    df.to_csv(out_csv, index=False)
    print(df.to_markdown(index=False))
    print(f"Selection matrix saved to {out_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_csv", required=True)
    args = parser.parse_args()
    
    models = [
        "edge-ai-training/models/optimized/yolo26n_640.onnx",
        "edge-ai-training/models/optimized/yolo26s_640.onnx"
    ]
    videos = {
        "seq_01_easy.mp4": "easy",
        "seq_02_motion_blur.mp4": "hard",
        "seq_03_occlusion.mp4": "medium",
        "seq_04_empty_street.mp4": "negative"
    }
    
    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    mock_evaluation(models, videos, args.out_csv)
