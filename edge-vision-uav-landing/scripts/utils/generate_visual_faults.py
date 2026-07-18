import cv2
import numpy as np
import yaml
import os
import hashlib
import argparse
import glob

def add_blur(frame, kernel_size):
    k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    return cv2.GaussianBlur(frame, (k, k), 0)

def add_noise(frame, variance):
    noise = np.random.normal(0, variance, frame.shape).astype(np.int16)
    noisy_frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return noisy_frame

def add_low_light(frame, gamma):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(frame, table)

def process_sequence(input_dir, output_dir, config_suite, seed=42):
    np.random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)
    
    # Support both a directory of images or an explicit pattern, but usually it's a dir
    if os.path.isdir(input_dir):
        image_files = sorted(glob.glob(os.path.join(input_dir, "*.jpg")) + glob.glob(os.path.join(input_dir, "*.png")))
    else:
        # if they passed a specific pattern or file, we try parsing it
        image_files = sorted(glob.glob(input_dir))
        
    if not image_files:
        print(f"[ERROR] No images found in {input_dir}")
        return False
        
    for img_path in image_files:
        frame = cv2.imread(img_path)
        if frame is None:
            continue
            
        fault_type = config_suite.get('fault_type')
        if fault_type == 'blur':
            frame = add_blur(frame, config_suite.get('kernel_size', 5))
        elif fault_type == 'noise':
            frame = add_noise(frame, config_suite.get('noise_variance', 10))
        elif fault_type == 'combined':
            for sub_fault in config_suite.get('faults', []):
                if sub_fault['type'] == 'low_light':
                    frame = add_low_light(frame, sub_fault.get('gamma', 0.5))
                elif sub_fault['type'] == 'noise':
                    frame = add_noise(frame, sub_fault.get('noise_variance', 10))
                elif sub_fault['type'] == 'blur':
                    frame = add_blur(frame, sub_fault.get('kernel_size', 5))
                    
        out_path = os.path.join(output_dir, os.path.basename(img_path))
        cv2.imwrite(out_path, frame)
        
    print(f"[INFO] Generated corrupted sequence in {output_dir}")
    return True

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-id", type=str, required=True, help="Asset ID for tracking")
    parser.add_argument("--input-dir", type=str, required=True, help="Path to input sequence directory")
    parser.add_argument("--output-dir", type=str, required=True, help="Path to output corrupted sequence directory")
    parser.add_argument("--fault", type=str, required=True, help="Fault suite name from config")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--config", type=str, default="configs/faults/visual_faults.yaml", help="Path to fault config")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    
    if not os.path.exists(args.config):
        print(f"[ERROR] Config file {args.config} not found.")
        exit(1)
        
    with open(args.config, 'r') as f:
        configs = yaml.safe_load(f)['fault_suites']
        
    if args.fault not in configs:
        print(f"[ERROR] Fault {args.fault} not found in config.")
        exit(1)
        
    process_sequence(args.input_dir, args.output_dir, configs[args.fault], args.seed)
