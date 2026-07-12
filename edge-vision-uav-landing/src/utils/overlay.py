import cv2

def draw_target_center(frame, center_x, center_y):
    """Vẽ tâm chuẩn của camera (nơi mong muốn target nằm vào)"""
    cv2.drawMarker(frame, (center_x, center_y), (0, 255, 0), cv2.MARKER_CROSS, 20, 2)
    return frame

def draw_detection_info(frame, corners, center, target_id, error_x, error_y):
    """Vẽ bounding box của marker, tâm marker và các thông số error"""
    if corners is not None:
        cv2.polylines(frame, [corners.astype(int)], True, (0, 255, 0), 2)
        cv2.circle(frame, (int(center[0]), int(center[1])), 5, (0, 0, 255), -1)
        
        info_text = f"ID: {target_id} | e_x: {error_x:.1f} e_y: {error_y:.1f}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    return frame