import sys
import os
import cv2
from pathlib import Path

# Thêm đường dẫn để import src
sys.path.append(str(Path(__file__).parent.parent))

from src.perception.replay_source import ReplaySource
from src.evaluation.fault_injection import FaultInjector

def main():
    # Giả định có 1 file video test (cần tải video thật vào thư mục videos/)
    video_path = "videos/test_landing.mp4" 
    
    # Tạo thư mục videos nếu chưa có và mock 1 video ngắn 1 giây bằng OpenCV
    os.makedirs("videos", exist_ok=True)
    if not os.path.exists(video_path):
        print("Đang tạo một video mock để test...")
        out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (640, 480))
        for i in range(30):
            frame = cv2.applyColorMap(cv2.convertScaleAbs(cv2.randn(np.zeros((480, 640), dtype=np.uint8), 128, 50)), cv2.COLORMAP_JET)
            out.write(frame)
        out.release()

    source = ReplaySource(video_path, playback_speed=1.0)
    injector = FaultInjector("configs/faults.yaml")
    
    # Mở file log CSV
    os.makedirs("logs", exist_ok=True)
    with open("logs/fault_injection_log.csv", "w") as f:
        f.write("timestamp_ns,frame_id,injected_fault,status\n")
        
        while True:
            ret, frame, timestamp = source.read_frame()
            if not ret:
                break
                
            faulty_frame, fault_type = injector.apply_faults(frame)
            
            if faulty_frame is None:
                # Frame bị drop
                f.write(f"{timestamp},{source.frame_id},{fault_type},dropped\n")
                continue
                
            f.write(f"{timestamp},{source.frame_id},{fault_type},processed\n")
            
            # Hiển thị trực quan (tùy chọn)
            cv2.imshow("Fault Injection Replay", faulty_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    source.release()
    cv2.destroyAllWindows()
    print("Hoàn tất Replay Test. Log đã được lưu tại logs/fault_injection_log.csv")

if __name__ == "__main__":
    import numpy as np
    main()