import cv2
import numpy as np

class VisualFaultInjector:
    def add_gaussian_noise(self, frame, severity=1):
        noise = np.random.normal(0, 10 * severity, frame.shape).astype(np.uint8)
        return cv2.add(frame, noise)

    def add_motion_blur(self, frame, severity=1):
        size = severity * 2 + 1
        kernel = np.zeros((size, size))
        kernel[int((size-1)/2), :] = np.ones(size) / size
        return cv2.filter2D(frame, -1, kernel)

    def add_occlusion(self, frame, severity=1):
        out = frame.copy()
        h, w = frame.shape[:2]
        for _ in range(severity * 5):
            x, y = np.random.randint(0, w-20), np.random.randint(0, h-20)
            cv2.rectangle(out, (x, y), (x+20, y+20), (0,0,0), -1)
        return out
