import cv2, os, yaml, glob, numpy as np
import imageio

def apply_fault(frame, config):
    ftype = config.get('fault_type')
    if ftype == 'blur':
        k = config.get('kernel_size', 5)
        k = k if k % 2 == 1 else k + 1
        return cv2.GaussianBlur(frame, (k, k), 0)
    elif ftype == 'motion_blur':
        k = config.get('kernel_size', 15)
        kernel = np.zeros((k, k))
        kernel[int((k-1)/2), :] = np.ones(k) / k
        return cv2.filter2D(frame, -1, kernel)
    elif ftype == 'noise':
        noise = np.random.normal(0, config.get('noise_variance', 10), frame.shape).astype(np.int16)
        return np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    elif ftype in ['brightness', 'overexposure']:
        inv_gamma = 1.0 / config.get('gamma', 1.0)
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(frame, table)
    elif ftype == 'contrast_reduction':
        alpha = config.get('alpha', 0.5)
        return cv2.convertScaleAbs(frame, alpha=alpha, beta=128*(1-alpha))
    elif ftype == 'compression':
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.get('quality', 10)]
        result, encimg = cv2.imencode('.jpg', frame, encode_param)
        return cv2.imdecode(encimg, 1)
    elif ftype == 'resolution_degradation':
        h, w = frame.shape[:2]
        scale = config.get('scale', 0.5)
        small = cv2.resize(frame, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    elif ftype == 'occlusion':
        out = frame.copy()
        h, w = frame.shape[:2]
        b = config.get('block_size', 50)
        x = np.random.randint(0, w-b)
        y = np.random.randint(0, h-b)
        out[y:y+b, x:x+b] = 0
        return out
    return frame

def process_sequence(input_dir, seq_out_dir, vid_out_dir, config, fault_name):
    os.makedirs(seq_out_dir, exist_ok=True)
    os.makedirs(vid_out_dir, exist_ok=True)
    images = sorted(glob.glob(os.path.join(input_dir, "*.jpg")))
    np.random.seed(42)
    
    # Chuẩn bị writer để sinh viewable video
    video_path = os.path.join(vid_out_dir, f"{fault_name}_viewable.mp4")
    writer = imageio.get_writer(video_path, fps=30, macro_block_size=1)
    
    for img_path in images:
        frame = cv2.imread(img_path)
        if frame is None: continue
        frame = apply_fault(frame, config)
        
        # 1. Lưu bản tương thích (Image Sequence .jpg) cho Tracker YOLO
        cv2.imwrite(os.path.join(seq_out_dir, os.path.basename(img_path)), frame)
        
        # 2. Ghi thêm vào bản Viewable (.mp4) cho người dùng xem
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        writer.append_data(frame_rgb)
        
    writer.close()
    print(f"-> Saved sequence to {seq_out_dir}")
    print(f"-> Saved video to {video_path}")

if __name__ == "__main__":
    with open('configs/faults/visdrone_visual_faults.yaml', 'r') as f:
        configs = yaml.safe_load(f)['fault_suites']
    base_dir = 'edge-ai-training/datasets/raw/visdrone/v2019_mot_val/VisDrone2019-MOT-val/sequences/uav0000137_00458_v'
    
    # Tạo cấu trúc thư mục rõ ràng
    seq_base = 'edge-ai-training/datasets/processed/derived_faults/sequences'
    vid_base = 'edge-ai-training/datasets/processed/derived_faults/videos'
    os.makedirs(seq_base, exist_ok=True)
    os.makedirs(vid_base, exist_ok=True)
    
    # Biên dịch luôn video gốc (Clean) để dễ đối chiếu
    print("Generating CLEAN viewable video...")
    clean_writer = imageio.get_writer(os.path.join(vid_base, "clean_viewable.mp4"), fps=30, macro_block_size=1)
    for img in sorted(glob.glob(os.path.join(base_dir, "*.jpg"))):
        clean_writer.append_data(imageio.imread(img))
    clean_writer.close()
    
    # Chạy bơm lỗi cho 18 sequence
    for name, config in configs.items():
        print(f"\nGenerating {name}...")
        fault_name = name.replace('visdrone_', '')  # Lấy tên lỗi kèm mức độ (vd: blur_medium)
        process_sequence(
            base_dir, 
            os.path.join(seq_base, f"uav0000137_00458_v_{fault_name}"), 
            vid_base, 
            config,
            fault_name
        )
