import cv2
import numpy as np

class PoseEstimator:
    def __init__(self, camera_matrix, dist_coeffs, marker_size=0.15):
        """
        marker_size: Kích thước cạnh của ArUco marker tính bằng mét (m). Mặc định 0.15m (15cm).
        """
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.marker_size = marker_size
        
        # Định nghĩa 4 góc của marker trong không gian 3D (Z=0 vì marker phẳng)
        # Thứ tự các góc: top-left, top-right, bottom-right, bottom-left
        half_size = self.marker_size / 2.0
        self.obj_points = np.array([
            [-half_size,  half_size, 0],
            [ half_size,  half_size, 0],
            [ half_size, -half_size, 0],
            [-half_size, -half_size, 0]
        ], dtype=np.float32)

    def estimate_pose(self, corners):
        """
        Dự đoán tvec (vị trí) và rvec (góc xoay) của marker.
        corners: Tọa độ 4 góc 2D nhận diện được từ ảnh (của 1 marker).
        """
        # solvePnP yêu cầu corner format phải đúng chuẩn
        img_points = np.array(corners, dtype=np.float32)
        success, rvec, tvec = cv2.solvePnP(
            self.obj_points, 
            img_points, 
            self.camera_matrix, 
            self.dist_coeffs,
            flags=cv2.SOLVEPNP_IPPE_SQUARE # Thuật toán tối ưu cho điểm phẳng hình vuông
        )
        return success, rvec, tvec
        
    def get_error_metric(self, tvec):
        """
        Lấy lỗi theo hệ tọa độ metric (mét) từ tvec.
        Trong hệ OpenCV: X là qua phải, Y là xuống dưới, Z là khoảng cách phía trước.
        """
        if tvec is None:
            return 0.0, 0.0, 0.0
        x_m = float(tvec[0][0])
        y_m = float(tvec[1][0])
        z_m = float(tvec[2][0])
        return x_m, y_m, z_m