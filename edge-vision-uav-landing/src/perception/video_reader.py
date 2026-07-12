import cv2

class VideoReader:
    def __init__(self, source=0, width=640, height=480):
        # Thêm cờ CAP_V4L2 để fix lỗi timeout trên Linux
        self.cap = cv2.VideoCapture(source, cv2.CAP_V4L2)
        # Ép camera xuất định dạng YUYV vì luồng MJPG đang bị nhiễu và vỡ ảnh (Corrupt JPEG data)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()