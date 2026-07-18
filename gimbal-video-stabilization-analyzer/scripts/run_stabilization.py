import cv2
import numpy as np
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from stabilizer import VideoStabilizer

def create_synthetic_shaky_video(path):
    out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (640, 480))
    for i in range(100):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Rung lắc
        offset_x = int(np.sin(i * 0.5) * 20 + np.random.randn() * 5)
        offset_y = int(np.cos(i * 0.5) * 20 + np.random.randn() * 5)
        cv2.rectangle(frame, (300 + offset_x, 220 + offset_y), (340 + offset_x, 260 + offset_y), (0, 255, 0), -1)
        out.write(frame)
    out.release()

if __name__ == "__main__":
    input_vid = "sample_shaky.mp4"
    output_vid = "stabilized_output.mp4"
    print("Generating synthetic shaky video...")
    create_synthetic_shaky_video(input_vid)
    print("Running Stabilization Phase...")
    stab = VideoStabilizer()
    metrics = stab.stabilize(input_vid, output_vid)
    print(f"Metrics Output: {metrics}")
    
    with open('stabilization_metrics.csv', 'w') as f:
        f.write("Metric,Value\n")
        f.write(f"Camera trajectory jitter,{metrics['jitter_variance']:.4f}\n")
        f.write(f"Processing FPS,{metrics['fps_average']}\n")
