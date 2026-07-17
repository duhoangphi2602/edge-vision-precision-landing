import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
import numpy as np
from src.estimation.camera_calibration import CameraCalibration
from src.estimation.pose_estimator import PoseEstimator

def test_pose():
    print("--- Test Pose Estimation ---")
    calib = CameraCalibration("configs/camera.yaml")
    cam_mat, dist = calib.get_parameters()
    print("Loaded Camera Matrix:\n", cam_mat)
    
    # Kích thước thật 0.15m (15cm)
    estimator = PoseEstimator(cam_mat, dist, marker_size=0.15)
    
    # Giả lập tọa độ 2D corners của marker khi nó nằm chính diện, cách camera tầm 1 mét
    # Giả sử kích thước trên pixel khoảng 80x80 px nằm ở trung tâm ảnh
    mock_corners = [[
        [280., 200.], # Top-left
        [360., 200.], # Top-right
        [360., 280.], # Bottom-right
        [280., 280.]  # Bottom-left
    ]]
    
    success, rvec, tvec = estimator.estimate_pose(mock_corners[0])
    
    if success:
        x_m, y_m, z_m = estimator.get_error_metric(tvec)
        print("\nPose Estimation Success!")
        print(f"X Offset (Lệch trái/phải) = {x_m:.3f} m")
        print(f"Y Offset (Lệch trên/dưới) = {y_m:.3f} m")
        print(f"Z Distance (Khoảng cách)  = {z_m:.3f} m")
    else:
        print("Pose Estimation Failed.")

if __name__ == "__main__":
    test_pose()