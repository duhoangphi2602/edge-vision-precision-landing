import cv2
import time

class ReplaySource:
    def __init__(self, video_path: str, playback_speed: float = 1.0):
        self.video_path = video_path
        self.playback_speed = playback_speed
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Không thể mở video: {video_path}")
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps <= 0:
            self.fps = 30.0 # Default fallback
            
        self.frame_delay = 1.0 / (self.fps * self.playback_speed)
        self.frame_id = 0

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return False, None, 0
            
        # Giả lập thời gian thực (playback speed)
        if self.playback_speed > 0:
            time.sleep(self.frame_delay)
            
        # Giả lập timestamp (nanoseconds)
        timestamp_ns = int(time.time() * 1e9)
        self.frame_id += 1
        return True, frame, timestamp_ns

    def release(self):
        self.cap.release()