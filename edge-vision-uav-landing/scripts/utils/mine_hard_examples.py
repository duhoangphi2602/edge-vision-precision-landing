import csv, os, glob, shutil

clean_csv = 'runs/Day_22_VisDrone/metrics/clean_metrics.csv'
fault_csvs = glob.glob('runs/Day_22_VisDrone/metrics/*_metrics.csv')
if clean_csv in fault_csvs:
    fault_csvs.remove(clean_csv)

hard_examples_dir = 'edge-ai-training/datasets/hard_examples'
os.makedirs(hard_examples_dir, exist_ok=True)

# Load clean baseline (Lưu count và avg_conf)
clean_data = {}
with open(clean_csv, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        clean_data[int(row['frame'])] = {
            'count': int(row['count']),
            'avg_conf': float(row['avg_conf'])
        }

mined_count = 0
for fault_csv in fault_csvs:
    fault_name = os.path.basename(fault_csv).replace('_metrics.csv', '')
    seq_dir = f'edge-ai-training/datasets/processed/derived_faults/sequences/uav0000137_00458_v_{fault_name}'
    
    with open(fault_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            frame = int(row['frame'])
            f_count = int(row['count'])
            f_conf = float(row['avg_conf'])
            
            c_count = clean_data[frame]['count']
            c_conf = clean_data[frame]['avg_conf']
            
            is_hard_example = False
            
            # Điều kiện 1: Rớt xe (Partial False Negative)
            if c_count > 0 and f_count < 0.8 * c_count:
                is_hard_example = True
                
            # Điều kiện 2: Nhìn gà hóa cuốc (False Positive)
            elif f_count > c_count + 2:
                is_hard_example = True
                
            # Điều kiện 3: Sụt giảm tự tin nghiêm trọng (Soft Negative)
            elif c_count > 0 and f_count > 0 and f_conf < c_conf - 0.2:
                is_hard_example = True
            
            if is_hard_example:
                src_img = os.path.join(seq_dir, f"{frame+1:07d}.jpg") # VisDrone format
                dst_img = os.path.join(hard_examples_dir, f"{fault_name}_{frame:07d}.jpg")
                if os.path.exists(src_img):
                    shutil.copy(src_img, dst_img)
                    mined_count += 1

print(f"Mining hoàn tất! Đã thu thập {mined_count} hard-examples đa chiều.")
