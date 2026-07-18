# Hướng dẫn Import dữ liệu VisDrone-MOT thủ công

## 1. Yêu cầu tải (Dataset/Task)
Bộ dữ liệu cần tải: **VisDrone2019-MOT** (Multi-Object Tracking).
*Lý do: Bài toán Tracking của chúng ta yêu cầu đối tượng phải có danh tính (persistent target ID) được duy trì qua các frame, điều mà bản VID hay DET không có.*

## 2. Nguồn tải chính thức
- **Nguồn:** [VisDrone Official Website](https://github.com/VisDrone/VisDrone-Dataset)
- **Tình trạng:** Cần có tài khoản Baidu Pan hoặc link Google Drive (nếu có) được công bố trên trang chủ của họ.

## 3. Mức độ tải cần thiết (Smoke Subset)
Bạn **KHÔNG CẦN** phải tải toàn bộ dataset hàng chục GB.
Để đáp ứng bài test `SMOKE_VALIDATED`, bạn chỉ cần tải đúng **1 sequence** (ví dụ: `uav0000137_00458_v.mp4`) kèm theo file annotation tương ứng của sequence đó.

## 4. Cấu trúc thư mục yêu cầu
Sau khi tải, hãy đặt 2 file đó vào đúng đường dẫn sau trong dự án:

```text
edge-ai-training/datasets/raw/visdrone/
├── sequences/
│   └── uav0000137_00458_v.mp4
└── annotations/
    └── uav0000137_00458_v.txt
```

Cấu trúc file annotation VisDrone-MOT chuẩn là:
`<frame_index>,<target_id>,<bbox_left>,<bbox_top>,<bbox_width>,<bbox_height>,<score>,<object_category>,<truncation>,<occlusion>`

## 5. Lệnh thực thi Import (Import Command)
Sau khi đã đặt các file vào đúng chỗ, mở terminal và chạy lệnh sau (chế độ an toàn Dry-run trước để hệ thống không thay đổi file):

```bash
python3 scripts/data_prep/import_visdrone_sequence.py \
    --input edge-ai-training/datasets/raw/visdrone/sequences/uav0000137_00458_v.mp4 \
    --annotation edge-ai-training/datasets/raw/visdrone/annotations/uav0000137_00458_v.txt \
    --sequence-id uav0000137_00458_v \
    --output-dir edge-ai-training/datasets/processed \
    --dry-run \
    --overwrite false
```

Lệnh này sẽ tự động:
1. Parse và giữ đúng `target_id`, `class` (xe cộ).
2. Lựa chọn Target bám theo policy chuẩn xác.
3. Sinh ra Manifest và chép file CSV vào thư mục `processed`.
