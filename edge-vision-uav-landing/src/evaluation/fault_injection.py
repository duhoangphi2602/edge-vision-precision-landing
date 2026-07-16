import cv2
import numpy as np
import yaml
import random

class FaultInjector:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
    def apply_faults(self, frame):
        fault_applied = "none"
        result_frame = frame.copy()
        
        # 1. Drop Frame
        if self.config.get('drop_frame', {}).get('enabled', False):
            if random.random() < self.config['drop_frame'].get('drop_probability', 0.1):
                return None, "dropped"
                
        # 2. Gaussian Noise
        if self.config.get('gaussian_noise', {}).get('enabled', False):
            mean = self.config['gaussian_noise'].get('mean', 0)
            std = self.config['gaussian_noise'].get('std', 15)
            noise = np.random.normal(mean, std, result_frame.shape).astype(np.uint8)
            result_frame = cv2.add(result_frame, noise)
            fault_applied = "noise"
            
        # 3. Motion Blur
        if self.config.get('motion_blur', {}).get('enabled', False):
            k_size = self.config['motion_blur'].get('kernel_size', 15)
            kernel = np.zeros((k_size, k_size))
            kernel[int((k_size-1)/2), :] = np.ones(k_size)
            kernel /= k_size
            result_frame = cv2.filter2D(result_frame, -1, kernel)
            fault_applied += "_blur"
            
        # 4. Occlusion (Che khuất)
        if self.config.get('occlusion', {}).get('enabled', False):
            h, w = result_frame.shape[:2]
            box_w = self.config['occlusion'].get('box_w', 50)
            box_h = self.config['occlusion'].get('box_h', 50)
            x1 = random.randint(0, max(0, w - box_w))
            y1 = random.randint(0, max(0, h - box_h))
            cv2.rectangle(result_frame, (x1, y1), (x1 + box_w, y1 + box_h), (0, 0, 0), -1)
            fault_applied += "_occlusion"

        if fault_applied == "none":
            fault_applied = "clean"
            
        return result_frame, fault_applied