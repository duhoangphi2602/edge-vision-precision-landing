import onnxruntime as ort
import sys
import yaml

config_path = "configs/missions/p1_b_tracking_v1.yaml"
try:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    model_path = config.get("model_path")
    if not model_path:
        raise ValueError("model_path missing in config")
    
    print(f"Loading ONNX model from: {model_path}")
    session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    print("Model load SUCCESS.")
    sys.exit(0)
except Exception as e:
    print(f"Model load FAILED: {e}")
    sys.exit(1)
