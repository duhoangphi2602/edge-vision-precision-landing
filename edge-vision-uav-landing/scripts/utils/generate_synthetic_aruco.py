import cv2
import numpy as np
import os
import yaml

def create_synthetic_aruco_video(output_path, config_path):
    # Setup video writer
    fps = 30
    duration = 30
    num_frames = fps * duration
    width, height = 640, 480
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Generate ArUco marker (DICT_4X4_50, ID 0)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker_size = 200
    marker_img = cv2.aruco.generateImageMarker(aruco_dict, 0, marker_size)
    marker_img = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)
    
    np.random.seed(42)
    
    # Generate synthetic motions
    x, y = width / 2, height / 2
    scale = 0.5
    angle = 0
    
    for i in range(num_frames):
        # Create grass-like background
        bg = np.ones((height, width, 3), dtype=np.uint8) * np.array([50, 150, 50], dtype=np.uint8)
        noise = np.random.normal(0, 10, (height, width, 3)).astype(np.uint8)
        bg = cv2.add(bg, noise)
        
        # Simple random walk for parameters
        x += np.random.normal(0, 2)
        y += np.random.normal(0, 2)
        scale += np.random.normal(0, 0.005)
        angle += np.random.normal(0, 0.5)
        
        # Keep in bounds
        x = np.clip(x, 100, width - 100)
        y = np.clip(y, 100, height - 100)
        scale = np.clip(scale, 0.2, 2.0)
        
        # Transform marker
        M = cv2.getRotationMatrix2D((marker_size/2, marker_size/2), angle, scale)
        M[0, 2] += x - marker_size/2
        M[1, 2] += y - marker_size/2
        
        # Warp marker onto background
        warped_marker = cv2.warpAffine(marker_img, M, (width, height), borderMode=cv2.BORDER_TRANSPARENT)
        
        # Create mask
        gray_marker = cv2.cvtColor(warped_marker, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_marker, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        
        bg_masked = cv2.bitwise_and(bg, bg, mask=mask_inv)
        marker_masked = cv2.bitwise_and(warped_marker, warped_marker, mask=mask)
        frame = cv2.add(bg_masked, marker_masked)
        
        # Add slight blur occasionally
        if i % 30 < 5:
            frame = cv2.GaussianBlur(frame, (5, 5), 0)
            
        out.write(frame)
        
    out.release()
    
    # Save config
    config = {
        'seed': 42,
        'fps': fps,
        'duration_sec': duration,
        'resolution': f"{width}x{height}",
        'marker_dict': 'DICT_4X4_50',
        'marker_id': 0,
        'motions': ['random_walk_translation', 'random_walk_scale', 'random_walk_rotation'],
        'effects': ['grass_background', 'gaussian_noise', 'occasional_blur']
    }
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
        
if __name__ == '__main__':
    create_synthetic_aruco_video(
        'assets/videos/base/p1a_aruco_landing/aruco_id0_landing_v1.mp4',
        'assets/videos/manifests/generation_configs/aruco_synthetic_v1.yaml'
    )
