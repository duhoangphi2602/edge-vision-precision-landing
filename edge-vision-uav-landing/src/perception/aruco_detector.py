import cv2
import numpy as np

class ArucoDetector:
    def __init__(self, dict_type="DICT_4X4_50", target_id=0):
        self.target_id = target_id
        # Tương thích với các phiên bản OpenCV mới
        try:
            self.aruco_dict = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dict_type))
            self.parameters = cv2.aruco.DetectorParameters()
            self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        except AttributeError:
            # Fallback cho OpenCV cũ
            self.aruco_dict = cv2.aruco.Dictionary_get(getattr(cv2.aruco, dict_type))
            self.parameters = cv2.aruco.DetectorParameters_create()
            self.detector = None

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.detector:
            corners, ids, _ = self.detector.detectMarkers(gray)
        else:
            corners, ids, _ = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
          
        if ids is not None:
            for i in range(len(ids)):
                if ids[i][0] == self.target_id:
                    # Tính tâm của marker
                    c = corners[i][0]
                    center_x = (c[0][0] + c[2][0]) / 2.0
                    center_y = (c[0][1] + c[2][1]) / 2.0
                    return True, corners[i][0], (center_x, center_y)
          
        return False, None, None

    def compute_error(self, marker_center, camera_center):
        if marker_center is None:
            return 0.0, 0.0
        # e_x = x_target - x_center
        error_x = marker_center[0] - camera_center[0]
        error_y = marker_center[1] - camera_center[1]
        return error_x, error_y