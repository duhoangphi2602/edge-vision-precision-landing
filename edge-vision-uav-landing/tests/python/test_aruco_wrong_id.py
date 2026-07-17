import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
import cv2
import numpy as np
import os

# Thêm đường dẫn src vào PYTHONPATH để import được module
from src.perception.aruco_detector import ArucoDetector

def main():
    print("=== BAT DAU BAI TEST NHAN DIEN ARUCO ===")
    
    # 1. Khởi tạo detector mục tiêu ID = 0 (theo Mission P1-A)
    detector = ArucoDetector(dict_type="DICT_4X4_50", target_id=0)
    
    # Lấy dictionary để tạo ảnh test
    try:
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    except AttributeError:
        aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        
    # 2. Tạo ảnh chứa ArUco ID 0 (Marker ĐÚNG)
    marker_id_0 = np.zeros((200, 200), dtype=np.uint8)
    try:
        marker_id_0 = cv2.aruco.generateImageMarker(aruco_dict, 0, 200, marker_id_0, 1)
    except AttributeError:
        marker_id_0 = cv2.aruco.drawMarker(aruco_dict, 0, 200, marker_id_0, 1)
        
    frame_correct = np.ones((480, 640, 3), dtype=np.uint8) * 255
    frame_correct[140:340, 220:420, :] = cv2.cvtColor(marker_id_0, cv2.COLOR_GRAY2BGR)

    # 3. Tạo ảnh chứa ArUco ID 1 (Marker SAI)
    marker_id_1 = np.zeros((200, 200), dtype=np.uint8)
    try:
        marker_id_1 = cv2.aruco.generateImageMarker(aruco_dict, 1, 200, marker_id_1, 1)
    except AttributeError:
        marker_id_1 = cv2.aruco.drawMarker(aruco_dict, 1, 200, marker_id_1, 1)
        
    frame_wrong = np.ones((480, 640, 3), dtype=np.uint8) * 255
    frame_wrong[140:340, 220:420, :] = cv2.cvtColor(marker_id_1, cv2.COLOR_GRAY2BGR)

    # 4. Đưa ảnh vào detector
    print("\n[TEST 1] Dua frame co chua Marker ID 0 vao...")
    found_0, corners_0, center_0 = detector.detect(frame_correct)
    if found_0:
        print(f"-> KET QUA: PASS. Nhan dien thanh cong! Tam cua Marker o pixel: {center_0}")
    else:
        print("-> KET QUA: FAIL. Khong tim thay Marker ID 0.")

    print("\n[TEST 2] Dua frame co chua Marker ID 1 vao (Wrong-ID)...")
    found_1, corners_1, center_1 = detector.detect(frame_wrong)
    if not found_1:
        print("-> KET QUA: PASS. He thong da loai bo thanh cong Marker ID 1.")
    else:
        print(f"-> KET QUA: FAIL. He thong nhan nham ID 1 la muc tieu!")

    print("\n=== KET THUC BAI TEST ===")

if __name__ == "__main__":
    main()
