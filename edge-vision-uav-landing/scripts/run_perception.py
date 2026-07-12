import time
import yaml
import cv2
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.perception.video_reader import VideoReader
from src.perception.aruco_detector import ArucoDetector
from src.utils.overlay import draw_target_center, draw_detection_info

def main():
    # Load Config
    with open("configs/perception.yaml", "r") as f:
        config = yaml.safe_load(f)

    cam_cfg = config["camera"]
    target_cfg = config["target"]
    camera_center = (target_cfg["center_x"], target_cfg["center_y"])

    # Init Modules
    reader = VideoReader(source=cam_cfg["source"], width=cam_cfg["width"], height=cam_cfg["height"])
    detector = ArucoDetector(dict_type=target_cfg["aruco_dict"], target_id=target_cfg["target_id"])

    # Setup CSV Log (Ghi đè file baseline ngày 1)
    log_file = open("logs/perception_baseline.csv", "w")
    log_file.write("timestamp_ns,frame_id,detected,error_x,error_y,latency_ms\n")

    frame_id = 0
    print("Starting perception loop. Press 'q' to quit.")

    while True:
        start_time = time.time_ns()
        frame = reader.read_frame()
        if frame is None:
            break

        detected, corners, marker_center = detector.detect(frame)
        
        error_x, error_y = 0.0, 0.0
        if detected:
            error_x, error_y = detector.compute_error(marker_center, camera_center)
            frame = draw_detection_info(frame, corners, marker_center, target_cfg["target_id"], error_x, error_y)

        frame = draw_target_center(frame, camera_center[0], camera_center[1])
        
        # Tính latency và log dữ liệu
        latency_ms = (time.time_ns() - start_time) / 1e6
        log_file.write(f"{time.time_ns()},{frame_id},{detected},{error_x},{error_y},{latency_ms:.2f}\n")

        cv2.imshow("Edge Vision Perception", frame)
        frame_id += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    reader.release()
    cv2.destroyAllWindows()
    log_file.close()
    print("Perception loop stopped.")

if __name__ == "__main__":
    main()