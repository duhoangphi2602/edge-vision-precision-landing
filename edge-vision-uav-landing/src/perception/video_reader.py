import cv2

class VideoReader:
    def __init__(self, source=0, width=640, height=480):
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()