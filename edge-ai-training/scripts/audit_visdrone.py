import os
import glob
from pathlib import Path
from ultralytics.utils.downloads import download
from collections import Counter
import yaml

def audit_dataset():
    print("Bắt đầu audit dataset VisDrone...")
    
    # 1. Định vị đường dẫn dataset theo ultralytics (thường lưu ở ~/.config/ultralytics/settings.yaml -> datasets_dir)
    # Tuy nhiên, an toàn nhất là đọc trực tiếp từ config
    try:
        from ultralytics import settings
        dataset_dir = Path(settings['datasets_dir']) / 'VisDrone'
    except Exception as e:
        dataset_dir = Path.home() / "Projects" / "datasets" / "VisDrone"
        
    print(f"Đường dẫn dataset mong đợi: {dataset_dir}")
    
    # Nếu chưa có thư mục, chúng ta không tải ở script này để tránh treo, 
    # mà sẽ tải bằng script hoặc lệnh riêng.
    if not dataset_dir.exists():
        print(f"[LỖI] Không tìm thấy dataset tại {dataset_dir}. Vui lòng chạy lệnh train bằng VisDrone.yaml trước để hệ thống tự tải.")
        return

    # 2. Quét số lượng ảnh và nhãn
    images_train = list((dataset_dir / "images" / "train").glob("*.jpg"))
    labels_train = list((dataset_dir / "labels" / "train").glob("*.txt"))
    
    print(f"\n--- THỐNG KÊ SỐ LƯỢNG (TRAIN) ---")
    print(f"Số lượng ảnh: {len(images_train)}")
    print(f"Số lượng file nhãn: {len(labels_train)}")
    
    # Check pairing
    img_stems = set([p.stem for p in images_train])
    lbl_stems = set([p.stem for p in labels_train])
    missing_labels = img_stems - lbl_stems
    missing_images = lbl_stems - img_stems
    print(f"Số ảnh không có nhãn: {len(missing_labels)}")
    print(f"Số nhãn không có ảnh: {len(missing_images)}")

    # 3. Phân tích nội dung nhãn (Class distribution & Invalid boxes)
    print(f"\n--- PHÂN TÍCH NHÃN (TRAIN) ---")
    class_counts = Counter()
    invalid_boxes = 0
    empty_labels = 0
    total_boxes = 0
    
    for lbl_path in labels_train:
        if os.path.getsize(lbl_path) == 0:
            empty_labels += 1
            continue
            
        with open(lbl_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 5:
                    cls_id = int(parts[0])
                    class_counts[cls_id] += 1
                    total_boxes += 1
                    
                    # Kiểm tra bounding box có hợp lệ không (giá trị chuẩn hóa phải nằm trong [0, 1])
                    try:
                        x, y, w, h = map(float, parts[1:5])
                        if x < 0 or y < 0 or w <= 0 or h <= 0 or x > 1 or y > 1 or w > 1 or h > 1:
                            invalid_boxes += 1
                    except ValueError:
                        invalid_boxes += 1

    print(f"Tổng số bounding boxes: {total_boxes}")
    print(f"Số file nhãn rỗng: {empty_labels}")
    print(f"Số bounding boxes không hợp lệ (ngoài phạm vi 0-1): {invalid_boxes}")
    
    print(f"\n--- PHÂN BỐ LỚP (CLASS DISTRIBUTION) ---")
    # Lấy tên class từ VisDrone.yaml
    classes = ['pedestrian', 'people', 'bicycle', 'car', 'van', 'truck', 'tricycle', 'awning-tricycle', 'bus', 'motor']
    for cls_id in sorted(class_counts.keys()):
        cls_name = classes[cls_id] if cls_id < len(classes) else f"Unknown({cls_id})"
        print(f"Lớp {cls_id} ({cls_name}): {class_counts[cls_id]} boxes")

    # 4. Ghi báo cáo ra file markdown
    report_path = Path("reports/dataset_audit_visdrone_v1.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Báo Cáo Audit Dataset VisDrone\n\n")
        f.write("## 1. Số lượng và Pairing\n")
        f.write(f"- Tổng số ảnh (train): {len(images_train)}\n")
        f.write(f"- Tổng số file nhãn (train): {len(labels_train)}\n")
        f.write(f"- Ảnh thiếu nhãn: {len(missing_labels)}\n")
        f.write(f"- Nhãn thiếu ảnh: {len(missing_images)}\n\n")
        f.write("## 2. Tính toàn vẹn của Bounding Boxes\n")
        f.write(f"- Tổng số boxes: {total_boxes}\n")
        f.write(f"- Số boxes không hợp lệ (out of bounds): {invalid_boxes}\n")
        f.write(f"- Số file nhãn rỗng: {empty_labels}\n\n")
        f.write("## 3. Phân bố các lớp (Class Distribution)\n")
        for cls_id in sorted(class_counts.keys()):
            cls_name = classes[cls_id] if cls_id < len(classes) else f"Unknown({cls_id})"
            f.write(f"- **{cls_name}**: {class_counts[cls_id]}\n")
            
    print(f"\nĐã ghi báo cáo vào {report_path}")

if __name__ == "__main__":
    audit_dataset()
