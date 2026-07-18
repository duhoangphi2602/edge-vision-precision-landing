import csv
import os
import matplotlib.pyplot as plt

os.makedirs('../reports', exist_ok=True)

try:
    times = []
    dts = []
    with open('../logs/python_only_benchmark.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            times.append(float(row['timestamp']))
            dts.append(float(row['delta_t']))
    
    plt.figure(figsize=(10, 5))
    plt.plot(times, dts, label='Python-Only Control dt (s)', color='red', marker='o')
    plt.axhline(y=0.033, color='blue', linestyle='--', label='Hybrid C++ Target dt (0.033s)')
    plt.axhline(y=0.1, color='green', linestyle=':', label='Normal Perception dt (0.100s)')
    
    plt.title('Architecture Control Loop Jitter under 800ms Perception Stall')
    plt.xlabel('Timestamp (s)')
    plt.ylabel('Delta T (s)')
    plt.ylim(0, 1.0)
    plt.legend()
    plt.grid(True)
    plt.savefig('../reports/ab_architecture_benchmark.png')
    print("Plot saved to reports/ab_architecture_benchmark.png")
except Exception as e:
    print("Could not generate plot (make sure matplotlib is installed):", e)
