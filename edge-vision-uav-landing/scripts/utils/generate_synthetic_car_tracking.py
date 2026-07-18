import cv2
import numpy as np
import csv
import urllib.request
import os

def generate():
    out_vid = "assets/videos/base/p1b_vehicle_tracking/synthetic_car_tracking.mp4"
    out_csv = "assets/videos/annotations/synthetic_car_tracking_target.csv"
    
    # Download a high quality car image that YOLO will definitely detect
    # Unsplash car image
    url = "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
    try:
        req = urllib.request.urlopen(url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        car_img_full = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except Exception as e:
        print("Failed to download car image", e)
        return
        
    # The image is 400x266. We'll resize it to be a bit smaller so it fits our 768x432 canvas well.
    car_img = cv2.resize(car_img_full, (200, 133))
    car_h, car_w = car_img.shape[:2]
    
    w, h = 768, 432
    fps = 12.5
    n_frames = 150
    
    out = cv2.VideoWriter(out_vid, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    
    # Create an asphalt-like background
    np.random.seed(42)
    bg_frame = np.random.randint(50, 100, (h, w, 3), dtype=np.uint8)
    bg_frame = cv2.GaussianBlur(bg_frame, (5, 5), 0)
    # Draw some "road lines" and "buildings"
    cv2.line(bg_frame, (w//2, 0), (w//2, h), (150, 150, 150), 10)
    cv2.rectangle(bg_frame, (100, 100), (200, 200), (40, 40, 40), -1)
    cv2.rectangle(bg_frame, (500, 300), (600, 400), (40, 40, 40), -1)
    
    start_x, start_y = 50, 100
    end_x, end_y = w - car_w - 50, h - car_h - 50
    
    with open(out_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["frame_id", "timestamp_sec", "target_present", "bbox_x1", "bbox_y1", "bbox_x2", "bbox_y2", "target_id", "annotation_source"])
        
        for i in range(n_frames):
            bg = bg_frame.copy()
            
            # Interpolate position
            t = i / max(1, n_frames - 1)
            cx = int(start_x + (end_x - start_x) * t)
            cy = int(start_y + (end_y - start_y) * t)
            
            # Paste car
            bg[cy:cy+car_h, cx:cx+car_w] = car_img
            
            out.write(bg)
            
            writer.writerow([
                i, 
                round(i/fps, 3), 
                "True", 
                cx, cy, cx+car_w, cy+car_h, 
                "synthetic_car_0", 
                "synthetic_generator"
            ])
            
    out.release()
    print(f"Generated {out_vid} with {n_frames} frames.")

if __name__ == "__main__":
    generate()
