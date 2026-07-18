import cv2, os, glob, csv, sys
import imageio
try:
    from ultralytics import YOLO
except ImportError:
    sys.exit("ultralytics required")

def track_sequence(sequence_dir, output_csv, output_video):
    # Sử dụng model yolo26s custom đã được train và export ONNX từ các ngày trước
    model = YOLO('edge-vision-uav-landing/models/yolo26s_640_v1/model.onnx', task='detect')
    images = sorted(glob.glob(os.path.join(sequence_dir, "*.jpg")))
    
    writer = imageio.get_writer(output_video, fps=30, macro_block_size=1)
    
    with open(output_csv, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['frame', 'count', 'avg_conf'])
        for idx, img_path in enumerate(images):
            frame = cv2.imread(img_path)
            # Model custom chỉ có 4 class: car, van, truck, bus. Bắt toàn bộ các class này.
            results = model.predict(frame, verbose=False)
            
            count = 0
            avg_conf = 0.0
            if len(results) > 0 and len(results[0].boxes) > 0:
                boxes = results[0].boxes
                count = len(boxes)
                # Tính điểm trung bình của tất cả các xe bắt được
                avg_conf = sum(boxes.conf.tolist()) / count
                
            csv_writer.writerow([idx, count, round(avg_conf, 3)])
            
            # Draw bounding boxes and write to video
            annotated_frame = results[0].plot()
            annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            writer.append_data(annotated_frame_rgb)
            
    writer.close()

if __name__ == "__main__":
    base_dir = 'edge-ai-training/datasets/raw/visdrone/v2019_mot_val/VisDrone2019-MOT-val/sequences/uav0000137_00458_v'
    faults_dir = 'edge-ai-training/datasets/processed/derived_faults/sequences'
    
    # Tạo cấu trúc thư mục con cho gọn gàng
    metrics_dir = 'runs/Day_22_VisDrone/metrics'
    videos_dir = 'runs/Day_22_VisDrone/videos'
    os.makedirs(metrics_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)
    
    print("Tracking CLEAN sequence...")
    track_sequence(
        base_dir, 
        os.path.join(metrics_dir, 'clean_metrics.csv'), 
        os.path.join(videos_dir, 'clean_annotated.mp4')
    )
    
    for fault_folder in glob.glob(os.path.join(faults_dir, "uav0000137_00458_v_*")):
        fault_name = os.path.basename(fault_folder).replace("uav0000137_00458_v_", "")
        print(f"Tracking {fault_name.upper()} sequence...")
        track_sequence(
            fault_folder, 
            os.path.join(metrics_dir, f'{fault_name}_metrics.csv'),
            os.path.join(videos_dir, f'{fault_name}_annotated.mp4')
        )
