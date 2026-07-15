import yaml
import numpy as np
import os

class CameraCalibration:
    def __init__(self, config_path="configs/camera.yaml"):
        self.config_path = config_path
        self.camera_matrix = None
        self.dist_coeffs = None
        self.width = 640
        self.height = 480
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Cannot find camera config at {self.config_path}")
        
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)
            self.camera_matrix = np.array(data.get("camera_matrix", []), dtype=np.float32)
            self.dist_coeffs = np.array(data.get("dist_coeffs", []), dtype=np.float32)
            self.width = data.get("image_width", 640)
            self.height = data.get("image_height", 480)
            
    def get_parameters(self):
        return self.camera_matrix, self.dist_coeffs