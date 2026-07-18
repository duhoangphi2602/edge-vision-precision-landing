import cv2
import yaml
import time
import argparse
import os
import csv
import numpy as np
from ultralytics import YOLO

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.utils.run_manager import add_standard_args, create_run_dir, save_run_metadata

class VehicleTracker:
    def __init__(self, config_path, model_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        print(f"Loading model {model_path}...")
        self.model = YOLO(model_path, task='detect')
        
        self.target_id = None
        self.tracking_state = "SEARCH" # SEARCH, LOCKED, LOST
        self.last_seen_time = 0
        self.lost_timeout = self.config.get('lost_timeout_ms', 500) / 1000.0
        self.conf_thresh = self.config.get('confidence_threshold', 0.25)
        self.detector_classes = self.config.get('detector_classes', ['car', 'bus', 'truck'])
        
    def process_frame(self, frame):
        h, w = frame.shape[:2]
        center_x, center_y = w / 2, h / 2
        
        start_infer = time.time()
        # Chạy YOLO tracking
        results = self.model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False, conf=self.conf_thresh)
        infer_latency_ms = (time.time() - start_infer) * 1000
        
        result = results[0]
        
        valid_detections = []
        if result.boxes is not None and result.boxes.id is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            ids = result.boxes.id.cpu().numpy().astype(int)
            confs = result.boxes.conf.cpu().numpy()
            cls_ids = result.boxes.cls.cpu().numpy().astype(int)
            
            for box, trk_id, conf, cls_id in zip(boxes, ids, confs, cls_ids):
                class_name = result.names[cls_id]
                # Filter classes
                if class_name in self.detector_classes:
                    cx = (box[0] + box[2]) / 2
                    cy = (box[1] + box[3]) / 2
                    dist = np.sqrt((cx - center_x)**2 + (cy - center_y)**2)
                    valid_detections.append({
                        'id': trk_id, 'box': box, 'conf': conf, 'class': class_name, 'dist': dist, 'cx': cx, 'cy': cy
                    })
        
        current_time = time.time()
        selected_det = None
        
        if self.tracking_state == "SEARCH" or self.tracking_state == "LOST":
            if valid_detections:
                # Target selection policy: nearest to center
                valid_detections.sort(key=lambda x: x['dist'])
                selected_det = valid_detections[0]
                self.target_id = selected_det['id']
                self.tracking_state = "LOCKED"
                self.last_seen_time = current_time
        
        elif self.tracking_state == "LOCKED":
            # Duy trì target id
            for det in valid_detections:
                if det['id'] == self.target_id:
                    selected_det = det
                    self.last_seen_time = current_time
                    break
            
            if selected_det is None:
                if (current_time - self.last_seen_time) > self.lost_timeout:
                    self.tracking_state = "LOST"
                    self.target_id = None
        
        # Visualize
        if selected_det:
            box = selected_det['box']
            cv2.rectangle(frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
            cv2.putText(frame, f"ID:{self.target_id} {selected_det['class']} {selected_det['conf']:.2f}", 
                        (int(box[0]), int(box[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        cv2.putText(frame, f"State: {self.tracking_state}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"Infer ms: {infer_latency_ms:.1f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        return frame, self.tracking_state, self.target_id, infer_latency_ms

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_standard_args(parser)
    parser.add_argument("--reference-bbox", type=str, help="Reference bbox to lock on, e.g. 0:50,100,250,233")
    args = parser.parse_args()
    
    out_dir, run_id = create_run_dir(args, "P2-A")
    
    # We load defaults for YOLO config and model
    config_path = "edge-vision-uav-landing/configs/tracker_config.yaml"
    model_path = "edge-vision-uav-landing/models/yolov8n.pt"
    if not os.path.exists(config_path):
        config_path = "edge-vision-uav-landing/configs/perception.yaml"
    
    tracker = VehicleTracker(config_path, model_path)
    cap = cv2.VideoCapture(args.input)
    
    if not cap.isOpened():
        print(f"Error opening video file {args.input}")
        exit(1)
        
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    out_video = os.path.join(out_dir, "tracking_output.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_video, fourcc, fps, (width, height))
    
    log_file = os.path.join(out_dir, "tracking_metrics.csv")
    csv_f = open(log_file, 'w', newline='')
    writer = csv.writer(csv_f)
    writer.writerow(["frame", "state", "target_id", "infer_latency_ms"])
    
    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        proc_frame, state, tid, latency = tracker.process_frame(frame)
        out.write(proc_frame)
        writer.writerow([frame_idx, state, tid, round(latency, 2)])
        
        frame_idx += 1
        
    cap.release()
    out.release()
    csv_f.close()
    
    save_run_metadata(out_dir, vars(args), tracker.config, "python3 " + " ".join(sys.argv))
    
    if args.export_viewable:
        view_copy = os.path.join(os.path.dirname(__file__), '../../../tools/video/create_viewable_copy.py')
        os.system(f"python3 {view_copy} --input {out_video} --export-viewable")
    
    print(f"Saved video to {out_video} and metrics to {log_file}")
