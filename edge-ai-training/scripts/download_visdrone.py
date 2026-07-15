import yaml
from ultralytics.data.utils import check_det_dataset

def download_dataset():
    print("Bắt đầu tải và chuẩn bị dataset VisDrone...")
    print("Quá trình này sẽ mất vài phút tùy tốc độ mạng, vui lòng chờ...")
    # Lệnh này sẽ check xem VisDrone đã tải chưa, nếu chưa nó sẽ tự động tải và giải nén
    dataset_info = check_det_dataset("VisDrone.yaml")
    print(f"\nThành công! Dataset đã sẵn sàng tại: {dataset_info.get('path', 'unknown')}")

if __name__ == "__main__":
    download_dataset()
