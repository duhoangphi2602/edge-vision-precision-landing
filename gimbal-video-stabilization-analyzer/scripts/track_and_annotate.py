from ultralytics import YOLO
import argparse
import os
import cv2
import logging

logging.getLogger("ultralytics").setLevel(logging.WARNING)

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True, help='Path to input MP4')
parser.add_argument('--output', required=True, help='Path to output MP4')
parser.add_argument('--model', default='../edge-ai-training/models/optimized/yolo26s_640.onnx')
args = parser.parse_args()

model = YOLO(args.model, task='detect')
cap = cv2.VideoCapture(args.input)
fps = cap.get(cv2.CAP_PROP_FPS)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

print(f"Tracking {args.input} -> {args.output}...")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    results = model.track(frame, persist=True, conf=0.4, verbose=False)
    annotated_frame = results[0].plot()
    out.write(annotated_frame)
    
cap.release()
out.release()
print(f"Tracking completed: {args.output}")
