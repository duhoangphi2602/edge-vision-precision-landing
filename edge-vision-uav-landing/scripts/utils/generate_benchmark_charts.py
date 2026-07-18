import os
import pandas as pd
import matplotlib.pyplot as plt

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../reports/figures')
os.makedirs(output_dir, exist_ok=True)

def plot_preliminary_fps_latency():
    # Đây là dữ liệu Fallback (Placeholder) mô phỏng cấu trúc đánh giá model.
    # Khi hoàn tất Day 21/22, ta sẽ đọc từ file CSV thực tế.
    data = {
        'Model': ['YOLO26s (CPU)', 'YOLO26s (ONNX CPU)', 'YOLO26s (ONNX Edge)'],
        'FPS': [15.2, 28.5, 45.0],
        'Latency_ms': [65.0, 35.0, 22.0]
    }
    df = pd.DataFrame(data)
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx() # Tạo trục Y thứ 2
    
    # Cột FPS (Càng cao càng tốt)
    ax1.bar(df['Model'], df['FPS'], color='skyblue', width=0.4, label='FPS (Higher is better)')
    # Đường Latency (Càng thấp càng tốt)
    ax2.plot(df['Model'], df['Latency_ms'], color='red', marker='o', linewidth=2, label='Latency (ms) (Lower is better)')
    
    ax1.set_ylabel('Frames Per Second (FPS)')
    ax2.set_ylabel('End-to-End Latency (ms)')
    plt.title('Preliminary Benchmark: Latency vs FPS\n(Waiting for Day 22 True Data)')
    
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'preliminary_fps_latency.png'), dpi=300)
    plt.close()

def plot_failure_categories():
    # Mô phỏng Lock Rate (Tỉ lệ bám mục tiêu thành công) theo từng loại nhiễu
    data = {
        'Category': ['Motion Blur', 'Occlusion', 'Illumination', 'Scale Variation', 'Clean Baseline'],
        'Lock_Rate': [0.55, 0.45, 0.80, 0.85, 0.95]
    }
    df = pd.DataFrame(data)
    
    plt.figure(figsize=(10,6))
    bars = plt.bar(df['Category'], df['Lock_Rate'], color='coral')
    
    # Thêm ngưỡng an toàn
    plt.axhline(y=0.70, color='r', linestyle='--', label='Minimum Safe Threshold (70%)')
    
    plt.ylabel('Target Lock Rate (0.0 -> 1.0)')
    plt.title('Preliminary Robustness: Target Lock Rate under Faults\n(Protocol: VisDrone Synthetic Faults)')
    plt.ylim(0, 1.1)
    plt.legend()
    
    # Ghi chú % trên đầu cột
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f'{yval*100:.1f}%', ha='center', va='bottom')
        
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'preliminary_failure_categories.png'), dpi=300)
    plt.close()

if __name__ == "__main__":
    print("Generating fallback charts...")
    plot_preliminary_fps_latency()
    plot_failure_categories()
    print(f"-> Generated charts successfully at: {output_dir}/")
